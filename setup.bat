@echo off
:: Request Administrator privileges (needed for VC Redistributable)
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :RunAdmin
) else (
    echo Requesting Administrator privileges to perform full system setup...
    powershell -Command "Start-Process -FilePath '%~dpnx0' -Verb RunAs"
    exit /B
)

:RunAdmin
:: Ensure we are in the correct project directory, not System32
cd /d "%~dp0"
title Jarvis Full System Setup
echo ========================================================
echo                 JARVIS FULL SETUP
echo ========================================================
echo.

echo [1/4] Installing Microsoft Visual C++ Redistributable (Required for AI)...
powershell -Command "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'vc_redist.x64.exe'; Start-Process -FilePath '.\vc_redist.x64.exe' -ArgumentList '/install /passive /norestart' -Wait; Remove-Item vc_redist.x64.exe -ErrorAction SilentlyContinue"

echo.
echo [2/4] Installing Python Backend Dependencies...
:: Ensure pip is up to date
python -m pip install --upgrade pip

:: Install specific pytorch version first to bypass Windows long-path limits
python -m pip install torch==2.0.1 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu

:: Install the rest of the dependencies
python -m pip install -r requirements.txt

echo.
echo [3/4] Installing Node Frontend Dependencies...
if exist "frontend" (
    cd frontend
    call npm install
    cd ..
) else (
    echo Frontend folder not found. Skipping Node dependencies.
)

echo.
echo [4/4] Setting up Playwright Browsers...
python -m playwright install

echo.
echo ========================================================
echo   Setup Complete! You can now run Start_Jarvis.bat
echo ========================================================
pause
