@echo off
cd /d "%~dp0"

echo Waiting for internet connection...
:pingloop
ping -n 1 8.8.8.8 >nul 2>&1
if errorlevel 1 (
    timeout /t 5 >nul
    goto pingloop
)

call venv\Scripts\activate 2>nul || echo "Virtual environment not found, using global python"
python -m agent.main
pause
