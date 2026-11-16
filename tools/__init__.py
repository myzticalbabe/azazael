"""Azazael toolbelt.

This file exists for one reason: without it this directory is an implicit
*namespace* package, and a regular package named ``tools`` in site-packages
always wins the import even when the repository root is first on ``sys.path``.
The effect was measured on 2026-11-15 — four test modules failed collection
with ``ImportError: cannot import name 'staged_scanner_gate' from 'tools'``
while the file sat right here, readable, in this directory:

    tests/test_audit_parseable_files.py
    tests/test_monotone_reduction_check.py
    tests/test_silent_failure_audit.py
    tests/test_staged_scanner_gate.py

A regular package resolves by path order, so the repository copy is used.
"""
