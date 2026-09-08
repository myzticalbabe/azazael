# coding: utf-8
"""


__all__ = [
    "ALGO_DEFAULTS",
    "SB3Agent",
    "SB3AgentPool",
    "SUPPORTED_ALGOS",
]

SB3Agent — FreeThreadedAgent wrapping stable-baselines3 RL algorithms.

Provides a FreeThreadedAgent subclass that wraps SB3's PPO, DQN, and A2C
algorithms with automatic DataPipelineWorm integration for training data,
ModelVersioner for version tracking, and PAMS/MemoryBus for observability.

Features:
- train() — Train from LocalMemoryStore data via DataPipelineWorm
- predict() — Inference using trained model
- save() / load() — Model persistence
- Auto-register with ModelVersioner after training
- MemoryBus events for training progress
- SB3AgentPool for multi-agent parallel training

Usage:
    agent = SB3Agent(algo="PPO", policy="MlpPolicy")
    
    # Train from memory data
    result = agent.train(source="SystemZ", total_timesteps=1000)
    
    # Predict
    action, state = agent.predict(observation)
    
    # Persist
    agent.save("models/my_model")
    agent.load("models/my_model")
"""

import sys
import json
import time
import os
import subprocess
import threading
import numpy as np

from datetime import datetime
from pathlib import Path
from typing import Any

# -- Import CORE utilities ----------------------------------------------------
# Add parent dir (src/) to sys.path, NOT CORE/ directly, to avoid CORE/logging.py
# shadowing the stdlib logging module (required by gymnasium/sb3)
_azazael_src = str(Path(__file__).resolve().parent.parent)
if _azazael_src not in sys.path:
    sys.path.insert(0, _azazael_src)

from CORE.Agent import FreeThreadedAgent, AgentConfig, IS_FREE_THREADED

# -- SB3 with graceful fallback ----------------------------------------------
# NOTE: importing stable_baselines3 pulls in torch, whose C-extensions SEGFAULT
# free-threaded 3.14t at import time (even with -X gil=1). So on free-threaded
# Python with the GIL disabled, skip the import entirely — train() will route
# to the GIL subprocess fallback instead.
try:
    import sysconfig as _sysconfig
    _SKIP_SB3_IMPORT = (
        _sysconfig.get_config_var("Py_GIL_DISABLED") == 1
        and hasattr(sys, "_is_gil_enabled")
        and not sys._is_gil_enabled()
        and os.environ.get("AZAZAEL_GIL_ENFORCED") != "1"
    )
except Exception:
    _SKIP_SB3_IMPORT = False

if not _SKIP_SB3_IMPORT:
    try:
        from stable_baselines3 import PPO, DQN, A2C
        from stable_baselines3.common.base_class import BaseAlgorithm
        HAS_SB3 = True
    except ImportError:
        HAS_SB3 = False
        PPO = DQN = A2C = None
        BaseAlgorithm = object
else:
    HAS_SB3 = False
    PPO = DQN = A2C = None
    BaseAlgorithm = object

try:
    import gymnasium as gym
    HAS_GYM = True
except ImportError:
    HAS_GYM = False
    gym = None

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None
    torch = None

try:
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# -- DataPipelineWorm for training data --------------------------------------
try:
    from CORE.WORMS.expansion.learning import DataPipelineWorm
    HAS_PIPELINE = True
except ImportError:
    HAS_PIPELINE = False
    DataPipelineWorm = None

# -- ModelVersioner for version tracking -------------------------------------
try:
    from CORE.WORMS.expansion.learning import ModelVersioner
    HAS_VERSIONER = True
except ImportError:
    HAS_VERSIONER = False
    ModelVersioner = None

# -- MemoryBus for messaging -------------------------------------------------
try:
    HAS_MEMORYBUS = True
except ImportError:
    HAS_MEMORYBUS = False

# -- Agent registry ----------------------------------------------------------
try:
    from CORE.agent_registry import register_agent
except ImportError:
    def register_agent(**kw):
        return lambda cls: cls


# -- GIL-enforced fallback for free-threaded Python --------------------------

def _needs_gil_enforcement() -> bool:
    """True when running on free-threaded Python with the GIL disabled.

    SB3/torch C-extensions are known to segfault under 3.14t no-GIL, so
    deep training must run under a GIL-enabled interpreter.
    """
    try:
        import sysconfig
        return (sysconfig.get_config_var("Py_GIL_DISABLED") == 1
                and hasattr(sys, "_is_gil_enabled")
                and not sys._is_gil_enabled())
    except Exception:
        return False


def _find_gil_python() -> (str | None):
    """Locate a standard (GIL-enabled) Python interpreter.

    Prefers AZAZAEL_GIL_PYTHON env var, then the sibling standard build
    (python3.14t.exe implies python.exe next to it), then py -V:3.14.
    Returns None if no GIL interpreter can be found.
    """
    # 1. Explicit override
    cand = os.environ.get("AZAZAEL_GIL_PYTHON")
    if cand and os.path.isfile(cand):
        return cand

    # 2. Sibling standard build next to the free-threaded exe
    #    (.../python3.14t.exe -> .../python.exe)
    try:
        sib = Path(sys.executable).with_name("python.exe")
        if sib.is_file() and sib.resolve() != Path(sys.executable).resolve():
            return str(sib)
    except Exception:
        pass

    # 3. py launcher discovery (best-effort, non-fatal)
    try:
        proc = subprocess.run(
            ["py", "-V:3.14", "-c",
             "import sys; print(sys.executable)"],
            capture_output=True, text=True, timeout=15,
        )
        if proc.returncode == 0:
            p = proc.stdout.strip().splitlines()[-1].strip()
            if p and os.path.isfile(p):
                return p
    except Exception:
        pass
    return None


def _run_training_in_gil_subprocess(
    algo: str, policy: str, device: str, seed: int,
    source: (str | None), event_type: (str | None),
    total_timesteps: int, model_name: (str | None),
) -> dict:
    """Run SB3 training in a standard (GIL-enabled) Python subprocess.

    Used when the host process is free-threaded 3.14t, where SB3/torch
    segfault even with -X gil=1 (the t-build itself is unsafe to import
    these C-extensions). The subprocess uses a standard interpreter,
    trains, registers with ModelVersioner, and prints a JSON result.
    """
    gil_py = _find_gil_python()
    if gil_py is None:
        return {
            "error": "No GIL-enabled Python found for SB3 fallback "
                     "(set AZAZAEL_GIL_PYTHON)",
            "trained": False,
        }

    cmd = [
        gil_py, "-c", _GIL_SUBPROCESS_CODE,
        "--", algo, policy, device, str(seed),
        source or "", event_type or "", str(total_timesteps),
        model_name or "",
    ]
    env = dict(os.environ)
    env["AZAZAEL_GIL_ENFORCED"] = "1"  # guard against re-exec loops
    env["AZAZAEL_SRC"] = _azazael_src  # bootstrap sys.path for CORE import
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=1800, env=env,
        )
    except subprocess.TimeoutExpired:
        return {"error": "GIL subprocess training timed out (30 min)", "trained": False}
    except FileNotFoundError:
        return {"error": f"GIL interpreter not found: {gil_py}", "trained": False}

    # Parse the last JSON line of stdout (prints may precede it)
    payload = None
    for line in reversed((proc.stdout or "").strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                payload = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
    if payload is None:
        return {
            "error": f"GIL subprocess failed (rc={proc.returncode}): "
                     f"{(proc.stderr or proc.stdout or '')[-400:]}",
            "trained": False,
        }
    payload["via_gil_subprocess"] = True
    return payload


# Code executed inside the GIL-enforced subprocess. Reads argv after '--'.
_GIL_SUBPROCESS_CODE = r'''
import sys, json, os
_src = os.environ.get("AZAZAEL_SRC")
if _src and _src not in sys.path:
    sys.path.insert(0, _src)
sys.argv = sys.argv[sys.argv.index("--") + 1:]
algo, policy, device, seed = sys.argv[0], sys.argv[1], sys.argv[2], int(sys.argv[3])
source = sys.argv[4] or None
event_type = sys.argv[5] or None
total_timesteps = int(sys.argv[6])
model_name = sys.argv[7] or None
try:
    from CORE.sb3_agent import SB3Agent
    agent = SB3Agent(algo=algo, policy=policy, device=device, seed=seed)
    result = agent.train(source=source, event_type=event_type,
                         total_timesteps=total_timesteps,
                         model_name=model_name, register_model=True)
    result["gil_enforced"] = True
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"error": f"{type(e).__name__}: {e}", "trained": False,
                      "gil_enforced": True}))
'''


# -- Supported algorithms ----------------------------------------------------


# -- Supported algorithms ----------------------------------------------------

SUPPORTED_ALGOS = {
    "PPO": PPO,
    "DQN": DQN,
    "A2C": A2C,
}

ALGO_DEFAULTS = {
    "PPO": {
        "learning_rate": 3e-4,
        "n_steps": 2048,
        "batch_size": 64,
        "n_epochs": 10,
        "gamma": 0.99,
        "gae_lambda": 0.95,
        "clip_range": 0.2,
        "ent_coef": 0.0,
        "vf_coef": 0.5,
        "max_grad_norm": 0.5,
    },
    "DQN": {
        "learning_rate": 1e-4,
        "buffer_size": 50000,
        "learning_starts": 1000,
        "batch_size": 32,
        "tau": 1.0,
        "gamma": 0.99,
        "train_freq": 4,
        "target_update_interval": 1000,
    },
    "A2C": {
        "learning_rate": 7e-4,
        "n_steps": 5,
        "gamma": 0.99,
        "gae_lambda": 1.0,
        "ent_coef": 0.01,
        "vf_coef": 0.5,
        "max_grad_norm": 0.5,
    },
}


@register_agent(category="rl", priority=8, description="SB3-based RL agent wrapping PPO/DQN/A2C")
class SB3Agent(FreeThreadedAgent):
    """
    FreeThreadedAgent wrapping stable-baselines3 RL algorithms.

    Features:
    - train() from LocalMemoryStore data via DataPipelineWorm
    - predict() for inference
    - save() / load() for persistence
    - Auto ModelVersioner registration
    - MemoryBus event publishing
    - Gym environment auto-creation for training

    Usage:
        agent = SB3Agent(algo="PPO")
        result = agent.train(source="SystemZ", total_timesteps=1000)
        action, _ = agent.predict(observation)
        agent.save("models/my_model.zip")
    """

    VERSION = "1.0.0"

    def __init__(self, config: (AgentConfig | None) = None, algo: str = "PPO",
                 policy: str = "MlpPolicy", algo_kwargs: (dict | None) = None,
                 device: str = "auto", seed: (int | None) = None,
                 env_kwargs: (dict | None) = None):
        """
        Initialize SB3Agent.

        Args:
            config: AgentConfig for the base FreeThreadedAgent.
            algo: Algorithm name: "PPO", "DQN", or "A2C".
            policy: SB3 policy type: "MlpPolicy", "CnnPolicy", "MultiInputPolicy".
            algo_kwargs: Additional kwargs passed to the SB3 constructor.
            device: Torch device ("auto", "cpu", "cuda"). "auto" picks cuda if available.
            seed: Random seed for reproducibility.
            env_kwargs: Additional kwargs for the gym environment.
        """
        super().__init__(config or AgentConfig(
            agent_name=f"SB3-{algo}",
            pams_source="sb3_agent",
        ))

        self.algo_name = algo.upper() if HAS_SB3 else "PPO"
        self.policy = policy
        self.algo_kwargs = algo_kwargs or {}
        self.env_kwargs = env_kwargs or {}
        self.seed = seed or int(time.time())

        # Device selection
        if device == "auto" and HAS_TORCH:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device or "cpu"

        # SB3 model (lazy init)
        self._model: (BaseAlgorithm | None) = None
        self._env: (gym.Env | None) = None
        self._model_lock = threading.Lock()

        # DataPipelineWorm (lazy)
        self._pipeline: (DataPipelineWorm | None) = None

        # ModelVersioner (lazy)
        self._versioner: (ModelVersioner | None) = None

        # Training metadata
        self._training_history: list[dict] = []
        self._last_train_time: (float | None) = None
        self._total_timesteps_trained = 0

        # Define observation space for the default environment
        self._obs_dim = 4  # Default: 4-dim continuous (can be overridden)
        self._action_dim = 2  # Default: 2-dim discrete

        if not HAS_SB3:
            self.set_state("sb3_available", False)
            if self.config.log_level in ("debug", "warning"):
                print(f"[{self.agent_id}] WARNING: SB3 not installed. "
                      f"Install: pip install stable-baselines3")

    # -- Properties ----------------------------------------------------------

    @property
    def is_trained(self) -> bool:
        """Whether the model has been trained."""
        return self._model is not None

    @property
    def algo_class(self):
        """Get the SB3 algorithm class for the current algo_name."""
        if not HAS_SB3:
            return None
        return SUPPORTED_ALGOS.get(self.algo_name)

    # -- Public API ----------------------------------------------------------

    def train(self, source: (str | None) = None, event_type: (str | None) = None,
              total_timesteps: int = 10000, n_episodes: (int | None) = None,
              learning_rate: (float | None) = None, use_data_split: bool = True,
              max_age_days: int = 30, model_name: (str | None) = None,
              register_model: bool = True, **kwargs) -> dict[str, Any]:
        """
        Train the SB3 model using data from LocalMemoryStore.

        Uses DataPipelineWorm to extract training data, creates a gym
        environment from the extracted features, and trains the SB3 model.

        Args:
            source: Filter memories by source component.
            event_type: Filter by event type.
            total_timesteps: Total training timesteps for SB3.
            n_episodes: If set, overrides total_timesteps as episodes × max_steps.
            learning_rate: Override the default learning rate.
            use_data_split: If True, use train/val split from pipeline.
            max_age_days: Only include records newer than N days.
            model_name: Name for ModelVersioner registration.
            register_model: If True, auto-register with ModelVersioner.
            **kwargs: Additional kwargs passed to SB3 model.learn().

        Returns:
            dict with training stats.
        """
        # -- GIL enforcement fallback (checked FIRST — SB3 may not even be
        # importable here; on free-threaded 3.14t the torch import segfaults,
        # so HAS_SB3 is False and the fallback below is the only safe path) --
        if os.environ.get("AZAZAEL_GIL_ENFORCED") != "1" and (
                _needs_gil_enforcement() or not HAS_SB3):
            gil_py = _find_gil_python()
            if gil_py is not None:
                print(f"[SB3Agent] GIL-enforced fallback via {gil_py}", flush=True)
                return _run_training_in_gil_subprocess(
                    algo=self.algo_name, policy=self.policy, device=self.device,
                    seed=self.seed, source=source, event_type=event_type,
                    total_timesteps=(n_episodes * 200 if n_episodes else total_timesteps),
                    model_name=model_name,
                )

        if not HAS_SB3:
            return {"error": "stable-baselines3 not installed", "trained": False}

        start = time.perf_counter()

        # -- Step 1: Extract training data ------------------------------
        pipeline = self._get_pipeline()
        records = pipeline.extract_from_memory(
            source=source, event_type=event_type,
            limit=5000, max_age_days=max_age_days,
        )

        if not records:
            return {"error": f"No training data found for source={source}", "trained": False}

        # -- Step 2: Create environment --------------------------------
        try:
            env = self._create_env_from_records(records)
        except Exception as e:
            return {"error": f"Failed to create environment: {e}", "trained": False}

        # -- Step 3: Override params ----------------------------------
        params = dict(ALGO_DEFAULTS.get(self.algo_name, {}))
        if learning_rate is not None:
            params["learning_rate"] = learning_rate
        params.update(self.algo_kwargs)
        params.update(kwargs)

        # -- Step 4: Create or re-init model ---------------------------
        try:
            with self._model_lock:
                if self._model is None:
                    algo_cls = self.algo_class
                    if algo_cls is None:
                        return {"error": f"Unsupported algorithm: {self.algo_name}"}

                    self._model = algo_cls(
                        self.policy,
                        env,
                        verbose=0 if self.config.log_level != "debug" else 1,
                        device=self.device,
                        seed=self.seed,
                        **params,
                    )
                else:
                    self._model.set_env(env)

                # Train
                n = n_episodes * 200 if n_episodes else total_timesteps
                self._model.learn(total_timesteps=n, reset_num_timesteps=False)
                self._total_timesteps_trained += n

        except Exception as e:
            return {"error": f"Training failed: {e}", "trained": False}

        duration_ms = (time.perf_counter() - start) * 1000
        self._last_train_time = time.time()

        # -- Step 5: Record training stats -----------------------------
        train_result = {
            "algo": self.algo_name,
            "policy": self.policy,
            "total_timesteps": n,
            "records_used": len(records),
            "data_source": source or "all",
            "duration_ms": round(duration_ms, 2),
            "device": self.device,
            "learning_rate": params.get("learning_rate"),
            "total_timesteps_trained": self._total_timesteps_trained,
            "trained": True,
        }

        self._training_history.append(train_result)
        if len(self._training_history) > 50:
            self._training_history = self._training_history[-50:]

        # Record in PAMS
        if self._pams:
            self._pams.record_event(
                "sb3_training_complete",
                train_result,
                source=self.config.pams_source, severity="info",
            )

        # Publish on bus
        self._publish_bus_event(f"agent.{self.agent_id}.training_complete", train_result)

        # -- Step 6: Register with ModelVersioner ----------------------
        if register_model and HAS_VERSIONER:
            mname = model_name or f"SB3_{self.algo_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                versioner = self._get_versioner()
                versioner.register_model(
                    name=mname,
                    version=f"v{len(self._training_history)}",
                    metrics={
                        "total_timesteps": n,
                        "records_used": len(records),
                        "duration_ms": round(duration_ms, 2),
                    },
                    metadata={
                        "algo": self.algo_name,
                        "policy": self.policy,
                        "device": self.device,
                        "data_source": source or "all",
                    },
                )
                train_result["registered_model"] = mname
            except Exception as e:
                train_result["registry_error"] = str(e)

        return train_result

    def predict(self, observation: np.ndarray, deterministic: bool = True,
                state: Any = None) -> tuple[Any, Any]:
        """
        Predict an action from an observation.

        Args:
            observation: The environment observation.
            deterministic: Whether to use deterministic or stochastic policy.
            state: Optional recurrent state.

        Returns:
            (action, next_state) tuple.
        """
        if not HAS_SB3 or self._model is None:
            # Fallback: random action
            action = np.random.randint(0, self._action_dim)
            return action, None

        try:
            return self._model.predict(observation, deterministic=deterministic, state=state)
        except Exception:
            self._increment_stat('tasks_failed')
            return np.array([0]), None

    def predict_batch(self, observations: list[np.ndarray],
                      deterministic: bool = True) -> list[Any]:
        """Predict actions for a batch of observations."""
        return [self.predict(obs, deterministic=deterministic)[0] for obs in observations]

    def save(self, path: str | Path) -> bool:
        """
        Save the trained model to disk.

        Args:
            path: File path (without extension, .zip will be added).

        Returns:
            True if saved successfully.
        """
        if not HAS_SB3 or self._model is None:
            return False
        try:
            path = str(path)
            self._model.save(path)
            return True
        except Exception:
            return False

    def load(self, path: str | Path, env: Any = None) -> bool:
        """
        Load a trained model from disk.

        Args:
            path: File path (without extension).
            env: Optional environment to associate with the model.

        Returns:
            True if loaded successfully.
        """
        if not HAS_SB3:
            return False
        try:
            path = str(path)
            algo_cls = self.algo_class
            if algo_cls is None:
                return False
            with self._model_lock:
                self._model = algo_cls.load(path, env=env or self._env)
            return True
        except Exception:
            return False

    def get_training_history(self, limit: int = 10) -> list[dict]:
        """Get recent training history."""
        return self._training_history[-limit:]

    # -- Environment Creation ------------------------------------------------

    def _create_env_from_records(self, records: list[dict]) -> 'gym.Env':
        """
        Create a gym environment from LocalMemoryStore records.

        Transforms records into a simple vector environment where:
        - Observation: feature vector extracted from record data
        - Action: discrete action space (0 = info, 1 = warning, 2 = error)
        - Reward: based on record severity

        Handles variable-length feature vectors by padding shorter records
        with zeros to match the maximum feature dimension.
        """
        if not HAS_GYM:
            raise ImportError("gymnasium is required for environment creation")

        # Extract features from records
        features = []
        for r in records:
            data = r.get("data", {})
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    data = {}
            if not isinstance(data, dict):
                data = {}

            # Build observation vector
            obs = []
            # Severity ordinal
            sev_map = {"info": 0.0, "warning": 0.33, "error": 0.67, "critical": 1.0}
            obs.append(sev_map.get(r.get("severity", "info"), 0.0))

            # Numeric data fields (normalized)
            for val in data.values():
                if isinstance(val, (int, float)):
                    obs.append(min(max(float(val) / 100.0, 0.0), 1.0))
                elif isinstance(val, bool):
                    obs.append(1.0 if val else 0.0)

            if obs:
                features.append(obs)

        if not features:
            # Default observation space
            self._obs_dim = 4
            self._action_dim = 2
            return self._create_default_env()

        # Pad all feature vectors to the same length using a sentinel value
        # outside the normalized [0,1] range. The model learns to ignore -2.0
        # as a "missing feature" signal (P2-6: proper attention mask is future work).
        max_dim = max(len(f) for f in features)
        for f in features:
            if len(f) < max_dim:
                f.extend([-2.0] * (max_dim - len(f)))

        # Determine observation dimension
        self._obs_dim = max_dim
        self._action_dim = 3  # info, warning, error

        # Create environment
        return self._create_vector_env(features)

    def _create_vector_env(self, feature_vectors: list[list[float]]) -> 'gym.Env':
        """
        Create a simple vector-based gym environment.

        The environment cycles through the feature vectors, and the agent's
        goal is to predict the correct severity level for each observation.
        """
        import gymnasium as gym
        from gymnasium.spaces import Box, Discrete

        class _MemoryDatasetEnv(gym.Env):
            """Gym environment from LocalMemoryStore data."""

            def __init__(self, features: list[list[float]]):
                super().__init__()
                self.features = features
                self.n = len(features)
                self.idx = 0

                obs_dim = len(features[0]) if features else 4
                self.observation_space = Box(
                    low=-1.0, high=1.0,
                    shape=(obs_dim,),
                    dtype=np.float32,
                )
                self.action_space = Discrete(3)  # 0=improve, 1=maintain, 2=escalate

                # Infer expected action from feature vector
                # First feature is severity ordinal (0.0=info, 0.33=warning, 0.67=error, 1.0=critical)
                self._expected_actions = []
                for feat in features:
                    sev = feat[0] if feat else 0.0
                    if sev <= 0.33:  # info/warning -> maintain
                        self._expected_actions.append(1)  # maintain
                    elif sev <= 0.67:  # error -> escalate
                        self._expected_actions.append(2)  # escalate
                    else:  # critical -> escalate
                        self._expected_actions.append(2)  # escalate

            def reset(self, *, seed=None, options=None):
                super().reset(seed=seed)
                self.idx = np.random.randint(0, self.n) if self.n > 0 else 0
                obs = np.array(self.features[self.idx], dtype=np.float32)
                return obs, {}

            def step(self, action):
                # Reward: +1 for correct action, -0.5 for incorrect
                expected = self._expected_actions[self.idx]
                reward = 1.0 if action == expected else -0.5
                self.idx = (self.idx + 1) % self.n
                obs = np.array(self.features[self.idx], dtype=np.float32)
                done = self.idx == 0  # Episode ends when we cycle through all
                return obs, reward, done, False, {}

        return _MemoryDatasetEnv(feature_vectors)

    def _create_default_env(self) -> 'gym.Env':
        """Create a default simple environment when no data is available."""
        import gymnasium as gym
        from gymnasium.spaces import Box, Discrete

        class _DefaultEnv(gym.Env):
            """Simple default environment with 4-dim observation space."""

            def __init__(self):
                super().__init__()
                self.observation_space = Box(
                    low=-1.0, high=1.0, shape=(4,), dtype=np.float32
                )
                self.action_space = Discrete(2)
                self.t = 0

            def reset(self, *, seed=None, options=None):
                super().reset(seed=seed)
                self.t = 0
                return np.zeros(4, dtype=np.float32), {}

            def step(self, action):
                self.t += 1
                obs = np.random.randn(4).astype(np.float32) * 0.1
                reward = 1.0 if action == 0 else -0.1
                done = self.t >= 200
                return obs, reward, done, False, {}

        return _DefaultEnv()

    # -- Lazy helpers --------------------------------------------------------

    def _get_pipeline(self) -> DataPipelineWorm:
        """Lazy DataPipelineWorm for memory access."""
        if self._pipeline is None and HAS_PIPELINE:
            try:
                self._pipeline = DataPipelineWorm()
            except Exception:
                self._pipeline = False  # Sentinel
        return self._pipeline if self._pipeline else None

    def _get_versioner(self) -> (ModelVersioner | None):
        """Lazy ModelVersioner for version tracking."""
        if self._versioner is None and HAS_VERSIONER:
            try:
                self._versioner = ModelVersioner()
            except Exception:
                self._versioner = False
        return self._versioner if self._versioner else None

    # -- FreeThreadedAgent._run override -------------------------------------

    def _run(self, task: dict[str, Any], pool: Any = None) -> Any:
        """
        Override FreeThreadedAgent._run() to handle SB3 agent tasks.

        Supported task payloads:
        - {"action": "train", "source": "...", "total_timesteps": 1000}
        - {"action": "predict", "observation": [...]}
        - {"action": "save", "path": "models/model"}
        - {"action": "load", "path": "models/model"}
        - {"action": "get_training_history"}
        """
        action = task.get("action", "predict")
        payload = task.get("payload", task)

        if action == "train":
            return self.train(**payload)
        elif action == "predict":
            obs = np.array(payload.get("observation", payload.get("data", [])))
            action_out, state = self.predict(obs)
            return {"action": action_out.tolist() if hasattr(action_out, 'tolist') else action_out}
        elif action == "save":
            path = payload.get("path", "models/sb3_model")
            return {"saved": self.save(path)}
        elif action == "load":
            path = payload.get("path", "models/sb3_model")
            return {"loaded": self.load(path)}
        elif action == "get_training_history":
            return self.get_training_history()
        else:
            return {"error": f"Unknown action: {action}"}

    def __repr__(self) -> str:
        trained = "trained" if self.is_trained else "untrained"
        return (f"SB3Agent(id={self.agent_id}, algo={self.algo_name}, "
                f"policy={self.policy}, {trained}, "
                f"steps={self._total_timesteps_trained})")


# -- SB3AgentPool ------------------------------------------------------------

@register_agent(category="rl", priority=7, description="Multi-agent SB3 pool for parallel training and inference")
class SB3AgentPool(FreeThreadedAgent):
    """
    Pool of SB3Agent instances for parallel training and inference.

    Manages a pool of SB3Agent workers for distributed training runs
    or batch inference across multiple algorithms/configurations.

    Usage:
        pool = SB3AgentPool(n_agents=4)
        results = pool.train_parallel(source="SystemZ", total_timesteps=5000)
        predictions = pool.predict_parallel(observations)
    """

    VERSION = "1.0.0"

    def __init__(self, config: AgentConfig = None, n_agents: int = 4,
                 algo: str = "PPO", algo_kwargs: dict = None):
        super().__init__(config or AgentConfig(
            agent_name="SB3Pool",
            pams_source="sb3_pool",
        ))
        self.n_agents = n_agents
        self.algo = algo
        self.algo_kwargs = algo_kwargs or {}
        self._agents: list[SB3Agent] = []
        self._init_agents()

    def _init_agents(self) -> None:
        """Initialize the pool of SB3Agent workers."""
        for i in range(self.n_agents):
            agent = SB3Agent(
                config=AgentConfig(agent_name=f"SB3-Worker-{i}", pams_source="sb3_pool"),
                algo=self.algo,
                algo_kwargs=self.algo_kwargs,
                seed=int(time.time()) + i,
            )
            self._agents.append(agent)

    def train_parallel(self, source: (str | None) = None, event_type: (str | None) = None,
                       total_timesteps: int = 5000,
                       hyperparameter_grid: (list[dict] | None) = None) -> list[dict]:
        """
        Train agents in parallel with optional hyperparameter grid.

        Uses FreeThreadedAgent.execute_many() for true parallel training
        across all agents in the pool.

        Args:
            source: Filter memories by source.
            event_type: Filter by event type.
            total_timesteps: Timesteps per training run.
            hyperparameter_grid: list of param dicts, one per agent.
                If provided, each agent trains with different params.
                If None, all agents train with default params.

        Returns:
            list of training result dicts.
        """
        tasks = []
        for i, agent in enumerate(self._agents):
            kwargs = {}
            if hyperparameter_grid and i < len(hyperparameter_grid):
                kwargs = hyperparameter_grid[i]
            task_payload = {
                "source": source, "event_type": event_type,
                "total_timesteps": total_timesteps, "register_model": False,
                **kwargs
            }
            tasks.append({"action": "train", "payload": task_payload})

        # Run parallel via execute_many (uses FreeThreadPool internally)
        task_results = self.execute_many(tasks, task_type="parallel_train")

        results = []
        for tr in task_results:
            if tr.success and tr.result:
                results.append(tr.result)
            else:
                results.append({"error": tr.error or "Unknown error", "trained": False})
        return results

    def predict_parallel(self, observations: list[np.ndarray]) -> list[Any]:
        """Run batch inference across all agents."""
        predictions = []
        for agent in self._agents:
            preds = agent.predict_batch(observations)
            predictions.append(preds)
        return predictions

    def get_best_agent(self) -> (SB3Agent | None):
        """Get the agent with the most training experience."""
        if not self._agents:
            return None
        return max(self._agents, key=lambda a: a._total_timesteps_trained)

    def _run(self, task: dict[str, Any], pool: Any = None) -> Any:
        action = task.get("action", "train_parallel")
        payload = task.get("payload", task)

        if action == "train_parallel":
            return self.train_parallel(**payload)
        elif action == "predict_parallel":
            obs_list = [np.array(o) for o in payload.get("observations", [])]
            return self.predict_parallel(obs_list)
        elif action == "get_best_agent":
            best = self.get_best_agent()
            return {"best_agent_id": best.agent_id if best else None}
        else:
            return {"error": f"Unknown action: {action}"}


# -- Self-test -----------------------------------------------------------------

if __name__ == '__main__':
    print("=" * 60)
    print("  SB3Agent - Self-test")
    print("=" * 60)
    print(f"  SB3 available: {HAS_SB3}")
    print(f"  Gymnasium available: {HAS_GYM}")
    print(f"  Torch available: {HAS_TORCH}")
    print(f"  Pipeline available: {HAS_PIPELINE}")
    print(f"  Free-threaded: {IS_FREE_THREADED}")

    if not HAS_SB3:
        print("\n  [SKIP] SB3 not installed — install with: pip install stable-baselines3")
    else:
        # Test 1: Create SB3Agent
        agent = SB3Agent(algo="PPO")
        print(f"\n  [1] Agent created: {agent}")
        print(f"      Device: {agent.device}")

        # Test 2: Train from memory
        result = agent.train(source="SystemZ", total_timesteps=500, register_model=False)
        print("\n  [2] Training result:")
        for k, v in result.items():
            print(f"      {k}: {v}")

        # Test 3: Predict
        if agent.is_trained:
            obs = np.zeros(4, dtype=np.float32)
            action, state = agent.predict(obs)
            print(f"\n  [3] Prediction: action={action}")

        # Test 4: Training history
        history = agent.get_training_history()
        print(f"\n  [4] Training history: {len(history)} entries")

        # Test 5: AgentPool
        pool = SB3AgentPool(n_agents=2, algo="PPO")
        print(f"\n  [5] Pool created: {pool.n_agents} agents")

    print("\n" + "=" * 60)
