# Azazael Training Data Pipeline — ETL to Model Training

## Overview
The training pipeline moves data from LocalMemoryStore through ETL stages into ML models:
```
Extract (DataPipelineWorm) -> Transform (FeatureEngineer/SchemaAware) -> Load (ModelVersioner)
                                                                              |
                                                                              v
                                                                     Train (RLTrainLoop/SB3Agent/GRPO)
```

## Key Components

### DataPipelineWorm (v2.0.0)
- **Extract**: FTS5 full-text search, source/event_type/severity filters, temporal queries
- **Transform**: Chain of callables, field extraction, severity filtering, flattening, dedup
- **Load**: JSON file output, LocalMemoryStore record, batch processing
- **Split**: Temporal session-based train/val/test (prevents data leakage)
- **CV**: Temporal cross-validation with expanding window + gap days

### SchemaAwareFeatureExtractor (v1.0.0)
- Uses **DATA_SHAPES** (static) and **DYNAMIC_SHAPES** (auto-discovered) registries
- Categorical fields → one-hot encoding with learned vocabularies
- Numeric fields → direct float extraction
- Falls back to generic extraction for unknown event types
- `fit()` builds category vocabs, `extract()` returns 2D feature matrix

### DATA_SHAPES Registry
Currently covers 10 event types: cluster_created, cluster_execution_started/completed,
cross_nature_route, metacluster_orchestrated/discovery, model_registered,
nature_cluster_executed/discovery, training_complete.

### DYNAMIC_SHAPES Registry
Auto-populated via `refresh_dynamic_shapes()` which calls `DataPipelineWorm.auto_discover_shapes()`.
Merged with static DATA_SHAPES at runtime.

## Split Strategies
- **by_session=True**: Splits by session_id (temporal ordering), newest=test, middle=val, oldest=train
- **by_session=False**: Random record-level shuffle
- Session-based prevents data leakage (same session never spans splits)

## CV (Cross-Validation)
- Expanding window: training set grows as folds progress
- Optional `gap_days` between train and test prevents seasonality bleed
- Default 5 folds, configurable via `temporal_cross_validation()`

## Key Files
| File | Purpose |
|------|---------|
| `CORE/WORMS/expansion/learning.py` | DataPipelineWorm, SchemaAwareFeatureExtractor, DATA_SHAPES, DYNAMIC_SHAPES |
| `CORE/WORMS/expansion/learning_features.py` | FeatureEngineer (fast-loading) |
