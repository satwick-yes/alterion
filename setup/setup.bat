@echo off
title Vani Setup
cd /d "%~dp0\.."
echo Setting up virtual environment...
python -m venv venv
echo Starting Vani Setup...
if exist install.py (
    venv\Scripts\python install.py
) else if exist setup\install.py (
    venv\Scripts\python setup\install.py
) else (
    echo Error: Could not find install.py in root or setup folder!
)
pause
