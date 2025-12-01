# AI Lecture Video Summarizer

Full-stack lecture assistant that:

- Transcribes long-form audio or video with a local Whisper model
- Summarizes transcripts with a fine-tuned Bart model trained for lecture notes
- Exposes a REST API (FastAPI) plus a lightweight frontend for uploads and text summaries

## Project layout

```
AI-Lecture-Video-Summarizer-main
├── backend/                 # FastAPI service + model loaders
├── Frontend/                # Static web UI that talks to the backend
├── app/                     # Legacy Streamlit prototype (still usable)
├── model/
│   ├── whisper-base/        # Local Whisper weights
│   └── Lecture_summarizer/  # Fine-tuned T5 weights
└── README.md
```

> **Note**  
> Change the API_KEY and DEV_KEY to your keys in "backend\services\summarizer.py".
> Download/keep both model folders in `model/` before starting the backend by running "download_models.py".  
> Use `download_models.py` to check if models are downloaded and download them .  
> **For audio/video processing**: Install [ffmpeg](https://ffmpeg.org/download.html) and ensure it's in your system PATH. This is required for converting audio/video files to the format needed by Whisper.

## Quick Start (Easiest Way)

**Just double-click `start_server.bat`** (or run `start_server.ps1` in PowerShell) and the app will:
- Start the backend server
- Serve the frontend automatically
- Open your browser to `http://localhost:8000`

No need to run separate commands! Everything runs from one server.

## Manual Setup

### 1. Install Dependencies

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the Server

**Option A: Use the launcher (Recommended)**
- Double-click `start_server.bat` (Windows)
- Or run `.\start_server.ps1` in PowerShell

**Option B: Manual start**
```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 3. Open in Browser

Visit `http://localhost:8000` - the frontend is automatically served!

## API Endpoints

Visit `http://localhost:8000/docs` for the interactive Swagger UI. Available routes:

- `GET /api/health` – service status
- `POST /api/summarize-text` – summarize raw text (`{"text": "..."}`)
- `POST /api/transcribe-and-summarize` – multipart upload (`file=<audio/video>`)

## Legacy Streamlit app

The original Streamlit prototype is still available under `app/app.py`. Activate the same virtual environment, install `streamlit`, and run:

```powershell
streamlit run app/app.py
```

This UI directly loads the local models for quick experiments; the FastAPI backend uses the same core logic so results are identical.
