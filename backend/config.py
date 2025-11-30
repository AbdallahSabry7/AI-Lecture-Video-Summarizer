from pathlib import Path

import torch
import os

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "model"
WHISPER_DIR = MODEL_DIR / "whisper-base"
SUMMARIZER_DIR = MODEL_DIR / "Lecture_summarizer"



DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

TEXT_CHUNK_WORD_COUNT = 900
AUDIO_CHUNK_SIZE = 50_000
TARGET_SAMPLE_RATE = 16_000

