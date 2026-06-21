#!/usr/bin/env python3
"""
COMPREHENSIVE_FIX — Thin wrapper around AZAZAEL_TOOLKIT canonical version.

This file is a convenience alias for the canonical source at
src/AZAZAEL_TOOLKIT/COMPREHENSIVE_FIX.py, kept here for backward
compatibility with code that imports or runs this from the root.

Canonical source is used by Desktop/AZAZAEL_Standalone/build_all.py.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AZAZAEL_TOOLKIT'))
from COMPREHENSIVE_FIX import main# dynamic import from AZAZAEL_TOOLKIT

if __name__ == '__main__':
    main()
