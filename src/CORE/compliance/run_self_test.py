"""Run all 8 compliance self-tests and print results."""
import sys
sys.path.insert(0, '.')

from CORE.compliance.orchestrator import self_test

print('Running self_test()...')
sys.stdout.flush()
success = self_test()
sys.stdout.flush()
print()
print('Result:', success)
sys.exit(0 if success else 1)
