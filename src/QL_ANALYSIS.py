#!/usr/bin/env python3
"""
QL Analysis — Thin wrapper around AZAZAEL_TOOLKIT canonical version.

Canonical source at src/AZAZAEL_TOOLKIT/QL_ANALYSIS.py,
used by Desktop/AZAZAEL_Standalone/build_all.py.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AZAZAEL_TOOLKIT'))
from QL_ANALYSIS import main

if __name__ == '__main__':
    main()
