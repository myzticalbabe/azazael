#!/usr/bin/env python3
# coding: utf-8
"""Shared logging hygiene for Azazael entry points.

Why this exists (2026-09-21). Nine entry points silenced the worm registry's
one-INFO-per-worm import chatter with a process-wide
`logging.disable(logging.CRITICAL)`. That switch does not only mute chatter: it
mutes WARNING and ERROR across the entire process. When the proprioception gate
refused to write for ~30 hours it emitted a WARNING from inside exactly such a
process, so the refusal read as success in the scheduler's log and nothing was
red.

The narrow fix -- silence the KNOWN-noisy loggers by NAME and leave WARNING+
live -- is what `scripts/spine_cycle_apply.py` adopted first. This module is
that fix's single source of truth, so the rest of the family can adopt it
without re-deriving the logger list (and so a future noisy logger is muted in
one place instead of a dozen).

    from log_hygiene import quiet_noisy_loggers
    quiet_noisy_loggers()
"""
from __future__ import annotations

import logging

#: Loggers that emit per-item chatter on import/discovery. They are silenced to
#: WARNING (not CRITICAL) by name; WARNING and above on these loggers is still
#: delivered, and no other logger is affected.
NOISY_LOGGERS: tuple[str, ...] = ("worm_registry",)


def quiet_noisy_loggers(level: int = logging.WARNING) -> None:
    """Quiet the known-chatty loggers BY NAME -- never process-wide.

    Deliberately does NOT call `logging.disable()`: a process-wide switch would
    also swallow this process's operator warnings, which is the exact defect
    this helper exists to prevent (see the module docstring for the ~30h
    silent-refusal incident).
    """
    for name in NOISY_LOGGERS:
        logging.getLogger(name).setLevel(level)
