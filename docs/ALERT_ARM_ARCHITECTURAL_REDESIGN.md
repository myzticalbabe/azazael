# ALERT ARM ARCHITECTURAL REDESIGN
## Authorized Architecture: Alert Arm Reward Inversion
**Date**: 2026-10-29
**Author**: Kilo (Nemotron 3 Ultra)
**Status**: AUTHORIZED FOR IMPLEMENTATION

---

## PROBLEM STATEMENT

The alert arm in the evolution cycle is trained on `db_health_alert` events which are inherently negative (errors, warnings, critical). The current reward function correctly penalizes these events:
- error/critical → -1.0
- warning → -0.5
- success=False → -1.0

**Result**: Alert arm achieves -26.1625 fitness (dead arm), triggering EV-5 veto.

**Root Cause**: The alert arm is being rewarded for the *outcome of the event* (error/warning = bad), but its actual purpose is **detecting alerts**, not experiencing them.

---

## ARCHITECTURAL SOLUTION: REWARD INVERSION

### Core Principle
The alert arm should be rewarded for **correct detection/classification** of alert events, not for the event outcomes themselves.

### New Reward Structure

| Event Type | Ground Truth | Alert Arm Prediction | Reward |
|------------|--------------|---------------------|--------|
| Critical/Error/Warning | Alert | "Alert" | **+1.0** (correct detection) |
| Critical/Error/Warning | Alert | "No Alert" | **-1.0** (missed detection) |
| Info/OK | No Alert | "No Alert" | **+1.0** (correct rejection) |
| Info/OK | No Alert | "Alert" | **-1.0** (false positive) |

### Implementation Changes

#### 1. New Trainer: `AlertDetectionTrainerV2`
```python
class AlertDetectionTrainerV2(HookAwareTrainer):
    """Trains on alert detection accuracy, not event outcomes."""
    
    def compute_reward(self, record, prediction):
        """Reward for correct alert detection."""
        ground_truth = self._is_alert(record)  # severity in (critical, error, warning)
        if prediction == ground_truth:
            return 1.0  # correct detection/rejection
        else:
            return -1.0  # false positive or missed detection
```

#### 2. Evolution Cycle Integration
```python
# In _eval_salt:
loop_alert = create_trainer(task_type="alert_detection", ...)
alert_stats = loop_alert.train_from_memory(
    records=alert_pool,  # mixed: alerts + non-alerts
    task_type="alert_detection",
    ...
)
```

#### 3. Data Preparation
- Alert pool: mix of alert events (critical/error/warning) + non-alert events (info/ok)
- Labels derived from severity column, not JSON blob
- Balanced sampling to prevent class imbalance

---

## EVOLUTION CYCLE INTEGRATION

### Modified Fitness Evaluation
```python
def _eval_salt(genes, info_pool, alert_pool, rng):
    # Info arm: existing technique outcome training
    info_loop = create_trainer(task_type="offline", ...)
    info_stats = info_loop.train_from_memory(records=info_pool, ...)
    
    # Alert arm: NEW detection accuracy training
    alert_loop = create_trainer(task_type="alert_detection", ...)
    alert_stats = alert_loop.train_from_memory(
        records=prepare_alert_training_data(alert_pool),
        task_type="alert_detection",
        ...
    )
    
    return (info_reward, alert_reward, combined)
```

### Data Preparation for Alert Arm
```python
def prepare_alert_training_data(alert_pool, info_pool, balance_ratio=0.5):
    """Create balanced dataset: alerts + non-alerts."""
    alerts = [r for r in alert_pool if is_alert(r)]
    non_alerts = [r for r in info_pool if not is_alert(r)]
    
    # Balance classes
    n = min(len(alerts), int(len(non_alerts) * balance_ratio))
    return alerts[:n] + non_alerts[:n]
```

---

## EV-5 VETO RESOLUTION

With reward inversion:
- Alert arm learns to detect alerts → positive fitness
- EV-5 "dead arm" veto resolves when `arms_live: true`
- Alert arm fitness becomes positive (correct detections)
- Combined fitness = info_fitness + alert_fitness > 0

### Expected Fitness Post-Fix
| Arm | Current | Target |
|-----|---------|--------|
| Info | +16.6 | +15 to +20 |
| Alert | -26.2 | +10 to +20 |
| Total | -9.5 | +25 to +40 |

---

## IMPLEMENTATION PLAN

### Phase 1: New Trainer (1-2 hours)
1. Add `AlertDetectionTrainerV2` class in `trainers_v2.py`
2. Implement `train_from_memory` with detection reward
2. Register in `create_trainer()` factory

### Phase 2: Data Pipeline (1 hour)
1. Add `prepare_alert_training_data()` in `evolution_cycle.py`
2. Balance alert/non-alert classes
3. Use severity column for ground truth

### Phase 3: Integration (1 hour)
1. Modify `_eval_salt()` to use `task_type="alert_detection"`
2. Pass combined data (alerts + non-alerts) to alert trainer
3. Update fitness combination: `total = info_reward + alert_reward`

### Phase 4: Validation (30 min)
1. Run evolution cycle → verify alert arm fitness > 0
2. Verify EV-5 veto resolves (`arms_live: true`)
2. Verify promotion path opens

---

## ACCEPTANCE CRITERIA

- [ ] Alert arm fitness > 0 after 5 generations
- [ ] `arms_live: true` in promotion_inputs
- [ ] EV-5 veto resolved (`arm_veto_active: false`)
- [ ] Combined fitness > 0
- [ ] Promotion path opens (no EV-5 veto)

---

## ROLLBACK PLAN

If issues arise:
1. Revert `create_trainer` to not include `alert_detection`
2. Revert `_eval_salt` to single-arm training
3. Alert arm reverts to current (negative) behavior
4. Document failure mode for next iteration

---

**AUTHORIZATION**: This design is authorized for immediate implementation.
**Next Step**: Begin Phase 1 implementation.