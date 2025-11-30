from transformers import BartForConditionalGeneration, BartTokenizerFast
import torch
import os

# Get the absolute path to the main project folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "Model", "Lecture_summarizer")

# Load model and tokenizer
tokenizer = BartTokenizerFast.from_pretrained(model_path)
model = BartForConditionalGeneration.from_pretrained(model_path)

def summarize_chunk(chunk, max_length=150, min_length=40):
    # Match the exact input format you trained on
    prompt = chunk

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    summary_ids = model.generate(
        inputs["input_ids"],
        max_length=max_length,
        min_length=min_length,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def summarize_long_text(long_text, chunk_word_count=450):
    # Split text by words instead of characters
    words = long_text.split()
    chunks = [
        " ".join(words[i:i+chunk_word_count])
        for i in range(0, len(words), chunk_word_count)
    ]

    summaries = []
    for chunk in chunks:
        summary = summarize_chunk(chunk)
        if summary.strip() != "0":  # skip unimportant chunks
            summaries.append(summary)

    final_summary = " ".join(summaries)
    return final_summary