"""
Utilities for chunking long passages and generating abstractive summaries.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List, Tuple
import os
import requests

import torch
from transformers import BartForConditionalGeneration, BartTokenizerFast

from backend.config import DEVICE, SUMMARIZER_DIR, TEXT_CHUNK_WORD_COUNT


DEV_KEY = "apibce198c0eb7a407b9"
API_KEY = "8432a3d38a1d4a3d84af196c441292e7"
REWRITERAI_URL = "https://rewriter.ai/api/paraphraser"


# PARAPHRASER_API_KEY = os.getenv("PARAPHRASER_API_KEY")    
# PARAPHRASER_URL = "https://api.apilayer.com/paraphraser"

def paraphrase_text(text):
    if not text or text.strip() == "":
        raise RuntimeError("Cannot paraphrase empty text")

    payload = {
        "dev_key": DEV_KEY,
        "api_key": API_KEY,
        "text": text
    }

    try:
        response = requests.post(REWRITERAI_URL, data=payload, timeout=15)
        data = response.json()

        if data.get("code") != 200:
            raise RuntimeError(f"RewriterAI error: {data}")

        if "text" in data and data["text"]:
            return data["text"]

        raise RuntimeError(f"Unexpected RewriterAI API response: {data}")

    except Exception as e:
        raise RuntimeError(f"Paraphrasing failed: {str(e)}")



@lru_cache(maxsize=1)
def _load_model() -> Tuple[BartTokenizerFast, BartForConditionalGeneration]:
    """
    Lazily load the fine-tuned T5 summarizer and cache it for reuse across
    requests. Keeping the weights on GPU significantly speeds up inference.
    """
    tokenizer = BartTokenizerFast.from_pretrained(SUMMARIZER_DIR)
    model = BartForConditionalGeneration.from_pretrained(SUMMARIZER_DIR).to(DEVICE)
    model.eval()
    return tokenizer, model


def _summarize_chunk(text: str, max_length: int = 256, min_length: int = 100) -> str:
    tokenizer, model = _load_model()
    prompt = text
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to(DEVICE)
    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=max_length,
            min_length=min_length,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True,
        )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)


def summarize_text(long_text: str, chunk_word_count: int = TEXT_CHUNK_WORD_COUNT) -> Tuple[str, List[str]]:
    """
    Break a long passage into manageable word batches, summarize each chunk,
    and stitch together the important pieces.
    """
    words = long_text.split()
    chunks = [
        " ".join(words[i : i + chunk_word_count])
        for i in range(0, len(words), chunk_word_count)
    ]

    chunk_summaries: List[str] = []
    for chunk in chunks:
        summary = _summarize_chunk(chunk)
        if summary.strip() != "0":
            chunk_summaries.append(summary)

    final_summary = " ".join(chunk_summaries).strip()

    final_summary = paraphrase_text(final_summary)
    
    return final_summary, chunk_summaries

