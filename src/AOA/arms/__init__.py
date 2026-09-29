"""AOA Arms - Adapter wrappers for all Quartet and support sub-systems."""
from .azazael_arm import AzazaelArm
from .libra_arm import LibraArm
from .codex_arm import CodexArm
from .eve_arm import EveArm
from .support_arms import PamsArm, PerformanceMonitorArm, LlamaServerArm, AgentSelectorArm
# KaliArm was exported on 2026-09-14 after being found on disk but missing here,
# and this import was lost again by 2026-09-29 while `src/AOA/test_arm_exports.py`
# -- the test written to prevent exactly this -- still documents the fix as done.
# That test is NOT collected by the suite (it lives under src/, and the suite runs
# tests/), so the omission went unnoticed until tests/test_monitor_verdict_accuracy.py
# reported `kali_arm` as defined-but-not-reexported. The omission is functional,
# not cosmetic: `@register_arm` fires only on IMPORT, so an unexported arm never
# enters ARM_REGISTRY -- it cannot be pinned by id or found by capability routing.
from .kali_arm import KaliArm  # noqa: F401
