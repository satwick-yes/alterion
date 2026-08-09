@echo off
title Vani Setup
cd /d "%~dp0\.."
echo Setting up virtual environment...
python -m venv venv
echo Starting Vani Setup...
venv\Scripts\python setup\install.py
pause
