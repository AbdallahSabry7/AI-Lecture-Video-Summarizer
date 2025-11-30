@echo off
echo ========================================
echo AI Lecture Summarizer - Starting Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "backend\.venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup first:
    echo   cd backend
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment and start server
echo Activating virtual environment...
call backend\.venv\Scripts\activate.bat

echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start http://localhost:8000

echo.
uvicorn backend.main:app --host 127.0.0.1 --port 8000

pause

