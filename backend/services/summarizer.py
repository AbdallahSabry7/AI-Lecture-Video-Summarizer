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
from backend.services.local_variables import DEV_KEY, API_KEY


import re
import html



filler_phrases = [
    'thank you', 'thanks everyone', 'bye', 'see you', 'hi everyone', 'hello everyone',
    'welcome to', 'let’s begin', 'let us begin', 'let’s start', 'so yeah', 'you know',
    'um', 'uh', 'ok', 'okay', 'alright', 'right', 'so now', 'so next', 'moving on',
    'as i said', 'as you can see', 'you can see', 'in this slide', 'on this slide',
    'slide shows', 'we will talk about', 'we’re going to talk about', 'i’m going to talk about',
    'let’s talk about', 'talk a little bit', 'for example', 'for instance',
    'basically', 'actually', 'so basically', 'so actually', 'kind of', 'sort of',
    'like i said', 'that’s it', 'that’s all', 'make sense', 'you know what i mean'
]

filler_pattern = re.compile(r'\b(' + '|'.join(map(re.escape, filler_phrases)) + r')\b', re.IGNORECASE)

def clean_text(text):
    if not isinstance(text, str):
        return ""
    
    # 1. Unescape HTML
    text = html.unescape(text)

    # 2. Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # 3. Remove content inside parentheses (FIXED)
    # Added backslashes to match literal parentheses
    text = re.sub(r"\([^)]*\)", "", text) 

    # 4. Remove filler phrases
    # Note: Be careful here. Removing too much destroys grammar.
    text = filler_pattern.sub(" ", text)

    # 5. Fix multiple dots (FIXED)
    # Added backslash to match literal dots only
    text = re.sub(r"\.{2,}", ".", text) 

    # 6. Fix multiple spaces
    text = re.sub(r"\s+", " ", text)

    text = text.strip()
    return text



REWRITERAI_URL = "https://rewriter.ai/api/paraphraser"


# PARAPHRASER_API_KEY = os.getenv("PARAPHRASER_API_KEY")    
# PARAPHRASER_URL = "https://api.apilayer.com/paraphraser"

def safe_paraphrase(text):
    if len(text.split()) < 20 or not any(c in text for c in ".?!"):
        return text
    return text
    
    # return paraphrase_text(text)

def paraphrase_text(text: str) -> str:
    """
    Paraphrases text using RewriterAI. 
    Returns None if text is empty or API fails (handled in caller).
    """
    if not text or not text.strip():
        return text  # Return as-is if empty

    payload = {
        "dev_key": DEV_KEY,
        "api_key": API_KEY,
        "text": text
    }

    try:
        response = requests.post(REWRITERAI_URL, data=payload, timeout=10)
        data = response.json()

        if data.get("code") != 200:
            print(f"Warning: RewriterAI API returned error: {data}")
            return text # Fallback to original text

        if "text" in data and data["text"]:
            return data["text"]

        return text # Fallback

    except Exception as e:
        print(f"Warning: Paraphrasing service failed ({str(e)}). Returning original summary.")
        return text


@lru_cache(maxsize=1)
def _load_model() -> Tuple[BartTokenizerFast, BartForConditionalGeneration]:
    
    tokenizer = BartTokenizerFast.from_pretrained(SUMMARIZER_DIR)
    model = BartForConditionalGeneration.from_pretrained(SUMMARIZER_DIR).to(DEVICE)
    model.eval()
    return tokenizer, model




def _summarize_chunk(text: str, max_length: int = 256, min_length: int = 128) -> str:
    tokenizer, model = _load_model()

    # text = clean_text(text)
    
    inputs = tokenizer(
        text, 
        return_tensors="pt", 
        truncation=True, 
        max_length=1024, 
        padding="longest"
    ).to(DEVICE)

    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"], 
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
    if not long_text or not long_text.strip():
        return "No text available to summarize.", []


    words = long_text.split()
    
    if len(words) < chunk_word_count :
        raw_summary = _summarize_chunk(long_text)
        return paraphrase_text(raw_summary), [raw_summary]

    chunks = [
        " ".join(words[i : i + chunk_word_count])
        for i in range(0, len(words), chunk_word_count)
    ]

    chunk_summaries: List[str] = []
    for chunk in chunks:
        summary = _summarize_chunk(chunk)
        if summary.strip() != "0":
            chunk_summaries.append(summary)

    final_raw = ". ".join(s.strip().rstrip('.') for s in chunk_summaries)

    final_summary = safe_paraphrase(final_raw)
    
    return final_summary, chunk_summaries