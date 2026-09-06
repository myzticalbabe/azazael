# coding: utf-8
"""_logging_shim.py — Lone re-export source for the CORE.logging alias.

IMPORTANT: This file is intentionally PRIVATE (leading underscore) because
it must NOT shadow the Python standard-library ``logging`` module.

Background: When a script runs from inside the package tree
(e.g. ``python CORE/worm_health.py``), ``azazael/src/CORE/`` lands on
``sys.path[0]``. A file literally named ``CORE/logging.py`` therefore
hijacked stdlib ``import logging`` inside ``concurrent.futures``,
triggering an ``AttributeError: module 'logging' has no attribute 'Logger'``
and breaking every module that imports ``concurrent.futures``
(``metrics`` -> ``freethreading``, ``worm_health``, ``graph_artifacts``).

Fix: renamed to ``_logging_shim.py`` and the ``CORE.logging`` alias is wired
in ``CORE/__init__.py`` as a package attribute, so:
    from CORE import logging              # works (package attribute)
    CORE.logging.get_logger(...)          # works
    import logging                        # now correctly resolves to stdlib

Backward-compat usage preserved:
    from CORE.logging import get_logger, configure_logging, StructuredLogger

Thread safety: All re-exports are resolved at import time (module level),
so this is safe under Python 3.14t free-threading.
"""

from CORE.azazael_logging import (
    get_logger as get_logger,
    configure_logging as configure_logging,
    StructuredLogger as StructuredLogger,
)
