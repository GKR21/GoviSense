@echo off
echo ========================================================
echo   Opening Farmer Mobile App in Android Studio...
echo ========================================================

set STUDIO_EXE=C:\Program Files\Android\Android Studio\bin\studio64.exe
set PROJECT_DIR=%~dp0farmer_app\android

if not exist "%STUDIO_EXE%" (
    echo [ERROR] Android Studio not found at:
    echo   %STUDIO_EXE%
    pause
    exit /b 1
)

start "" "%STUDIO_EXE%" "%PROJECT_DIR%"
echo Android Studio launched with project: %PROJECT_DIR%

