@echo off
setlocal enabledelayedexpansion
echo ========================================================
echo   GoviSense Farmer Mobile App - Emulator Launcher
echo ========================================================

set EMULATOR_EXE=%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe
set ADB_EXE=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe
set FLUTTER_BAT=C:\src\flutter\bin\flutter.bat

echo [1/3] Checking if Android Emulator is running...
"%ADB_EXE%" devices | findstr "emulator-" >nul
if errorlevel 1 (
    echo Starting emulator "Medium_Phone_API_37.0"...
    start "" "%EMULATOR_EXE%" -avd Medium_Phone_API_37.0
    echo Waiting for emulator to boot up...
    timeout /t 10 /nobreak >nul
) else (
    echo Emulator is already running!
)

echo.
echo [2/3] Waiting for device to become ready...
"%ADB_EXE%" wait-for-device

echo.
echo [3/3] Launching Flutter app on emulator...
cd /d "%~dp0farmer_app"
"%FLUTTER_BAT%" run

pause
