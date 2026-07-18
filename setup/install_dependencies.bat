@echo off
title Jarvis Setup
cd /d "%~dp0\.."
echo ===================================================
echo    JARVIS DEPENDENCY INSTALLER
echo ===================================================
echo.
echo Installing required Python packages...
python setup\setup.py
echo.
echo ===================================================
echo    Done!
echo ===================================================
pause
