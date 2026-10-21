@echo off
REM ============================================================
REM run_tests.bat — Run key Azazael unit and integration tests
REM ============================================================
setlocal enabledelayedexpansion

set PYTHONPATH=%CD%\src;%CD%\packages\azazael-core\src;%PYTHONPATH%
set PYTHONFAULTHANDLER=1

echo ========================================
echo  AZAZAEL TEST RUNNER
echo ========================================
echo.

set TESTS_PASSED=0
set TESTS_FAILED=0

call :run_test "PamsRecorder Unit" tests\test_pams_recorder.py
call :run_test "CLUSTERWORMS Integration" tests\test_clusterworms_integration.py
call :run_test "Logger" tests\test_logging.py
call :run_test "Free-Threading" tests\test_freethreading.py
call :run_test "Metrics" tests\test_metrics.py
call :run_test "CLI Observability" tests\test_cli_observability.py
call :run_test "Local Memory" tests\test_local_memory.py
call :run_test "MemoryBus" tests\test_memorybus.py
call :run_test "Worm Imports" tests\test_worm_imports.py
call :run_test "Config + Breaker" tests\test_config_and_breaker.py
call :run_test "Pool" tests\test_pool.py
call :run_test "DLQ" tests\test_dlq.py

echo.
echo ========================================
echo  RESULTS: %TESTS_PASSED% passed, %TESTS_FAILED% failed
echo ========================================

if %TESTS_FAILED% gtr 0 (
    exit /b 1
)
exit /b 0

:run_test
set TEST_NAME=%~1
set TEST_FILE=%~2

echo [RUNNING] %TEST_NAME% (%TEST_FILE%)
python -X faulthandler -m pytest %TEST_FILE% -v --tb=short -x --faulthandler 2>&1
if %ERRORLEVEL% equ 0 (
    echo [PASS] %TEST_NAME%
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] %TEST_NAME%
    set /a TESTS_FAILED+=1
)
echo.
goto :eof
