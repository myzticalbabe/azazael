"""Master test runner — runs ALL 90 test files end-to-end, reports every pass/fail."""
import sys
import os
import subprocess
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

TEST_DIR = os.path.join(os.path.dirname(__file__), 'tests')
PYTHON = sys.executable

# All 90 test files
test_files = sorted([
    f for f in os.listdir(TEST_DIR)
    if f.startswith('test_') and f.endswith('.py')
])

print(f"AZAZAEL COMPREHENSIVE TEST RUNNER")
print(f"Python: {sys.version}")
print(f"Found {len(test_files)} test files")
print("=" * 70)

results = {}
total_passed = 0
total_failed = 0
total_skipped = 0
total_tests = 0
start_time = time.time()

for i, tf in enumerate(test_files, 1):
    path = os.path.join(TEST_DIR, tf)
    print(f"\n[{i}/{len(test_files)}] {tf}")
    print("-" * 50)
    
    # Read file size
    size = os.path.getsize(path)
    
    try:
        proc_start = time.time()
        result = subprocess.run(
            [PYTHON, path],
            capture_output=True, text=True,
            timeout=600,  # 10 min per file
        )
        duration = time.time() - proc_start
        elapsed = f"{duration:.1f}s"
        
        # Parse results from stdout
        stdout = result.stdout
        stderr = result.stderr
        
        # Count test results from various formats
        lines = stdout.split('\n')
        file_passed = 0
        file_failed = 0
        file_skipped = 0
        
        for line in lines:
            if '[OK]' in line:
                file_passed += 1
            elif '[FAIL]' in line:
                file_failed += 1
            elif '[SKIP]' in line:
                file_skipped += 1
        
        # Also check exit code
        if result.returncode == 0 and file_failed == 0:
            status = "PASS"
            total_passed += 1
        else:
            status = "FAIL"
            total_failed += 1
        
        # Print summary
        summary_line = ""
        for line in lines:
            if 'Passed:' in line and 'Failed:' in line:
                summary_line = line.strip()
                # Parse summary line (e.g., "Passed: 22, Failed: 0, Skipped: 5")
                parts = line.split(',')
                for part in parts:
                    part = part.strip()
                    if part.startswith('Passed:'):
                        total_tests += int(part.split(':')[1].strip())
                    elif part.startswith('Failed:'):
                        total_tests += int(part.split(':')[1].strip())
                break
        
        results[tf] = {
            'status': status,
            'passed': file_passed,
            'failed': file_failed,
            'skipped': file_skipped,
            'duration': elapsed,
            'exit_code': result.returncode,
            'summary': summary_line,
        }
        
        # Print last 3 lines of output for context
        last_lines = [l for l in lines if l.strip() and ('Passed' in l or 'FAIL' in l or 'OK' in l or 'SKIP' in l)][-5:]
        for l in last_lines:
            print(f"  {l}")
        if stderr and len(stderr) > 50:
            print(f"  STDERR: {stderr.strip()[:200]}")
        
        print(f"  [{status}] {elapsed}")
        
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] Exceeded 10 minutes")
        results[tf] = {'status': 'TIMEOUT', 'duration': '>600s'}
        total_failed += 1
    except Exception as e:
        print(f"  [ERROR] {e}")
        results[tf] = {'status': 'ERROR', 'error': str(e)}
        total_failed += 1

# Summary
total_time = time.time() - start_time
print("\n" + "=" * 70)
print(f"COMPREHENSIVE TEST RESULTS")
print(f"Total test files: {len(test_files)}")
print(f"Total individual tests: {total_tests}")
print(f"Passed: {total_passed}")
print(f"Failed: {total_failed}")
print(f"Duration: {total_time:.0f}s ({total_time/60:.1f}m)")
print()

# List failures
failures = {k: v for k, v in results.items() if v.get('status') in ('FAIL', 'TIMEOUT', 'ERROR')}
if failures:
    print("FAILURES:")
    for tf, info in sorted(failures.items()):
        print(f"  {tf}: {info['status']} ({info.get('duration', '?')})")
        if info.get('summary'):
            print(f"    {info['summary']}")
        if info.get('error'):
            print(f"    Error: {info['error']}")

# Write results to JSON
report = {
    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
    'python': sys.version,
    'total_files': len(test_files),
    'total_tests': total_tests,
    'passed': total_passed,
    'failed': total_failed,
    'results': results,
}
with open(os.path.join(os.path.dirname(__file__), '_test_results.json'), 'w') as f:
    json.dump(report, f, indent=2)

print(f"\nFull results saved to _test_results.json")
sys.exit(0 if total_failed == 0 else 1)
