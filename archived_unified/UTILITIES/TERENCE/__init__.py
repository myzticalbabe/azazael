# coding: utf-8
"""
TERENCE Wrapper - Fixed imports

Usage:
    >>> from TERENCE.terence import TERENCE
    >>> t = TERENCE()
    >>> print(t.VERSION)
"""

from TERENCE.terence_core import TERENCE, Fix, FixStats

__all__ = ["TERENCE", "Fix", "FixStats"]
