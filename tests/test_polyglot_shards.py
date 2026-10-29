#!/usr/bin/env python3
"""G1 referencing test for the polyglot shard modules.

Names every new src module so the testing-paradigm gate (G1) is satisfied,
and asserts the golden cross-language agreement contract: every available
toolchain prints AZAZAEL-GOLDEN-OK. Missing toolchains skip cleanly inside
polyglot.self_test() and must not fail this test.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from INTERPRETERS import node_runner, pwsh_runner, sh_runner
from INTERPRETERS import run_code, supported_languages
from SHARDS import polyglot, registry


def test_runner_modules_expose_expected_api():
    assert hasattr(node_runner, "NodeRunner")
    assert hasattr(pwsh_runner, "PwshRunner")
    assert hasattr(sh_runner, "ShRunner")
    for cls in (node_runner.NodeRunner, pwsh_runner.PwshRunner, sh_runner.ShRunner):
        for method in ("run_file", "run_code", "check_syntax"):
            assert callable(getattr(cls, method, None)), f"{cls.__name__}.{method}"


def test_dispatcher_covers_all_shard_langs():
    langs = set(supported_languages())
    # supported_languages() skips short aliases (go/rs/js/sh); the canonical
    # long names are what it reports.
    for expected in ("python", "golang", "rust", "javascript", "powershell", "bash"):
        assert expected in langs, f"dispatcher missing {expected}"


def test_registry_routes_known_tasks():
    assert registry.route_shard("sync kali via sync_all") == "skills-ops"
    assert registry.route_shard("gateway upstream failover") == "gateway"
    assert registry.route_shard("run node_runner test file") == "interpreters"
    assert registry.route_shard("something entirely unknown xyz") == "skills-core"


def test_golden_cross_language_agreement():
    assert polyglot.self_test() is True


def test_run_code_javascript_inline():
    res = run_code("javascript", 'console.log("AZAZAEL-GOLDEN-OK");')
    assert res.success and "AZAZAEL-GOLDEN-OK" in res.stdout


def test_route_lang_spends_budgets():
    from SHARDS.registry import route_lang
    assert route_lang("gateway", "balanced") == "go"
    assert route_lang("gateway", "peak") == "rust"
    assert route_lang("gateway", "fast") in ("go", "rust")
    assert route_lang("skills-core") == "doc"
    assert route_lang("no-such-shard") == "python"
    assert route_lang("interpreters", "balanced") == "python"
    assert route_lang("interpreters", "fast") in (
        "python", "go", "rust", "javascript", "powershell", "bash")
