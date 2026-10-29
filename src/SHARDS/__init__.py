#!/usr/bin/env python3
"""Azazael SHARDS — polyglot skill/tool sharding.

A shard is one capability contract with implementations in one or more of
GO / RUST / PYTHON / JAVASCRIPT / POWERSHELL / SHELL behind a shared
JSON-serializable result shape. Python hosts the manifest, the router, and
the self-test; other languages execute through INTERPRETERS runners.

Layout per shard (only what pays — most shards stay Python-only):

    shards/<name>/{shard.py, shard.go, shard.rs, shard.js, shard.ps1, SHARD.md}

Usage:
    from SHARDS.polyglot import run_shard, self_test
    self_test()  # cold recompute across every available toolchain
"""

from SHARDS.registry import SHARDS
from SHARDS.polyglot import run_shard, self_test, supported_shard_langs

__all__ = ["SHARDS", "run_shard", "self_test", "supported_shard_langs"]
