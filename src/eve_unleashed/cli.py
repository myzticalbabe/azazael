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
# from typing import Optional  # removed — all names have native equivalents


def cmd_infer(args) -> int:
    """Run a single inference from the command line."""
    from .engine import create_engine
    from .core import ModelLoader

    # Parse input
    input_str = args.input
    try:
        inputs = json.loads(input_str)
    except json.JSONDecodeError:
        # Treat as plain string (for GGUF/transformers/VL text prompts)
        inputs = input_str

    # Create engine and load model
    engine = create_engine()
    framework = args.framework
    if framework == "auto":
        framework = ModelLoader.guess_framework(Path(args.model))

    try:
        handle = engine.load_model(args.model, framework)
    except Exception as e:
        print(f"ERROR loading model: {e}", file=sys.stderr)
        return 1

    # Run inference
    try:
        result = engine.infer(handle, inputs)
    except Exception as e:
        print(f"ERROR during inference: {e}", file=sys.stderr)
        return 1

    # Output
    if args.output == "json":
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
    from pathlib import Path

    # Frameworks
    fws = ModelLoader.detect_frameworks()
    print("=== Detected Frameworks ===")
    for name, avail in sorted(fws.items()):
        status = "✓ available" if avail else "✗ not installed"
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
            used = "✓" if m.inference_count > 0 else " "
            print(f"  [{used}] {m.filename:40s} {m.framework:12s} {m.size_mb:8.1f} MB  "
                  f"infer: {m.inference_count:4d}  avg: {m.avg_latency_ms:7.2f} ms")

    return 0


def cmd_config(args) -> int:
    """Backup or restore eve configuration."""
    from .config import EveConfig
    from pathlib import Path

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
    import time
    from .engine import InferenceEngine
    from .core import ModelLoader

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
                raise HTTPException(status_code=400, detail=str(e))
        else:
            handle = matching[0]

        try:
            result = engine.infer(handle, inputs, batch=batch)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # Handle both single InferenceResult and BatchResult
        if hasattr(result, "predictions"):
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

    print(f"🚀 Eve Unleashed Inference API starting on http://{args.host}:{args.port}")
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

    # eve stats
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
