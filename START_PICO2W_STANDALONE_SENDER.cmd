@echo off
cd /d "%~dp0"
py pc\send_alula.py --config build\pico2w-standalone\config.json --out build\pico2w-standalone\installer
pause
