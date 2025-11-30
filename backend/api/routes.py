from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, constr

from backend.services import summarizer, transcriber

router = APIRouter(prefix="/api", tags=["summarizer"])


class TextPayload(BaseModel):
    text: constr(strip_whitespace=True, min_length=1)  # type: ignore[name-defined]


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.post("/summarize-text")
async def summarize_text(payload: TextPayload):
    summary, chunk_summaries = summarizer.summarize_text(payload.text)
    return {"summary": summary, "chunks": chunk_summaries}


@router.post("/transcribe-and-summarize")
async def transcribe_and_summarize(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix or ".bin"
    temp_path = None
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            contents = await file.read()
            if not contents:
                raise HTTPException(status_code=400, detail="Uploaded file is empty")
            tmp_file.write(contents)
            temp_path = Path(tmp_file.name)
        
        # Transcribe audio/video
        try:
            transcript = transcriber.transcribe_media(temp_path)
        except RuntimeError as e:
            # Re-raise with proper HTTP status
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Transcription failed: {str(e)}"
            )
        
        if not transcript or not transcript.strip():
            raise HTTPException(
                status_code=500, 
                detail="Unable to produce transcript. The audio may be too short, silent, or in an unsupported format."
            )

        # Summarize transcript
        try:
            summary, chunk_summaries = summarizer.summarize_text(transcript)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Summarization failed: {str(e)}"
            )
        
        return {
            "transcript": transcript,
            "summary": summary,
            "chunks": chunk_summaries,
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(exc)}"
        )
    finally:
        # Clean up temp file
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass  # Ignore cleanup errors

