@echo off
echo ========================================================
echo   Launching GoviSense Farmer Mobile App on Emulator...
echo ========================================================

cd /d "%~dp0farmer_app"
"C:\src\flutter\bin\flutter.bat" run -d Medium_Phone_API_37.0
pause
