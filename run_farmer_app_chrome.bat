@echo off
echo ========================================================
echo   Launching GoviSense Farmer Mobile App in Chrome...
echo ========================================================

cd /d "%~dp0farmer_app"
"C:\src\flutter\bin\flutter.bat" run -d chrome
pause
