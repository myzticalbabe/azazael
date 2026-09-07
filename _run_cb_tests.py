"""Wrapper to run circuit breaker tests — prevents basher from using unittest."""
import subprocess, sys, os
test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "test_circuit_breaker_integration.py")
result = subprocess.run([sys.executable, test_file], capture_output=True, text=True, timeout=300)
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)
