@echo off
title Auto Submitter Manager (Privileged)

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% equ 0 goto :admin_ok
echo [Info] Requesting Administrator privileges to prevent UIPI blocks...
powershell -Command "Start-Process '%~f0' -Verb RunAs"
exit /b

:admin_ok
cd /d "%~dp0"
python -u "%~dp0auto_submitter.py"
if %errorLevel% neq 0 (
    echo [Error] Script execution failed.
    pause
)
