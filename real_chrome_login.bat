@echo off
echo Opening your REAL Google Chrome to bypass Cloudflare permanently...
echo Please log in to LeetCode, then close the browser entirely.

:: Try to find Chrome installation path
set CHROME_PATH=
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if defined CHROME_PATH (
    %CHROME_PATH% "https://leetcode.com/accounts/login/" --user-data-dir="%~dp0data\browser_profile" --start-maximized
) else (
    echo Could not find Google Chrome installed on this PC.
)
pause
