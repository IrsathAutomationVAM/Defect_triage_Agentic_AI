@echo off
setlocal
cd /d "%~dp0"
python agent.py
if errorlevel 1 (
    echo.
    echo Agent failed. Make sure Python is installed and available on PATH.
    exit /b 1
)
