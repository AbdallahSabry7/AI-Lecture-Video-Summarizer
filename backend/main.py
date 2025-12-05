from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel  # <-- Added this import
from fpdf import FPDF

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

# --- PDF GENERATION ENDPOINT ---
class PDFRequest(BaseModel):
    text: str
    filename: str = "summary.pdf"

# Note: We use /api/download-pdf to match the frontend's default API URL
@app.post("/api/download-pdf")
async def download_pdf(request: PDFRequest):
    try:
        # Initialize PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Set font (Arial/Helvetica, bold, size 16 for title)
        pdf.set_font("helvetica", "B", 16)
        
        # --- FIX: Use standard cell + ln instead of new_x/new_y ---
        # 0 = width (full page), 10 = height, ln=1 (move to next line), align='C' (center)
        pdf.cell(0, 10, "Lecture Summary", ln=1, align='C') 
        
        pdf.ln(10) # Add extra line break
        
        # Set font for body
        pdf.set_font("helvetica", size=12)
        
        # Write text
        # We replace specific unicode characters that might break standard fonts
        safe_text = request.text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, safe_text)
        
        # Output the PDF as bytes
        pdf_bytes = bytes(pdf.output())
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={request.filename}"
            }
        )
    except Exception as e:
        print(f"PDF Error: {e}") 
        raise HTTPException(status_code=500, detail=str(e))

# --- STATIC FILE SERVING (Keep this at the bottom) ---
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