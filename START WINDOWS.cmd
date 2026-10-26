@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 pc\app.py
) else (
    python pc\app.py
)
if errorlevel 1 (
    echo.
    echo Install Python 3.10 or newer from python.org with Tcl/Tk and the Python launcher.
    echo Then double-click START WINDOWS.cmd again.
    pause
)
