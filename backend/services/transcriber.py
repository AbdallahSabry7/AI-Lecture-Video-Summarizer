"""
Audio/video transcription helpers backed by Whisper.
"""
from __future__ import annotations

import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Tuple

import numpy as np
import soundfile as sf
import torch
from pydub import AudioSegment
from transformers import WhisperForConditionalGeneration, WhisperProcessor

from backend.config import (
    AUDIO_CHUNK_SIZE,
    DEVICE,
    TARGET_SAMPLE_RATE,
    WHISPER_DIR,
)


@lru_cache(maxsize=1)
def _load_whisper() -> Tuple[WhisperProcessor, WhisperForConditionalGeneration]:
    """
    Load Whisper model from local directory. If model files are missing,
    this will attempt to download from Hugging Face (requires internet).
    """
    if not WHISPER_DIR.exists() or not any(WHISPER_DIR.iterdir()):
        raise RuntimeError(
            f"Whisper model directory not found at {WHISPER_DIR}. "
            "Please run model/whisper-base/whisper_load.py to download the model first, "
            "or ensure the model files are present in the directory."
        )
    
    # Check if config.json exists (indicates model is present)
    config_file = WHISPER_DIR / "config.json"
    if not config_file.exists():
        raise RuntimeError(
            f"Whisper model files not found in {WHISPER_DIR}. "
            "The model needs to be downloaded. Run: python model/whisper-base/whisper_load.py"
        )
    
    try:
        processor = WhisperProcessor.from_pretrained(str(WHISPER_DIR), local_files_only=True)
        model = WhisperForConditionalGeneration.from_pretrained(str(WHISPER_DIR), local_files_only=True).to(DEVICE)
        model.eval()
        return processor, model
    except Exception as e:
        # If local_files_only fails, try without it (will download if needed)
        if "local_files_only" in str(e).lower():
            raise RuntimeError(
                f"Whisper model files incomplete in {WHISPER_DIR}. "
                "Please run: python model/whisper-base/whisper_load.py to download the complete model."
            ) from e
        raise RuntimeError(f"Failed to load Whisper model: {str(e)}") from e


def _ensure_wav(input_path: Path) -> Path:
    if input_path.suffix.lower() == ".wav":
        return input_path
    try:
        audio = AudioSegment.from_file(str(input_path))
        audio = audio.set_channels(1).set_frame_rate(TARGET_SAMPLE_RATE)
        wav_path = input_path.with_suffix(".wav")
        audio.export(str(wav_path), format="wav")
        return wav_path
    except Exception as e:
        error_msg = str(e)
        if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
            raise RuntimeError(
                "ffmpeg is required for audio/video processing. "
                "Please install ffmpeg and ensure it's in your PATH. "
                "Download from: https://ffmpeg.org/download.html"
            ) from e
        raise RuntimeError(f"Failed to convert audio file: {error_msg}") from e


def _load_audio(wav_path: Path) -> Tuple[np.ndarray, int]:
    speech, sample_rate = sf.read(wav_path, dtype="float32")
    if speech.ndim > 1:
        speech = np.mean(speech, axis=1)
    return speech, sample_rate


def transcribe_media(temp_file: Path) -> str:
    """
    Convert any supported media file to mono 16k wav, then run chunked Whisper
    inference to produce a transcript string.
    """
    try:
        cleaned_path = _ensure_wav(temp_file)
        speech, sample_rate = _load_audio(cleaned_path)
    except Exception as e:
        # Clean up temp file on error
        try:
            temp_file.unlink(missing_ok=True)  # type: ignore[attr-defined]
        except (TypeError, AttributeError):
            if temp_file.exists():
                temp_file.unlink()
        raise
    
    processor, model = _load_whisper()

    transcripts = []
    for start in range(0, len(speech), AUDIO_CHUNK_SIZE):
        end = min(start + AUDIO_CHUNK_SIZE, len(speech))
        chunk = speech[start:end]
        input_features = processor(
            chunk, sampling_rate=sample_rate, return_tensors="pt"
        ).input_features.to(DEVICE)
        with torch.no_grad():
            pred_ids = model.generate(input_features, max_new_tokens=400)
        chunk_transcript = processor.batch_decode(
            pred_ids, skip_special_tokens=True
        )[0]
        transcripts.append(chunk_transcript)

    transcript = " ".join(transcripts).strip()

    # Clean up converted wav files to avoid disk bloat
    if cleaned_path != temp_file:
        try:
            cleaned_path.unlink(missing_ok=True)  # type: ignore[attr-defined]
        except TypeError:
            if cleaned_path.exists():
                cleaned_path.unlink()

    try:
        temp_file.unlink(missing_ok=True)  # type: ignore[attr-defined]
    except TypeError:
        if temp_file.exists():
            temp_file.unlink()

    return transcript

