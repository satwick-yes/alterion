@echo off
title Jarvis - Entire Setup
color 0B
echo ===================================================
echo               JARVIS ENTIRE SETUP
echo ===================================================
echo.
echo Step 1: Installing all dependencies and Playwright browsers...
echo Setting up the background voice listener...
cd /d "%~dp0\.."
python setup\setup.py

echo.
echo ===================================================
echo Step 1.5: Downloading Voice Recognition Model
echo ===================================================
echo.
python setup\download_vosk.py

echo.
echo ===================================================
echo Step 2: Configuring API Keys
echo ===================================================
echo.
python setup\setup_keys.py

echo.
echo ===================================================
echo Setup is fully complete!
echo You can now use the launchers to start Jarvis.
echo ===================================================
pause
