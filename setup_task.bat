@echo off
echo ==============================================
echo Setting up LeetCode Daily Agent Background Task
echo ==============================================
echo.

set SCRIPT_DIR=%~dp0

:: Create a scheduled task to run automatically whenever you log into your computer
schtasks /create /f /tn "LeetCodeDaily" /tr "wscript.exe \"%SCRIPT_DIR%run_invisible.vbs\"" /sc onlogon

echo.
echo Setup complete! The agent will now run invisibly in the background every time you turn on your PC.
echo It will wait for your Wi-Fi to connect, and then solve the daily problem using your saved Chrome profile!
pause
