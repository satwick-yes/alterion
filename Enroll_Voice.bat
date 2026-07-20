@echo off
:: Check for admin rights (required for creating symlinks for the AI model on Windows)
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :RunAdmin
) else (
    echo Requesting Administrator privileges to download AI model files...
    powershell -Command "Start-Process -FilePath '%~dpnx0' -Verb RunAs"
    exit /B
)

:RunAdmin
:: Ensure we are in the correct project directory, not System32
cd /d "%~dp0"
title Jarvis Voice Biometrics Enrollment
echo =========================================
echo Starting Voice Biometrics Enrollment...
echo =========================================
echo.
python -m core.enroll_voice
echo.
pause
