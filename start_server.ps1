# AI Lecture Summarizer - Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Lecture Summarizer - Starting Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "backend\.venv")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup first:" -ForegroundColor Yellow
    Write-Host "  cd backend"
    Write-Host "  python -m venv .venv"
    Write-Host "  .\.venv\Scripts\activate"
    Write-Host "  pip install -r requirements.txt"
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& "backend\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Open browser after 3 seconds
Start-Sleep -Seconds 3
Start-Process "http://localhost:8000"

Write-Host ""
# Start the server
uvicorn backend.main:app --host 127.0.0.1 --port 8000

