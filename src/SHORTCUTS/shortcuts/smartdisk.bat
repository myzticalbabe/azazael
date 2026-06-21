@echo off
REM SMARTDISK Launcher
set "PYTHON_PATH=python"
if exist "%USERPROFILE%\AppData\Local\Programs\Python\Python314\python.exe" set "PYTHON_PATH=%USERPROFILE%\AppData\Local\Programs\Python\Python314\python.exe"
"%PYTHON_PATH%" "C:\Users\clint\Desktop\WORMZ\SMARTDISK.py" --health %*
pause
