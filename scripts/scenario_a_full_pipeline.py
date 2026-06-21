#!/usr/bin/env python3
"""
scenario_a_full_pipeline.py — Scenario A: Full Pipeline (Training → Deployment)

End-to-end neural training pipeline using GRPOTrainer, followed by ONNX
export and deployment via LM Studio or the 12-provider failover chain.

Pipeline:
  DataPipelineWorm → SchemaAwareFeatureExtractor → GRPOTrainer →
  ModelVersioner → ONNX export → LM Studio / Provider Failover

Usage:
    python scripts/scenario_a_full_pipeline.py
    python scripts/scenario_a_full_pipeline.py --source SystemZ --episodes 100
    python scripts/scenario_a_full_pipeline.py --skip-export --dry-run
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path

# Add src/ to path
_src = str(Path(__file__).resolve().parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)


def warm_registry():
    """Warm the worm registry for accurate component discovery."""
    print("Warming worm registry...", flush=True)
    try:
        from CORE.worm_registry import discover_worms
        n = discover_worms()
        print(f"  → {n} worms registered", flush=True)
    except Exception as e:
        print(f"  [WARN] Registry warm failed: {e}", flush=True)


def step_extract(records: int, source: str) -> dict:
    """Step 1: Extract training data from LocalMemoryStore."""
    print("\n── Step 1: Data Extraction ─────────────────────────────", flush=True)
    from CORE.WORMS.expansion.learning import DataPipelineWorm

    pipeline = DataPipelineWorm()
    data = pipeline.extract_from_memory(source=source, limit=records)
    print(f"  Extracted {len(data)} records from source={source}", flush=True)
    return {"pipeline": pipeline, "records": data, "count": len(data)}


def step_featurize(data: dict) -> dict:
    """Step 2: Extract schema-aware features."""
    print("\n── Step 2: Feature Engineering ─────────────────────────", flush=True)
    from CORE.WORMS.expansion.learning import SchemaAwareFeatureExtractor

    records = data["records"]
    if not records:
        print("  [SKIP] No records to featurize", flush=True)
        return data

    extractor = SchemaAwareFeatureExtractor()
    features, labels, meta = extractor.extract_features_and_labels(records)
    print(f"  Feature dim: {meta.get('dim', 0)}", flush=True)
    print(f"  Shapes used: {meta.get('shapes_used', [])}", flush=True)
    print(f"  Unknown shapes: {meta.get('unknown_shapes', 0)}", flush=True)
    data["features"] = features
    data["labels"] = labels
    data["feature_meta"] = meta
    return data


def step_train_grpo(data: dict, episodes: int, source: str) -> dict:
    """Step 3: Train via GRPOTrainer."""
    print("\n── Step 3: GRPO Training ───────────────────────────────", flush=True)
    from CORE.WORMS.expansion.learning_grpo import GRPOTrainer

    trainer = GRPOTrainer()
    records = data.get("records", [])

    if not records:
        print("  [SKIP] No training data — registering placeholder", flush=True)
        data["train_result"] = {"trainer": "GRPOTrainer", "trained": False,
                                "error": "No training data"}
        return data

    groups = trainer.generate_group({"task_type": "pipeline", "source": source},
                                    group_size=min(8, max(1, len(records) // 4)))
    print(f"  Generated {len(groups)} candidate groups", flush=True)

    rewards = trainer.compute_group_rewards(groups, {
        "task_type": "pipeline", "source": source,
    })
    trainer.update_policy(groups, rewards, context_key=f"scenario_a_{source}")
    stats = trainer.get_stats()
    best_worm = trainer.select_best(f"scenario_a_{source}")

    print(f"  Updates:       {stats.get('n_updates', 0)}", flush=True)
    print(f"  Contexts:      {stats.get('n_contexts', 0)}", flush=True)
    print(f"  Worms scored:  {stats.get('total_worms_scored', 0)}", flush=True)
    print(f"  Best worm:     {best_worm}", flush=True)

    data["train_result"] = {
        "trainer": "GRPOTrainer",
        "trained": True,
        "n_updates": stats.get("n_updates", 0),
        "n_contexts": stats.get("n_contexts", 0),
        "total_worms_scored": stats.get("total_worms_scored", 0),
        "best_worm": best_worm,
    }
    data["trainer"] = trainer
    return data


def step_register(data: dict, model_name: str) -> dict:
    """Step 4: Register model with ModelVersioner."""
    print("\n── Step 4: Model Registration ───────────────────────────", flush=True)
    from CORE.WORMS.expansion.learning import ModelVersioner

    versioner = ModelVersioner()
    train_result = data.get("train_result", {})

    if not train_result.get("trained"):
        print("  [SKIP] No trained model to register", flush=True)
        return data

    version = versioner.register_model(
        name=model_name,
        version=f"v{int(time.time())}",
        metrics={
            "n_updates": train_result.get("n_updates", 0),
            "total_worms_scored": train_result.get("total_worms_scored", 0),
            "records_used": data.get("count", 0),
        },
        metadata={
            "scenario": "A_full_pipeline",
            "trainer": "GRPOTrainer",
            "source": data.get("source", "unknown"),
            "pipeline": "DataPipelineWorm → SchemaAwareFeatureExtractor → GRPOTrainer → ModelVersioner",
        },
    )
    print(f"  Model:    {model_name}", flush=True)
    print(f"  Version:  {version.get('version', '?')}", flush=True)
    data["model_name"] = model_name
    data["version"] = version
    return data


def step_export_onnx(data: dict, dry_run: bool) -> dict:
    """Step 5: Export model to ONNX format."""
    print("\n── Step 5: ONNX Export ─────────────────────────────────", flush=True)

    onnx_path = Path("output") / f"{data.get('model_name', 'model')}.onnx"
    onnx_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from ORCHESTRATION.ml_platforms.onnx_integration import export_to_onnx
    except ImportError:
        print("  [INFO] ml-platforms ONNX module not available", flush=True)
        print(f"  [MOCK] ONNX export would write to: {onnx_path}", flush=True)
        data["onnx_path"] = str(onnx_path) if dry_run else None
        return data

    if dry_run:
        print(f"  [DRY-RUN] Would export to: {onnx_path}", flush=True)
        data["onnx_path"] = str(onnx_path)
        return data

    try:
        export_to_onnx(data.get("trainer"), str(onnx_path))
        print(f"  Exported to: {onnx_path}", flush=True)
        size_kb = onnx_path.stat().st_size / 1024 if onnx_path.exists() else 0
        print(f"  Size: {size_kb:.1f} KB", flush=True)
        data["onnx_path"] = str(onnx_path)
    except Exception as e:
        print(f"  [WARN] ONNX export failed: {e}", flush=True)
        data["onnx_path"] = None
    return data


def step_deploy(data: dict, dry_run: bool) -> dict:
    """Step 6: Deploy via LM Studio or provider failover."""
    print("\n── Step 6: Deployment ───────────────────────────────────", flush=True)

    onnx_path = data.get("onnx_path")
    deploy_targets = []

    # Option A: LM Studio local server
    try:
        from ORCHESTRATION.ml_platforms.lm_studio_server import start_lm_studio
        if not dry_run:
            port = start_lm_studio()
            deploy_targets.append(f"LM Studio (localhost:{port})")
            print(f"  LM Studio started on port {port}", flush=True)
        else:
            deploy_targets.append("LM Studio (localhost:1234)")
            print(f"  [DRY-RUN] Would start LM Studio with model: {onnx_path}", flush=True)
    except ImportError:
        deploy_targets.append("LM Studio (ImportError — ml-platforms not available)")
        print("  [INFO] LM Studio server module not available", flush=True)

    # Option B: Provider failover chain
    try:
        from CORE.inference.providers import get_best_provider, list_providers
        all_providers = list_providers()
        best = get_best_provider()
        deploy_targets.append(f"Provider failover chain ({len(all_providers)} available)")
        if not dry_run:
            print(f"  Best provider: {best}", flush=True)
    except ImportError:
        deploy_targets.append("Provider failover (CORE.inference not available)")
        print("  [INFO] Inference providers module not available", flush=True)

    data["deploy_targets"] = deploy_targets
    data["deployed"] = True
    return data


def summary(data: dict, elapsed: float):
    """Print a formatted summary of the pipeline run."""
    print("\n" + "=" * 60)
    print("  SCENARIO A: FULL PIPELINE — Complete")
    print("=" * 60)
    print(f"  Source:        {data.get('source', '?')}")
    print(f"  Records:       {data.get('count', 0)}")
    print(f"  Feature dim:   {data.get('feature_meta', {}).get('dim', 'N/A')}")
    print(f"  Trainer:       GRPOTrainer")
    tr = data.get("train_result", {})
    print(f"  Trained:       {tr.get('trained', False)}")
    print(f"  Best worm:     {tr.get('best_worm', 'N/A')}")
    print(f"  Model:         {data.get('model_name', 'N/A')}")
    print(f"  Version:       {data.get('version', {}).get('version', 'N/A')}")
    print(f"  ONNX path:     {data.get('onnx_path', 'N/A')}")
    print(f"  Deployed to:   {', '.join(data.get('deploy_targets', ['N/A']))}")
    print(f"  Duration:      {elapsed:.1f}s")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Scenario A: Full Pipeline — GRPO training → ONNX → deploy",
    )
    parser.add_argument("--source", default="SystemZ",
                        help="Data source filter (default: SystemZ)")
    parser.add_argument("--records", type=int, default=200,
                        help="Max training records to extract (default: 200)")
    parser.add_argument("--episodes", type=int, default=50,
                        help="GRPO training episodes (default: 50)")
    parser.add_argument("--model-name", default=None,
                        help="Custom model name (default: auto-generated)")
    parser.add_argument("--skip-export", action="store_true",
                        help="Skip ONNX export step")
    parser.add_argument("--skip-deploy", action="store_true",
                        help="Skip deployment step")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print steps without executing")
    parser.add_argument("--output", default=None,
                        help="Save pipeline results JSON to path")

    args = parser.parse_args()

    print("=" * 60)
    print("  SCENARIO A: Full Pipeline")
    print("  DataPipelineWorm → SchemaAwareFeatureExtractor →")
    print("  GRPOTrainer → ModelVersioner → ONNX export → Deploy")
    print("=" * 60)
    print(flush=True)

    t0 = time.time()

    # Assemble data context
    data = {"source": args.source}

    # Step 1: Extract
    warm_registry()
    ext = step_extract(args.records, args.source)
    data.update(ext)

    # Step 2: Featurize
    data = step_featurize(data)

    # Step 3: Train
    # If no real data, we still register a placeholder for demo purposes
    data = step_train_grpo(data, args.episodes, args.source)

    # Generate model name
    model_name = args.model_name or f"GRPO_{args.source}_{time.strftime('%Y%m%d_%H%M%S')}"

    # Step 4: Register
    data = step_register(data, model_name)

    # Step 5: Export ONNX
    if not args.skip_export:
        data = step_export_onnx(data, args.dry_run)
    else:
        print("\n── Step 5: ONNX Export [SKIPPED] ──────────────────────", flush=True)

    # Step 6: Deploy
    if not args.skip_deploy:
        data = step_deploy(data, args.dry_run)
    else:
        print("\n── Step 6: Deployment [SKIPPED] ────────────────────────", flush=True)

    elapsed = time.time() - t0
    summary(data, elapsed)

    # Save results if requested
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Filter out unserializable objects
        serializable = {k: v for k, v in data.items()
                        if isinstance(v, (str, int, float, bool, list, dict, type(None)))}
        out_path.write_text(json.dumps(serializable, indent=2, default=str), encoding="utf-8")
        print(f"\nResults saved to: {out_path}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
