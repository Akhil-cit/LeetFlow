@echo off
echo ==============================================
echo Setting up LeetCode Daily Agent Background Task
echo ==============================================
echo.

set SCRIPT_DIR=%~dp0

:: Create a scheduled task to run every day at 10:00 AM
schtasks /create /f /tn "LeetCodeDaily" /tr "wscript.exe \"%SCRIPT_DIR%run_invisible.vbs\"" /sc daily /st 10:00

echo.
echo Setup complete! The agent will now run invisibly in the background every day at 10:00 AM.
echo IMPORTANT: Make sure your .env file is updated with your latest LEETCODE_SESSION cookie!
pause
