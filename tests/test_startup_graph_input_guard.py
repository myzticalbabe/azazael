#!/usr/bin/env python3
# coding: utf-8
"""Session startup must check graph inputs BEFORE building the graph.

Why this file exists. `scripts/check_tooling.py` is the mandatory first step of
a session. The 2026-09-21 lesson was that a single mislabelled file (an HTML
block page named `.pdf`) aborts a ~40-minute `graphify update .`, and the only
symptom is a stalled, un-explainable refresh. So the mislabel audit now runs at
startup, where it is cheap. These tests pin the two properties that make it
worth wiring in: it delegates to the audit tool, and it can NEVER hard-fail the
session -- a guard that can itself stop the session is worse than no guard.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from unittest import mock

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_CHECK_TOOLING = os.path.join(_ROOT, "scripts", "check_tooling.py")
_spec = importlib.util.spec_from_file_location("_check_tooling", _CHECK_TOOLING)
check_tooling = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_tooling)  # type: ignore[union-attr]


class TestStartupGraphInputGuard(unittest.TestCase):

    def test_guard_reports_a_result_without_raising(self):
        res = check_tooling.check_graph_input_hygiene()
        self.assertIn("available", res)
        self.assertIn("ok", res)
        self.assertIn("note", res)

    def test_guard_delegates_to_the_audit_in_check_mode(self):
        """`--check` is the regression semantics: only NEW mislabels fail."""
        seen = {}

        class _Done:
            returncode = 0
            stdout = "checked 500 parseable-binary file(s)\nOK: no new mislabelled files\n"
            stderr = ""

        def _run(cmd, **kw):
            seen["cmd"] = cmd
            return _Done()

        with mock.patch.object(check_tooling.subprocess, "run", _run):
            res = check_tooling.check_graph_input_hygiene()
        self.assertTrue(res["ok"])
        self.assertIn("--check", seen["cmd"])
        self.assertTrue(any("audit_parseable_files" in str(a) for a in seen["cmd"]))

    def test_a_new_mislabel_is_reported_as_not_ok(self):
        class _Fail:
            returncode = 1
            stdout = ("checked 500 file(s)\nNEW mislabels: 1\n"
                      "  archive/x.pdf  (.pdf -> text/<!doctype html)\n")
            stderr = ""

        with mock.patch.object(check_tooling.subprocess, "run",
                               lambda *a, **k: _Fail()):
            res = check_tooling.check_graph_input_hygiene()
        self.assertFalse(res["ok"])

    def test_guard_never_hard_fails_the_session(self):
        """An unavailable/failing audit must not stop startup -- it is insurance."""
        with mock.patch.object(check_tooling.subprocess, "run",
                               side_effect=OSError("no interpreter")):
            res = check_tooling.check_graph_input_hygiene()
        self.assertTrue(res["ok"], "a broken guard must fail SAFE, not fail startup")
        self.assertFalse(res["available"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
