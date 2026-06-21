#!/usr/bin/env python3
"""
Update Docs Paths — Thin wrapper around AZAZAEL_TOOLKIT canonical version.

Canonical source at src/AZAZAEL_TOOLKIT/update_docs_paths.py.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AZAZAEL_TOOLKIT'))
from update_docs_paths import main

if __name__ == '__main__':
    main()
