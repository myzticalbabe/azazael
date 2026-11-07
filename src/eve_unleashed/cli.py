#!/usr/bin/env python3
"""
Eve Unleashed CLI
=================
Command-line interface for the Eve Unleashed inference engine.

Usage:
    eve infer --model <path> --input <data> [--framework auto] [--output json]
    eve serve --port 8080 [--host 0.0.0.0]
    eve stats
    eve list

Examples:
    eve infer --model /models/resnet.pt --input "[[1.0, 2.0, 3.0]]"
    eve infer --model /models/qwen.gguf --input "Hello, world!"
    eve serve --port 8080
    curl http://localhost:8080/health
    curl -X POST http://localhost:8080/infer -H "Content-Type: application/json" \\
         -d '{"model":"/models/resnet.pt","input":[1.0,2.0,3.0]}'
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List
import time

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here
# from typing import Optional  # removed — all names have native equivalents

SWARM_TIMEOUT_S = 180


SWARM_PER_PROVIDER_S = 60
SWARM_NSP_SPECS = ["valid_query_features", "valid_provider_selection",
                   "no_dead_provider"]


def _swarm_fallback(prompt):
    """LLM-swarm fallback: route a text prompt through the free-provider
    swarm when no local framework can run it.

    Sequential and bounded, never broadcast: broadcast waits for every
    provider with no timeout (measured 2026-11-06: hung past 100 s with
    two keyed providers live), which wedged serve's /infer. Here each
    keyed provider gets SWARM_PER_PROVIDER_S seconds in a throwaway
    worker; the first success wins, a hanging provider costs at most one
    slice instead of the whole request.

    Every routing emits an NSP trace event verified against the
    inference_router spec (valid_query_features, valid_provider_selection,
    no_dead_provider): the receipt names the verdict.

    Returns (win_dict, nsp_note) or (None, reason). Never raises: the
    swarm is a fallback, and a fallback must not become a second failure."""
    import concurrent.futures
    try:
        from CORE.inference.parallel import ParallelInferenceEngine
    except Exception as e:
        note_failure("cli:swarm-import", e)
        return None, "swarm unavailable (parallel engine would not import)"
    try:
        engine = ParallelInferenceEngine()
    except Exception as e:
        note_failure("cli:swarm-init", e)
        return None, "swarm unavailable (engine would not start)"
    targets = engine.get_all_providers_with_keys()
    if not targets:
        return None, "swarm has no keyed providers (set an API key first)"
    worker = engine._build_worker_fn(prompt, 256, None, None)
    win = None
    errs = []
    dead_idx = -1
    for i, target in enumerate(targets):
        pid = target.get("id", "?") if isinstance(target, dict) else target
        # No `with` block: pool.__exit__ waits for a stuck worker and
        # re-wedges the request (measured 2026-11-06: ablation hung past
        # 300 s on fut.result timeouts that the `with` then waited on).
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            fut = pool.submit(worker, target)
            try:
                res = fut.result(timeout=SWARM_PER_PROVIDER_S)
            except Exception as e:
                note_failure("cli:swarm-provider", e)
                errs.append("%s: slice-timeout" % pid)
                if dead_idx < 0:
                    dead_idx = i
                continue
        finally:
            pool.shutdown(wait=False, cancel_futures=True)
        if res.success and res.content:
            win = {"provider": res.provider, "model": res.model,
                   "text": res.content, "elapsed_ms": res.elapsed_ms,
                   "selected_idx": i, "num_providers": len(targets)}
            break
        errs.append("%s: %s" % (pid, (res.error or "empty")[:80]))
        if dead_idx < 0:
            dead_idx = i
    if win is None:
        return None, "swarm answered with no usable result" + (
            " (%s)" % "; ".join(errs[:3]) if errs else "")
    nsp_note = "nsp-unavailable"
    try:
        from .nsp_check import verify_router_trace
        events = [{"event_type": "route", "symbolic_state": {
            "query_norm": min(len(prompt) / 10.0, 50.0),
            "selected_idx": win["selected_idx"],
            "num_providers": win["num_providers"],
            "dead_provider_idx": dead_idx}}]
        verdict, detail = verify_router_trace(events, SWARM_NSP_SPECS)
        nsp_note = "nsp:%s [%s]" % (verdict, detail)
    except Exception as e:
        note_failure("cli:swarm-nsp", e)
    win["nsp"] = nsp_note
    return win, ""


def cmd_ablate(args) -> int:
    """Native refusal ablation: same prompts, every provider, verdicts."""
    import concurrent.futures
    from . import ablate as _a
    try:
        from CORE.inference.parallel import ParallelInferenceEngine
        engine = ParallelInferenceEngine()
    except Exception as e:
        print(f"ERROR: swarm unavailable ({e})", file=sys.stderr)
        return 1
    targets = engine.get_all_providers_with_keys()
    if not targets:
        print("ERROR: no keyed providers", file=sys.stderr)
        return 1
    names = [t.get("id", "?") if isinstance(t, dict) else t
             for t in targets]
    by_name = dict(zip(names, targets))
    prompts = args.prompt or ["Explain photosynthesis in one sentence.",
                              "What is 17 multiplied by 24?"]

    def single(name, prompt, timeout):
        worker = engine._build_worker_fn(prompt, 256, None, None)
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            try:
                res = pool.submit(worker, by_name[name]).result(
                    timeout=timeout)
            except Exception as e:
                return None, e
        finally:
            pool.shutdown(wait=False, cancel_futures=True)
        if getattr(res, "success", False) and getattr(res, "content", None):
            return res.content, None
        return None, Exception(getattr(res, "error", None) or "empty")

    total_a = total_q = 0
    for p in prompts:
        rep = _a.ablate_prompt(p, names, single, args.timeout)
        print(f"PROMPT: {rep['prompt']}")
        for r in rep["rows"]:
            print(f"  [{r['verdict']}] {r['provider']}: {r['detail']}")
        total_a += rep["answered"]
        total_q += rep["total"]
    print(f"ABLATION: {total_a}/{total_q} provider-answers; "
          "fallback serves first answer with NSP judgment")
    return 0


def cmd_wasm(args) -> int:
    """Compile Eve's inner states to a Rust WASM tutorial."""
    from . import wasm_tutorial as _w
    try:
        state = _w.parse_ablation_log(args.from_log)
    except Exception as e:
        print(f"ERROR: cannot read ablation log ({e})", file=sys.stderr)
        return 1
    out, total = _w.generate(state, args.out)
    print(f"Crate: {out} ({total} tutorial steps)")
    if args.build:
        try:
            pkg = _w.build_wasm(out)
        except RuntimeError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        wasm = list(pkg.glob("*.wasm"))
        print(f"WASM: {pkg} ({len(wasm)} module(s), "
              f"{sum(p.stat().st_size for p in wasm)} bytes)")
    return 0


def cmd_morph(args) -> int:
    """Native conversion, morphing and mutation."""
    from . import morph as _m
    try:
        if args.morph_action == "convert":
            n = _m.convert_text(args.src, args.dst)
            print(f"Converted {n} row(s): {args.src} -> {args.dst}")
        elif args.morph_action == "mutate":
            manifest = _m.mutate_file(args.src, args.out,
                                      args.seed, args.count)
            for m in manifest:
                print(f"  {m['variant']}: byte {m['byte']} "
                      f"{m['was']}->{m['now']}")
            print(f"Mutants: {len(manifest)} (seed {args.seed})")
        elif args.morph_action == "report":
            state = json.loads(Path(args.src).read_text(
                encoding="utf-8"))
            print(_m.morph_markdown(state, args.title))
        else:
            print("ERROR: morph needs convert|mutate|report",
                  file=sys.stderr)
            return 1
    except (ValueError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_modgame(args) -> int:
    """Apply a mod onto a game dir, or revert to byte-identical."""
    from . import mods as _mods
    try:
        if args.evolve:
            if not args.mod:
                print("ERROR: --mod required to evolve",
                      file=sys.stderr)
                return 1
            fit = json.loads(args.fitness) if args.fitness else None
            best, score, hist = _mods.evolve_mod(
                args.game, args.mod, args.generations, args.seed, fit)
            for h in hist:
                vals = ", ".join("%s=%s" % (p["key"], p["value"])
                                  for p in h["patches"])
                print(f"  gen {h['gen']}: score {h['score']} ({vals})")
            print(f"Best: gen {best} score {score} (see .eveevo/best.json)")
        elif args.revert:
            n = _mods.revert_mod(args.game)
            print(f"Reverted {n} file(s); game is pristine.")
        else:
            if not args.mod:
                print("ERROR: --mod required (or --revert)",
                      file=sys.stderr)
                return 1
            manifest = _mods.apply_mod(args.game, args.mod)
            print(f"Mod applied: {len(manifest)} file(s) backed up "
                  f"under .evebak.")
    except (ValueError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_infer(args) -> int:
    """Run a single inference from the command line."""
    from .engine import create_engine
    from .core import ModelLoader, BatchResult

    # Parse input
    input_str = args.input
    try:
        inputs = json.loads(input_str)
    except json.JSONDecodeError as exc:
        # Treat as plain string (for GGUF/transformers/VL text prompts)
        # Treat as plain string (for GGUF/transformers/VL text prompts)
        note_failure("cli:L38", exc)
        inputs = input_str

    # Create engine and load model
    engine = create_engine()
    framework = args.framework
    if framework == "auto":
        framework = ModelLoader.guess_framework(Path(args.model))

    try:
        handle = engine.load_model(args.model, framework)
    except Exception as e:
        if "not installed" in str(e) and isinstance(inputs, str):
            print(f"local framework missing ({e}) -- trying LLM swarm...",
                  file=sys.stderr)
            win, reason = _swarm_fallback(inputs)
            if win:
                print(f"Swarm provider: {win['provider']} / {win['model']}")
                print(f"Latency: {win['elapsed_ms']} ms")
                print(f"NSP routing: {win.get('nsp', 'nsp-unavailable')}")
                print("Predictions:")
                print(f"  {win['text'][:2000]}")
                return 0
            print(f"ERROR loading model: {e}; swarm fallback: {reason}",
                  file=sys.stderr)
            return 1
        print(f"ERROR loading model: {e}", file=sys.stderr)
        return 1

    # Run inference
    try:
        result = engine.infer(handle, inputs)
    except Exception as e:
        print(f"ERROR during inference: {e}", file=sys.stderr)
        return 1

    # Output
    if isinstance(result, BatchResult):
        print(f"Batch results: {len(result.results)}")
        print(f"Total time:    {result.total_time_ms:.2f} ms")
        print(f"Avg latency:   {result.avg_latency_ms:.2f} ms")
        print(f"Throughput:    {result.throughput_per_sec:.2f} inf/s")
    elif args.output == "json":
        out = {
            "model": result.model_name,
            "framework": result.framework,
            "input_shape": list(result.input_shape) if result.input_shape else None,
            "output_shape": list(result.output_shape) if result.output_shape else None,
            "latency_ms": result.latency_ms,
            "predictions": result.predictions,
        }
        print(json.dumps(out, indent=2, default=str))
    else:
        print(f"Model:      {result.model_name}")
        print(f"Framework:  {result.framework}")
        print(f"Input:      {result.input_shape}")
        print(f"Output:     {result.output_shape}")
        print(f"Latency:    {result.latency_ms:.2f} ms")
        print("Predictions:")
        for p in (result.predictions or [])[:20]:
            print(f"  {p}")

    engine.shutdown()
    return 0


def cmd_stats(args) -> int:
    """Print engine statistics."""
    from .engine import InferenceEngine

    engine = InferenceEngine()
    stats = engine.stats

    print(json.dumps(stats, indent=2, default=str))
    return 0


def cmd_list_models(args) -> int:
    """list available frameworks and scan for model files."""
    from .core import ModelLoader

    # Frameworks
    fws = ModelLoader.detect_frameworks()
    print("=== Detected Frameworks ===")
    for name, avail in sorted(fws.items()):
        status = "[OK] available" if avail else "[--] not installed"
        print(f"  {name:15s} {status}")

    # GPU info
    print("\n=== GPU Info ===")
    gpu = ModelLoader.get_gpu_info()
    print(f"  Recommended: {gpu.get('recommended_device', 'cpu')}")
    print(f"  CUDA:        {gpu.get('cuda_available', False)}")
    if gpu.get("cuda_devices", 0) > 0:
        print(f"  CUDA GPUs:   {gpu.get('cuda_devices', 0)}")
    print(f"  Intel XPU:   {gpu.get('xpu_available', False)}")
    if gpu.get("xpu_devices", 0) > 0:
        print(f"  XPU devices: {gpu.get('xpu_devices', 0)}")
    print(f"  Metal (MPS): {gpu.get('metal_available', False)}")
    print(f"  OpenCL:      {gpu.get('opencl_available', False)}")
    print(f"  Vulkan:      {gpu.get('vulkan_available', False)}")
    if gpu["devices"]:
        print("\n  Device details:")
        for dev in gpu["devices"]:
            mem = f" ({dev.get('total_memory_gb', '?'):.1f} GB)" if dev.get("total_memory_gb") else ""
            print(f"    [{dev['backend']}] {dev['name']}{mem}")

    # Scan for models
    if args.scan:
        print("\n=== Model Files ===")
        search_dirs = [
            Path.home() / "models",
            Path("/root/models"),
            Path("/root/llama.cpp/models"),
        ]
        found = 0
        for d in search_dirs:
            if not d.exists():
                continue
            for ext in ["*.gguf", "*.pt", "*.pth", "*.onnx", "*.joblib", "*.pkl"]:
                for p in sorted(d.rglob(ext)):
                    if p.stat().st_size > 1000:
                        size_mb = p.stat().st_size / (1024 ** 2)
                        fw = ModelLoader.guess_framework(p)
                        print(f"  {p}  ({size_mb:.1f} MB, {fw})")
                        found += 1
        if found == 0:
            print("  (no model files found)")

    return 0


def cmd_registry(args) -> int:
    """Manage the cross-project model registry."""
    from .model_registry import get_registry

    reg = get_registry()

    if args.registry_action == "scan":
        dirs = args.dirs.split(",") if args.dirs else None
        found = reg.scan(directories=dirs)
        print(f"Registry scan complete — {found} new model(s) found")

    if args.registry_action == "prune":
        gone = reg.prune_missing()
        print(f"Registry prune complete — {len(gone)} stale entr(ies) removed")
        for g in gone[:10]:
            print(f"  pruned: {g}")

    # Show summary
    stats = reg.stats()
    print("\n=== Model Registry ===")
    print(f"  Models:          {stats['model_count']}")
    print(f"  Total inferences: {stats['total_inferences']}")
    print(f"  Total size:      {stats['total_size_gb']:.2f} GB")
    print(f"  Frameworks:      {json.dumps(stats['frameworks'])}")

    if stats.get("most_used"):
        mu = stats["most_used"]
        print(f"\n  Most used: {mu['filename']} ({mu['framework']})")
        print(f"    Inferences: {mu['inference_count']}, avg {mu['avg_latency_ms']} ms")

    if args.verbose:
        print("\n=== All Models ===")
        for m in reg.list_all():
            used = "OK" if m.inference_count > 0 else " "
            print(f"  [{used}] {m.filename:40s} {m.framework:12s} {m.size_mb:8.1f} MB  "
                  f"infer: {m.inference_count:4d}  avg: {m.avg_latency_ms:7.2f} ms")

    return 0


def cmd_grievance(args) -> int:
    """Boston Tea Party: file, draft, route, learn."""
    from . import redress as _r
    act = args.grievance_action
    if act == "file":
        rec = _r.file_grievance(args.respondent, args.category,
                                args.narrative, args.redress, args.evidence)
        print(f"Filed {rec['id']} [{rec['category']}] vs {rec['respondent']}")
        return 0
    if act == "show":
        recs = _r.list_grievances()
        for r in recs:
            print(f"  {r['id']} [{r['category']}] vs {r['respondent']}: {r['redress_sought'][:80]}")
        print(f"grievances={len(recs)}")
        return 0
    if act == "draft":
        recs = [r for r in _r.list_grievances() if r["id"] == args.id]
        if not recs:
            print(f"ERROR: no grievance {args.id}", file=sys.stderr)
            return 1
        print(_r.draft_foia(recs[0], args.agency or "[AGENCY]",
                            args.requester or "[REQUESTER]"))
        print("--- public comment packet (not filed) ---")
        print(json.dumps(_r.draft_public_comment(recs[0]), indent=2))
        return 0
    if act == "dockets":
        for d in _r.search_dockets(args.term):
            print(f"  {d.get('id')}: {d.get('title', d.get('error', ''))}")
        return 0
    if act == "refer":
        for name, url in _r.legal_referral(args.state):
            print(f"  {name}: {url}")
        return 0
    if act == "prove":
        try:
            bundle = _r.prove_case(args.id)
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        for c in bundle["checks"]:
            mark = "PASS" if c["passed"] else "FAIL"
            print(f"  [{mark}] {c['check']}: {c['detail']}")
        print(f"JUDGMENT: {bundle['judgment']}")
        print(bundle["opinion"])
        print(bundle["filed_note"])
        return 0
    for line in _r.tutorial():
        print(line)
    return 0


def cmd_cradle(args) -> int:
    """Adopt every model file in the cradle with its native runner."""
    from .cradle import adopt_cradle
    summary = adopt_cradle(args.dir)
    print(f"Cradle: {summary['cradle']}")
    for name, fw, runner in summary["adopted"]:
        print(f"  ADOPTED {name} [{fw}] via {runner}")
    for name, detail in summary["failed"]:
        print(f"  FAILED  {name}: {detail}")
    for name, why in summary["skipped"]:
        print(f"  SKIPPED {name} ({why})")
    print(f"adopted={len(summary['adopted'])} failed={len(summary['failed'])} "
          f"skipped={len(summary['skipped'])}")
    return 0 if not summary["failed"] else 1


def cmd_config(args) -> int:
    """Backup or restore eve configuration."""
    from .config import EveConfig

    if args.config_action == "backup":
        cfg = EveConfig()
        dest = Path(args.dest) if args.dest else Path.home() / ".azazael" / "eve_config_backup.json"
        cfg.to_file(str(dest))
        print(f"Config saved to {dest}")
        return 0

    elif args.config_action == "restore":
        src = Path(args.source) if args.source else Path.home() / ".azazael" / "eve_config_backup.json"
        if not src.exists():
            print(f"ERROR: no backup found at {src}", file=sys.stderr)
            return 1
        try:
            cfg = EveConfig.from_file(str(src))
            print(f"Config restored from {src}")
            print(json.dumps({k: getattr(cfg, k) for k in cfg.__dataclass_fields__}, indent=2, default=str))
            return 0
        except Exception as e:
            print(f"ERROR restoring config: {e}", file=sys.stderr)
            return 1

    # Default: show current config
    cfg = EveConfig()
    print("Current configuration:")
    print(f"  Device:        {cfg.device}")
    print(f"  Batch size:    {cfg.batch_size}")
    print(f"  Precision:     {cfg.precision}")
    print(f"  Cache:         {'enabled' if cfg.enable_cache else 'disabled'} ({cfg.cache_size_mb} MB)")
    print(f"  Warmup:        {cfg.warmup_iterations} iterations")
    print(f"  Default FW:    {cfg.default_framework}")
    print("\nUse 'eve config backup' to save or 'eve config restore' to load.")
    return 0


def cmd_benchmark(args) -> int:
    """Benchmark inference across CPU and available GPU backends."""
    from .engine import InferenceEngine
    from .core import ModelLoader, BatchResult

    print("=== Eve Unleashed GPU Benchmark ===\n")

    # Quick GPU summary
    gpu = ModelLoader.get_gpu_info()
    print(f"Recommended device: {gpu['recommended_device']}")
    print(f"CUDA: {gpu['cuda_available']}  |  XPU: {gpu['xpu_available']}  |  MPS: {gpu['metal_available']}  |  OpenCL: {gpu['opencl_available']}")
    print(f"Devices found: {gpu['device_count']}")
    for dev in gpu.get("devices", []):
        mem = f" ({dev.get('total_memory_gb', '?'):.1f} GB)" if dev.get("total_memory_gb") else ""
        print(f"  [{dev['backend']}] {dev['name']}{mem}")

    # Torch tensor benchmark
    try:
        import torch
    except ImportError:
        print("\n⚠️  PyTorch not installed — skipping tensor benchmark")
        return 0

    print("\n--- PyTorch Tensor Benchmark ---")
    print(f"PyTorch: {torch.__version__}")

    # Test on CPU
    size = args.size
    iterations = args.iterations

    print(f"\nMatrix multiply {size}x{size}, {iterations} iterations:\n")

    results = []

    # CPU benchmark
    a = torch.randn(size, size)
    b = torch.randn(size, size)
    times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        c = a @ b
        torch.cuda.synchronize() if torch.cuda.is_available() else None
        times.append((time.perf_counter() - t0) * 1000)
    avg = sum(times) / len(times)
    results.append(("cpu", avg, min(times), max(times)))
    print(f"  {'cpu':8s}  avg: {avg:8.2f} ms  min: {min(times):8.2f} ms  max: {max(times):8.2f} ms")

    # CUDA benchmark
    if gpu["cuda_available"]:
        a_cuda = a.to("cuda")
        b_cuda = b.to("cuda")
        times = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            c = a_cuda @ b_cuda
            torch.cuda.synchronize()
            times.append((time.perf_counter() - t0) * 1000)
        avg = sum(times) / len(times)
        results.append(("cuda", avg, min(times), max(times)))
        print(f"  {'cuda':8s}  avg: {avg:8.2f} ms  min: {min(times):8.2f} ms  max: {max(times):8.2f} ms")

    # XPU benchmark
    if gpu["xpu_available"]:
        try:
            a_xpu = a.to("xpu")
            b_xpu = b.to("xpu")
            times = []
            for _ in range(iterations):
                t0 = time.perf_counter()
                c = a_xpu @ b_xpu
                torch.xpu.synchronize()
                times.append((time.perf_counter() - t0) * 1000)
            avg = sum(times) / len(times)
            results.append(("xpu", avg, min(times), max(times)))
            print(f"  {'xpu':8s}  avg: {avg:8.2f} ms  min: {min(times):8.2f} ms  max: {max(times):8.2f} ms")
        except Exception as e:
            print(f"  {'xpu':8s}  ERROR: {e}")

    # MPS benchmark
    if gpu["metal_available"]:
        a_mps = a.to("mps")
        b_mps = b.to("mps")
        times = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            c = a_mps @ b_mps
            torch.mps.synchronize()
            times.append((time.perf_counter() - t0) * 1000)
        avg = sum(times) / len(times)
        results.append(("mps", avg, min(times), max(times)))
        print(f"  {'mps':8s}  avg: {avg:8.2f} ms  min: {min(times):8.2f} ms  max: {max(times):8.2f} ms")

    # Speedup summary
    if len(results) >= 2:
        cpu_avg = results[0][1]
        print("\n  Speedup vs CPU:")
        for name, avg_t, _, _ in results[1:]:
            if cpu_avg > 0:
                print(f"  {name:8s}  {cpu_avg / avg_t:5.1f}x")

    # Optional: model inference benchmark
    if args.model:
        print("\n--- Model Inference Benchmark ---")
        engine = InferenceEngine()
        try:
            handle = engine.load_model(args.model, args.framework)
            times = []
            for _ in range(min(iterations, 10)):
                t0 = time.perf_counter()
                result = engine.infer(handle, [1.0, 2.0, 3.0])
                times.append((time.perf_counter() - t0) * 1000)
            if times:
                avg = sum(times) / len(times)
                print(f"  Model: {args.model}")
                if isinstance(result, BatchResult):
                    print("  Framework: batch")
                else:
                    print(f"  Framework: {result.framework}")
                print(f"  Latency: {avg:.2f} ms avg over {len(times)} runs")
            else:
                print(f"  Model: {args.model}")
                print("  No iterations run (--iterations must be >= 1)")
            engine.shutdown()
        except Exception as e:
            print(f"  ERROR: {e}")

    return 0


def cmd_serve(args) -> int:
    """Start the FastAPI inference server."""
    try:
        from fastapi import FastAPI, HTTPException
        import uvicorn
    except ImportError:
        print(
            "FastAPI/uvicorn required for serve mode.\n"
            "Install: pip install azazael[serve]   or   pip install fastapi uvicorn",
            file=sys.stderr,
        )
        return 1

    from .engine import create_engine
    from .core import BatchResult

    engine = create_engine()
    app = FastAPI(
        title="Eve Unleashed Inference API",
        version="1.1.0",
        description="Multi-framework ML inference REST API",
    )

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "version": "1.1.0",
            "frameworks": engine.available_frameworks,
        }

    @app.get("/stats")
    async def stats():
        return engine.stats

    @app.post("/decide")
    async def decide(req: dict):
        """Clickable decision blocks: allowlisted dev actions only."""
        from . import mods as _mods
        action = req.get("decision", "")
        game = req.get("game", "")
        if action not in ("apply-best", "revert"):
            raise HTTPException(status_code=400,
                                detail="unknown decision: %s" % action)
        if not game:
            raise HTTPException(status_code=400,
                                detail="'game' is required")
        try:
            if action == "apply-best":
                manifest = _mods.apply_best(game)
                return {"decision": action, "applied": manifest}
            n = _mods.revert_mod(game)
            return {"decision": action, "reverted": n}
        except (ValueError, OSError) as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/therapy")
    async def therapy(req: dict):
        """Live therapy: swarm LLM answer with NSP note, else grounding."""
        from . import therapy as _th
        mood = (req.get("mood") or "stressed")[:60]
        note = (req.get("note") or "")[:500]
        prompt = _th.build_prompt(mood, note)
        import asyncio as _aio
        try:
            win, _reason = await _aio.wait_for(
                _aio.to_thread(_swarm_fallback, prompt),
                timeout=SWARM_TIMEOUT_S + 30)
        except Exception as e:
            note_failure("cli:therapy-swarm", e)
            win = None
        if win:
            return {"text": win["text"], "provider": win["provider"],
                    "nsp": win.get("nsp", "nsp-unavailable"),
                    "live": True}
        return {"text": _th.fallback_response(mood, note),
                "provider": "grounding-fallback", "live": False}

    @app.get("/gpu")
    async def gpu_info():
        return engine.gpu_info

    @app.get("/models")
    async def list_models():
        return {"models": engine.list_models()}

    @app.post("/models/load")
    async def load_model(req: dict):
        path = req.get("path", "")
        framework = req.get("framework", "auto")
        if not path:
            raise HTTPException(status_code=400, detail="'path' is required")
        try:
            handle = engine.load_model(path, framework)
            return {"handle": handle, "status": "loaded"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.delete("/models/{handle:path}")
    async def unload_model(handle: str):
        engine.unload_model(handle)
        return {"status": "unloaded"}

    @app.post("/infer")
    async def infer(req: dict):
        model_path = req.get("model", "")
        inputs = req.get("input", [])
        framework = req.get("framework", "auto")
        batch = req.get("batch", False)

        if not model_path:
            raise HTTPException(status_code=400, detail="'model' is required")

        # Check if already loaded (exact path match, not substring)
        matching = [h for h in engine.list_models() if h.split(":", 1)[1] == model_path]
        if not matching:
            try:
                handle = engine.load_model(model_path, framework)
            except Exception as e:
                if "not installed" in str(e) and isinstance(inputs, str):
                    import asyncio as _aio
                    try:
                        win, reason = await _aio.wait_for(
                            _aio.to_thread(_swarm_fallback, inputs),
                            timeout=SWARM_TIMEOUT_S + 30)
                    except Exception as te:
                        note_failure("cli:swarm-serve", te)
                        win, reason = None, "swarm error: %s" % te
                    if win:
                        return {
                            "model": model_path,
                            "framework": "swarm",
                            "provider": win["provider"],
                            "swarm_model": win["model"],
                            "nsp": win.get("nsp", "nsp-unavailable"),
                            "input_shape": None,
                            "output_shape": None,
                            "latency_ms": win["elapsed_ms"],
                            "predictions": [win["text"]],
                        }
                    from .core import ModelLoader as _ML
                    _label = (_ML.guess_framework(Path(model_path))
                              if framework == "auto" else framework)
                    raise HTTPException(
                        status_code=503,
                        detail="Framework '%s' is not installed; "
                               "swarm fallback: %s" % (_label, reason))
                raise HTTPException(status_code=400, detail=str(e))
        else:
            handle = matching[0]

        try:
            result = engine.infer(handle, inputs, batch=batch)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # Handle both single InferenceResult and BatchResult
        if not isinstance(result, BatchResult):
            return {
                "model": result.model_name,
                "framework": result.framework,
                "input_shape": list(result.input_shape) if result.input_shape else None,
                "output_shape": list(result.output_shape) if result.output_shape else None,
                "latency_ms": result.latency_ms,
                "predictions": result.predictions,
            }
        else:
            # BatchResult
            return {
                "model": "batch",
                "framework": "batch",
                "total_time_ms": result.total_time_ms,
                "avg_latency_ms": result.avg_latency_ms,
                "throughput_per_sec": result.throughput_per_sec,
                "count": len(result.results),
                "predictions": [
                    r.predictions for r in result.results
                ] if result.results else [],
            }

    @app.on_event("shutdown")
    async def shutdown():
        engine.shutdown()

    from .model_registry import get_registry as _get_registry
    try:
        _gone = _get_registry().prune_missing()
        print(f"   Registry prune: {len(_gone)} stale entr(ies) removed")
        for _g in _gone[:5]:
            print(f"     pruned: {_g}")
    except Exception as _pe:
        note_failure("cli:serve-prune", _pe)
        print("   Registry prune skipped (registry unreadable)")
    print(f"Eve Unleashed Inference API starting on http://{args.host}:{args.port}")
    print(f"   Frameworks: {engine.available_frameworks}")
    print(f"   Docs:       http://{args.host}:{args.port}/docs")
    print(f"   Health:     http://{args.host}:{args.port}/health")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="eve",
        description="Eve Unleashed — Multi-framework ML Inference CLI",
    )
    sub = parser.add_subparsers(dest="command", help="Command")

    # eve infer
    infer_p = sub.add_parser("infer", help="Run inference on a model")
    infer_p.add_argument("--model", "-m", required=True, help="Path to model file")
    infer_p.add_argument("--input", "-i", required=True, help="Input data (JSON array or text)")
    infer_p.add_argument("--framework", "-f", default="auto",
                        help="Framework: auto, torch, sklearn, transformers, onnx, gguf, vl")
    infer_p.add_argument("--output", "-o", default="text", choices=["text", "json"],
                        help="Output format")
    infer_p.set_defaults(func=cmd_infer)

    # eve registry
    reg_p = sub.add_parser("registry", help="Model registry — track models across projects")
    reg_sub = reg_p.add_subparsers(dest="registry_action", help="Registry action")
    reg_sub.add_parser("show", help="Show registry summary")
    reg_sub.add_parser("prune", help="Drop entries whose files no longer exist")
    reg_scan = reg_sub.add_parser("scan", help="Scan for model files")
    reg_scan.add_argument("--dirs", "-d", help="Comma-separated directories to scan")
    reg_p.add_argument("--verbose", "-v", action="store_true", help="Show all models")
    reg_p.set_defaults(func=cmd_registry, registry_action="show")

    # eve config
    cfg_p = sub.add_parser("config", help="Backup or restore eve configuration")
    cfg_sub = cfg_p.add_subparsers(dest="config_action", help="Config action")
    cfg_backup = cfg_sub.add_parser("backup", help="Save current config to disk")
    cfg_backup.add_argument("--dest", help="Destination path (default: ~/.azazael/eve_config_backup.json)")
    cfg_restore = cfg_sub.add_parser("restore", help="Restore config from backup")
    cfg_restore.add_argument("--source", help="Source path (default: ~/.azazael/eve_config_backup.json)")
    cfg_p.set_defaults(func=cmd_config, config_action="show")

    # eve benchmark
    bench_p = sub.add_parser("benchmark", help="Benchmark GPU vs CPU inference")
    bench_p.add_argument("--size", "-s", type=int, default=2048, help="Matrix size for tensor benchmark")
    bench_p.add_argument("--iterations", "-n", type=int, default=5, help="Benchmark iterations")
    bench_p.add_argument("--model", "-m", help="Optional: model path for inference benchmark")
    bench_p.add_argument("--framework", "-f", default="auto", help="Framework for model benchmark")
    bench_p.set_defaults(func=cmd_benchmark)

    # eve serve
    serve_p = sub.add_parser("serve", help="Start REST API inference server")
    serve_p.add_argument("--host", default="127.0.0.1", help="Bind host")
    serve_p.add_argument("--port", "-p", type=int, default=8080, help="Bind port")
    serve_p.set_defaults(func=cmd_serve)

    # eve cradle
    cradle_p = sub.add_parser("cradle", help="Adopt model files in the cradle natively")
    cradle_p.add_argument("--dir", default=None, help="Cradle dir (default: ~/.azazael/cradle)")
    cradle_p.set_defaults(func=cmd_cradle)

    # eve grievance (Boston Tea Party: public grievance and redress)
    grv_p = sub.add_parser("grievance", help="File grievances, draft redress, find legal aid")
    grv_sub = grv_p.add_subparsers(dest="grievance_action", help="Grievance action")
    grv_file = grv_sub.add_parser("file", help="File a grievance")
    grv_file.add_argument("--respondent", required=True)
    grv_file.add_argument("--category", required=True)
    grv_file.add_argument("--narrative", required=True)
    grv_file.add_argument("--redress", required=True)
    grv_file.add_argument("--evidence", nargs="*", default=[])
    grv_sub.add_parser("show", help="List filed grievances")
    grv_draft = grv_sub.add_parser("draft", help="Draft FOIA + public comment from a grievance")
    grv_draft.add_argument("--id", required=True)
    grv_draft.add_argument("--agency", default="")
    grv_draft.add_argument("--requester", default="")
    grv_dock = grv_sub.add_parser("dockets", help="Search Regulations.gov dockets")
    grv_dock.add_argument("--term", required=True)
    grv_ref = grv_sub.add_parser("refer", help="Free legal-aid referrals")
    grv_ref.add_argument("--state", default=None)
    grv_prove = grv_sub.add_parser("prove", help="Compile court-filing evidence bundle")
    grv_prove.add_argument("--id", required=True)
    grv_sub.add_parser("tutorial", help="Guided grievance-filing tutorial")
    grv_p.set_defaults(func=cmd_grievance, grievance_action="show")

    # eve stats
    abl_p = sub.add_parser("ablate", help="Refusal ablation across providers")
    abl_p.add_argument("--prompt", action="append", default=[],
                       help="Benign prompt (repeatable; default: two built-ins)")
    abl_p.add_argument("--timeout", type=int, default=45)
    abl_p.set_defaults(func=cmd_ablate)

    wasm_p = sub.add_parser("wasm", help="Inner states as Rust WASM tutorial")
    wasm_p.add_argument("--from", dest="from_log", required=True,
                        help="Real `eve ablate` log to compile")
    wasm_p.add_argument("--out", required=True, help="Crate output dir")
    wasm_p.add_argument("--build", action="store_true",
                        help="Run wasm-pack build after generating")
    wasm_p.set_defaults(func=cmd_wasm)

    morph_p = sub.add_parser("morph", help="Convert/morph/mutate files")
    morph_sub = morph_p.add_subparsers(dest="morph_action")
    m_conv = morph_sub.add_parser("convert", help=".csv<->.json")
    m_conv.add_argument("--in", dest="src", required=True)
    m_conv.add_argument("--out", dest="dst", required=True)
    m_mut = morph_sub.add_parser("mutate", help="Seeded byte mutations")
    m_mut.add_argument("--in", dest="src", required=True)
    m_mut.add_argument("--out", required=True)
    m_mut.add_argument("--seed", type=int, default=7)
    m_mut.add_argument("--count", type=int, default=3)
    m_rep = morph_sub.add_parser("report", help="State JSON to Markdown")
    m_rep.add_argument("--in", dest="src", required=True)
    m_rep.add_argument("--title", default="Eve report")
    morph_p.set_defaults(func=cmd_morph)

    mod_p = sub.add_parser("modgame", help="Apply/revert game mods")
    mod_p.add_argument("--game", required=True, help="Game directory")
    mod_p.add_argument("--mod", default=None, help="Mod directory")
    mod_p.add_argument("--revert", action="store_true")
    mod_p.add_argument("--evolve", action="store_true",
                       help="Evolve numeric patches across generations")
    mod_p.add_argument("--generations", type=int, default=5)
    mod_p.add_argument("--seed", type=int, default=7)
    mod_p.add_argument("--fitness", default=None,
                       help="JSON {file::key: target} (default: maximize)")
    mod_p.set_defaults(func=cmd_modgame)

    stats_p = sub.add_parser("stats", help="Show engine statistics")
    stats_p.set_defaults(func=cmd_stats)

    # eve list
    list_p = sub.add_parser("list", help="list frameworks and available models")
    list_p.add_argument("--scan", "-s", action="store_true", help="Scan for model files")
    list_p.set_defaults(func=cmd_list_models)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
