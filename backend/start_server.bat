@echo off

echo Activating virtual environment...
call G:\BrightdataSnapshot\backend\.venv\Scripts\activate

echo Starting Waitress server...
uvicorn main:app --host agent-back.lottotry.com --port 9000
pause
