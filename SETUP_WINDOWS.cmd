@echo off
setlocal
cd /d "%~dp0"
py "%~dp0tools\make_sheet.py"
if errorlevel 1 (
  echo Setup did not finish. See the message above and docs\05-troubleshooting.md.
) else (
  start "" "%~dp0build\VIEW_TYPING_SHEET.html"
)
pause
