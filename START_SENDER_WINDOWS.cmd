@echo off
setlocal
cd /d "%~dp0"
echo Artemis installer - PC sender
py "%~dp0pc\send_alula.py"
if errorlevel 1 (
  echo Sender could not start or transfer failed. Review the error above.
)
pause
