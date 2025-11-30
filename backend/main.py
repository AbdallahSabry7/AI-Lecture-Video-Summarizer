from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api.routes import router as api_router

# Get project root directory
BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "Frontend"

app = FastAPI(title="AI Lecture Summarizer API")

# CORS middleware - allow all origins when serving from same server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all when serving from same origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Serve frontend static files
if FRONTEND_DIR.exists():
    # Serve index.html at root
    @app.get("/")
    async def serve_frontend():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "AI Lecture Summarizer - Frontend not found"}
    
    # Serve CSS, JS, and other frontend files
    @app.get("/{filename}")
    async def serve_frontend_files(filename: str):
        # Don't interfere with API routes
        if filename.startswith("api"):
            return {"error": "Not found"}
        
        file_path = FRONTEND_DIR / filename
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # Fallback to index.html for any other path
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"error": "File not found"}
else:
    @app.get("/")
    async def root():
        return {"message": "AI Lecture Summarizer backend is running"}

