@echo off

echo Activating virtual environment...
call G:\WebScrapersApp\backend\.venv\Scripts\activate

echo Starting Waitress server...
run uvicorn main:app --host agent-back.lottotry.com --port 9000
pause
