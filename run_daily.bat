@echo off
cd /d "%~dp0"
call venv\Scripts\activate 2>nul || echo "Virtual environment not found, using global python"
python -m agent.main
