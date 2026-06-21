@echo off
REM Azazael CLI Assistant Launcher
set "PYTHON_PATH=python"
if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python314\python.exe" set "PYTHON_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python314\python.exe"
"%PYTHON_PATH%" "C:\Users\clint\Desktop\Azazael\Azazael_INTEGRATION.py" %*
pause
