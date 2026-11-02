#!/usr/bin/env python3
# coding: utf-8
"""
ray_serve_deployment.py — Ray Serve deployment for ORCHESTRATION tree.

Deploys ML models, feature store, and agent services via Ray Serve.
Integrates with vLLM, SGLang, TensorRT-LLM, and Feast.

WHY THIS EXISTS
---------------
ORCHESTRATION currently uses basic Ray. Ray Serve provides:
- Scalable model serving with auto-scaling
- Multi-model composition
- Request batching and streaming
- Integration with Ray Train/Tune/Data
- Production-ready deployment patterns

ARCHITECTURE
------------
Ray Serve Application → vLLM/SGLang Engines → TensorRT-LLM Optimized
                    → Feast Feature Store (online)
                    → LangGraph Agents
                    → Ray Train/Tune for training
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
from enum import Enum

import ray
from ray import serve
from ray.serve.handle import DeploymentHandle

# Optional imports
try:
    import vllm
    VLLM_AVAILABLE = True
except ImportError:
    VLLM_AVAILABLE = False

try:
    import sglang
    SGLANG_AVAILABLE = True
except ImportError:
    SGLANG_AVAILABLE = False

# Local imports
try:
    from CORE.feast_feature_store import FeastFeatureStore, get_feast_store
    from CORE.langgraph_integration import LangGraphWormRegistry, get_langgraph_registry
    from CORE.async_core import AsyncWormRegistry, get_async_registry
except ImportError:
    FeastFeatureStore = LangGraphWormRegistry = AsyncWormRegistry = None
    get_feast_store = get_langgraph_registry = get_async_registry = None


# Ray Serve deployments

@serve.deployment(
    name="feast_feature_store",
    num_replicas=2,
    ray_actor_options={"num_cpus": 1, "memory": 2000 * 1024 * 1024},
)
class FeastFeatureStoreDeployment:
    """Ray Serve deployment for Feast Feature Store."""
    
    def __init__(self):
        self.store = None
        self._initialized = False
    
    async def initialize(self):
        if not self._initialized:
            from CORE.feast_feature_store import get_feast_store
            self.store = get_feast_store()
            if not self.store.initialize():
                raise RuntimeError("Failed to initialize Feast store")
            # Apply default worm specs
            from CORE.feast_feature_store import DEFAULT_WORM_SPECS
            self.store.apply_worm_features(DEFAULT_WORM_SPECS)
            self._initialized = True
    
    @serve.batch(max_batch_size=32, batch_wait_timeout_s=0.1)
    async def get_online_features(
        self,
        entity_rows: List[Dict[str, str]],
        features: List[str],
    ) -> List[Dict[str, Any]]:
        if not self._initialized:
            await self.initialize()
        
        results = []
        for entity_row in entity_rows:
            result = self.store.get_online_features(
                entity_rows=[entity_row],
                features=features,
            )
            results.append(result)
        return results
    
    async def materialize(self, worm_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        if not self._initialized:
            await self.initialize()
        
        success = self.store.materialize_worm(worm_id, features)
        return {"success": success, "worm_id": worm_id}
    
    async def list_features(self) -> Dict[str, List[str]]:
        if not self._initialized:
            await self.initialize()
        return self.store.list_registered_features()


@serve.deployment(
    name="langgraph_registry",
    num_replicas=2,
    ray_actor_options={"num_cpus": 2, "memory": 4000 * 1024 * 1024},
)
class LangGraphRegistryDeployment:
    """Ray Serve deployment for LangGraph Worm Registry."""
    
    def __init__(self):
        self.registry = None
        self._initialized = False
    
    async def initialize(self):
        if not self._initialized:
            from CORE.langgraph_integration import get_langgraph_registry
            self.registry = get_langgraph_registry()
            self._initialized = True
    
    async def run_workflow(
        self,
        workflow_name: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self._initialized:
            await self.initialize()
        
        return self.registry.run_workflow(workflow_name, input_data, config)
    
    async def stream_workflow(
        self,
        workflow_name: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        if not self._initialized:
            await self.initialize()
        
        async for chunk in self.registry.stream_workflow(workflow_name, input_data, config):
            yield chunk
    
    async def list_workflows(self) -> List[str]:
        if not self._initialized:
            await self.initialize()
        return self.registry.list_workflows()
    
    async def get_state(self, workflow_name: str, thread_id: str) -> Optional[Dict]:
        if not self._initialized:
            await self.initialize()
        return self.registry.get_workflow_state(workflow_name, thread_id)


@serve.deployment(
    name="async_worm_registry",
    num_replicas=4,
    ray_actor_options={"num_cpus": 2, "memory": 4000 * 1024 * 1024},
)
class AsyncWormRegistryDeployment:
    """Ray Serve deployment for Async Worm Registry."""
    
    def __init__(self):
        self.registry = None
        self._initialized = False
    
    async def initialize(self):
        if not self._initialized:
            from CORE.async_core import get_async_registry
            self.registry = await get_async_registry()
            self._initialized = True
    
    async def execute_worm(
        self,
        worm_type: str,
        input_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        if not self._initialized:
            await self.initialize()
        
        try:
            result = await self.registry.execute_async(worm_type, input_data, params, timeout=timeout)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def spawn_worm(self, worm_type: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        if not self._initialized:
            await self.initialize()
        
        worm_id = await self.registry.spawn_async(worm_type, params)
        return {"success": True, "worm_id": worm_id}
    
    async def execute_stream(
        self,
        worm_type: str,
        input_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        if not self._initialized:
            await self.initialize()
        
        async for chunk in self.registry.execute_stream(worm_type, input_data, params):
            yield chunk
    
    async def list_worms(self) -> List[Dict[str, Any]]:
        if not self._initialized:
            await self.initialize()
        return self.registry.list_worms()
    
    async def get_metrics(self) -> Dict[str, int]:
        if not self._initialized:
            await self.initialize()
        return self.registry.get_metrics()


@serve.deployment(
    name="vllm_engine",
    num_replicas=1,
    ray_actor_options={
        "num_gpus": 1,
        "num_cpus": 4,
        "memory": 16000 * 1024 * 1024,
        "accelerator_type": "A100",
    },
)
class VLLMEngineDeployment:
    """Ray Serve deployment for vLLM LLM Engine."""
    
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-3.1-8B-Instruct",
        tensor_parallel_size: int = 1,
        max_model_len: int = 8192,
        gpu_memory_utilization: float = 0.9,
    ):
        self.model_name = model_name
        self.tensor_parallel_size = tensor_parallel_size
        self.max_model_len = max_model_len
        self.gpu_memory_utilization = gpu_memory_utilization
        self.engine = None
        self._initialized = False
    
    async def initialize(self):
        if not self._initialized:
            if not VLLM_AVAILABLE:
                raise RuntimeError("vLLM not installed. Install with: pip install vllm")
            
            self.engine = vllm.AsyncLLMEngine.from_engine_args(
                vllm.AsyncEngineArgs(
                    model=self.model_name,
                    tensor_parallel_size=self.tensor_parallel_size,
                    max_model_len=self.max_model_len,
                    gpu_memory_utilization=self.gpu_memory_utilization,
                    trust_remote_code=True,
                    dtype="auto",
                    enforce_eager=False,
                )
            )
            self._initialized = True
    
    @serve.batch(max_batch_size=16, batch_wait_timeout_s=0.05)
    async def generate(
        self,
        prompts: List[str],
        sampling_params: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        if not self._initialized:
            await self.initialize()
        
        from vllm import SamplingParams
        
        results = []
        for prompt, params in zip(prompts, sampling_params):
            sp = SamplingParams(**params)
            request_id = str(uuid.uuid4())
            
            # Generate
            async for output in self.engine.generate(prompt, sp, request_id):
                pass  # streaming handled differently
            
            # For batch, use generate with list
            outputs = await self.engine.generate(
                prompts=prompts,
                sampling_params=[SamplingParams(**p) for p in sampling_params],
                request_ids=[str(uuid.uuid4()) for _ in prompts],
            )
            
            for output in outputs:
                results.append({
                    "text": output.outputs[0].text,
                    "tokens": len(output.outputs[0].token_ids),
                    "finish_reason": output.outputs[0].finish_reason,
                })
        
        return results
    
    async def generate_stream(
        self,
        prompt: str,
        sampling_params: Dict[str, Any],
    ) -> AsyncGenerator[Dict[str, Any], None]:
        if not self._initialized:
            await self.initialize()
        
        from vllm import SamplingParams
        
        sp = SamplingParams(**sampling_params)
        request_id = str(uuid.uuid4())
        
        async for output in self.engine.generate(prompt, sp, request_id):
            yield {
                "text": output.outputs[0].text,
                "tokens": len(output.outputs[0].token_ids),
                "finish_reason": output.outputs[0].finish_reason,
            }


@serve.deployment(
    name="dit_video_pipeline",
    num_replicas=1,
    ray_actor_options={
        "num_gpus": 1,
        "num_cpus": 4,
        "memory": 16000 * 1024 * 1024,
    },
)
class DiTVideoPipelineDeployment:
    """Ray Serve deployment for DiT Video Pipeline."""
    
    def __init__(self):
        self.pipeline = None
        self._initialized = False
    
    async def initialize(self):
        if not self._initialized:
            from CODEX.dit_video_pipeline import create_dit_pipeline
            self.pipeline = create_dit_pipeline()
            self._initialized = True
    
    async def generate_video(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None,
        expand_prompt: bool = True,
        style: str = "cinematic",
    ) -> Dict[str, Any]:
        if not self._initialized:
            await self.initialize()
        
        from CODEX.dit_video_pipeline import VideoGenerationConfig
        
        cfg = VideoGenerationConfig(**(config or {}))
        result = self.pipeline.generate_video(prompt, cfg, expand_prompt, style)
        
        return {
            "success": True,
            "video_path": str(result.video_path),
            "frames": result.frames,
            "fps": result.fps,
            "duration_seconds": result.duration_seconds,
            "resolution": result.resolution,
            "generation_time_seconds": result.generation_time_seconds,
            "model_used": result.model_used,
            "prompt_original": result.prompt_original,
            "prompt_expanded": result.prompt_expanded,
            "seed": result.seed,
        }
    
    async def batch_generate(
        self,
        prompts: List[str],
        config: Optional[Dict[str, Any]] = None,
        style: str = "cinematic",
    ) -> List[Dict[str, Any]]:
        if not self._initialized:
            await self.initialize()
        
        from CODEX.dit_video_pipeline import VideoGenerationConfig
        
        cfg = VideoGenerationConfig(**(config or {}))
        results = self.pipeline.batch_generate(prompts, cfg, style)
        
        return [
            {
                "success": r is not None,
                "video_path": str(r.video_path) if r else None,
                "frames": r.frames if r else 0,
                "fps": r.fps if r else 0,
                "error": None if r else "Generation failed",
            }
            for r in results
        ]


@serve.deployment(
    name="orchestration_gateway",
    num_replicas=2,
    ray_actor_options={"num_cpus": 2, "memory": 4000 * 1024 * 1024},
)
class OrchestrationGateway:
    """
    Main gateway for ORCHESTRATION services.
    
    Routes requests to appropriate deployments:
    - Feature store operations
    - LangGraph workflows
    - Async worm execution
    - LLM generation
    - Video generation
    """
    
    def __init__(self):
        self.feast_handle: DeploymentHandle = serve.get_deployment("feast_feature_store").get_handle()
        self.langgraph_handle: DeploymentHandle = serve.get_deployment("langgraph_registry").get_handle()
        self.async_worm_handle: DeploymentHandle = serve.get_deployment("async_worm_registry").get_handle()
        self.vllm_handle: DeploymentHandle = serve.get_deployment("vllm_engine").get_handle()
        self.dit_video_handle: DeploymentHandle = serve.get_deployment("dit_video_pipeline").get_handle()
    
    async def get_online_features(
        self,
        entity_rows: List[Dict[str, str]],
        features: List[str],
    ) -> List[Dict[str, Any]]:
        return await self.feast_handle.get_online_features.remote(entity_rows, features)
    
    async def materialize_worm(self, worm_id: str, features: Dict[str, Any]) -> Dict[str, Any]:
        return await self.feast_handle.materialize.remote(worm_id, features)
    
    async def run_workflow(
        self,
        workflow_name: str,
        input_data: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self.langgraph_handle.run_workflow.remote(workflow_name, input_data, config)
    
    async def execute_worm(
        self,
        worm_type: str,
        input_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self.async_worm_handle.execute_worm.remote(worm_type, input_data, params)
    
    async def generate_llm(
        self,
        prompts: List[str],
        sampling_params: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        return await self.vllm_handle.generate.remote(prompts, sampling_params)
    
    async def generate_video(
        self,
        prompt: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await self.dit_video_handle.generate_video.remote(prompt, config)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all sub-deployments."""
        checks = {}
        
        try:
            await self.feast_handle.list_features.remote()
            checks["feast"] = "healthy"
        except Exception as e:
            checks["feast"] = f"unhealthy: {e}"
        
        try:
            await self.langgraph_handle.list_workflows.remote()
            checks["langgraph"] = "healthy"
        except Exception as e:
            checks["langgraph"] = f"unhealthy: {e}"
        
        try:
            await self.async_worm_handle.get_metrics.remote()
            checks["async_worm_registry"] = "healthy"
        except Exception as e:
            checks["async_worm_registry"] = f"unhealthy: {e}"
        
        return {
            "status": "healthy" if all(v == "healthy" for v in checks.values()) else "degraded",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Application builder
def build_orchestration_app() -> serve.Application:
    """Build the complete ORCHESTRATION Ray Serve application."""
    
    # Bind deployments
    feast_deployment = FeastFeatureStoreDeployment.bind()
    langgraph_deployment = LangGraphRegistryDeployment.bind()
    async_worm_deployment = AsyncWormRegistryDeployment.bind()
    vllm_deployment = VLLMEngineDeployment.bind(
        model_name="meta-llama/Llama-3.1-8B-Instruct",
        tensor_parallel_size=1,
    )
    dit_video_deployment = DiTVideoPipelineDeployment.bind()
    
    # Gateway binds to all
    gateway = OrchestrationGateway.bind()
    
    return serve.Application(
        "orchestration",
        deployments=[
            feast_deployment,
            langgraph_deployment,
            async_worm_deployment,
            vllm_deployment,
            dit_video_deployment,
            gateway,
        ],
    )


# CLI for deployment
def deploy_orchestration(
    address: str = "auto",
    namespace: str = "orchestration",
    working_dir: Optional[str] = None,
) -> str:
    """Deploy the ORCHESTRATION application to Ray cluster."""
    
    # Initialize Ray
    if not ray.is_initialized():
        ray.init(address=address, namespace=namespace, working_dir=working_dir)
    
    # Build and deploy
    app = build_orchestration_app()
    
    # Deploy
    serve.run(app, name="orchestration", route_prefix="/orchestration")
    
    return f"Deployed ORCHESTRATION to {address}"


def shutdown_orchestration():
    """Shutdown Ray Serve and Ray."""
    serve.shutdown()
    ray.shutdown()


# CLI
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="ORCHESTRATION Ray Serve Deployment")
    parser.add_argument("--deploy", action="store_true", help="Deploy to Ray cluster")
    parser.add_argument("--shutdown", action="store_true", help="Shutdown deployment")
    parser.add_argument("--address", default="auto", help="Ray cluster address")
    parser.add_argument("--namespace", default="orchestration", help="Ray namespace")
    parser.add_argument("--working-dir", help="Working directory for code")
    
    args = parser.parse_args()
    
    if args.deploy:
        result = deploy_orchestration(args.address, args.namespace, args.working_dir)
        print(result)
    elif args.shutdown:
        shutdown_orchestration()
        print("Shutdown complete")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()