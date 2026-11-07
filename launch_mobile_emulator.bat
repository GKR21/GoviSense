@echo off
echo ========================================================
echo   Launching Android Emulator (Medium_Phone_API_37.0)...
echo ========================================================

set EMULATOR_EXE=%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe

if not exist "%EMULATOR_EXE%" (
    echo [ERROR] Android emulator executable not found at:
    echo   %EMULATOR_EXE%
    echo Please make sure the Android SDK is installed.
    pause
    exit /b 1
)

start "" "%EMULATOR_EXE%" -avd Medium_Phone_API_37.0
echo Android emulator started in background!
