@echo off
echo ========================================================
echo   Launching GoviSense Mobile App in Chrome...
echo ========================================================

cd /d "%~dp0mobile"
"D:\flutter\bin\flutter.bat" run -d chrome
pause

