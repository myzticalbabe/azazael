"""FLAMING SWORD tool package.

Deliberately empty of imports. ``tools/sword.py`` loads its siblings by path at
import time (``_sibling()`` at sword.py:59), so importing ``tools.sword`` here
would run that resolution for every ``import tools`` and make a partial install
fail at package import rather than at the command that needs the module.

This file exists so the six ``[project.scripts]`` entries resolve after
``pip install .``: ``tools.sword``, ``tools.defender``, ``tools.sentinel``,
``tools.memory_bridge``, ``tools.chain_server``, ``tools.housekeep``.
"""
