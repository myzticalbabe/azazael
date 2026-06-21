# coding: utf-8
"""
Test Dynamic Logging System
"""
import sys
sys.path.insert(0, str(__file__.rsplit('UTILITIES', 1)[0] + 'UTILITIES'))

from AzazaelDynamicLogger import log, info, warn, error, success, section, logger

section("DYNAMIC LOGGING TEST")

info("Testing info message")
warn("Testing warning message")
error("Testing error message")
success("Testing success message")

info("Checking log history persistence...")
history = logger.get_history()
print(f"\nHistory count: {len(history)} messages")

print("\nTest complete. Check logs/ directory for persistent output.")
