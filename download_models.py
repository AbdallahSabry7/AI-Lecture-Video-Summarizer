"""
Helper script to download required models.
Run this once to download Whisper and verify fine_tuned model is present.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


def check_whisper_model():
    """Check if Whisper model exists, download if missing."""
    whisper_dir = PROJECT_ROOT / "model" / "whisper-base"
    config_file = whisper_dir / "config.json"

    if config_file.exists():
        print("[OK] Whisper model found")
        return True

    print("[MISSING] Whisper model not found")
    print(f"  Location: {whisper_dir}")
    print("  Downloading Whisper model...")

    try:
        from transformers import WhisperProcessor, WhisperForConditionalGeneration

        whisper_dir.mkdir(parents=True, exist_ok=True)
        model_name = "openai/whisper-base"

        print(f"  Downloading {model_name} (this may take a few minutes)...")
        processor = WhisperProcessor.from_pretrained(model_name)
        model = WhisperForConditionalGeneration.from_pretrained(model_name)

        print(f"  Saving to {whisper_dir}...")
        processor.save_pretrained(str(whisper_dir))
        model.save_pretrained(str(whisper_dir))

        print("  [OK] Whisper model downloaded successfully!")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to download Whisper model: {e}")
        print("  Make sure you have internet connection and try again.")
        return False


def check_fine_tuned_model():
    """Check if fine-tuned summarizer model exists, download if missing."""
    fine_tuned_dir = PROJECT_ROOT / "model" / "Lecture_summarizer"
    config_file = fine_tuned_dir / "config.json"

    if config_file.exists():
        print("[OK] Fine-tuned summarizer model found")
        return True

    print("[MISSING] Fine-tuned summarizer model not found")
    print(f"  Location: {fine_tuned_dir}")
    print("  Downloading model from HuggingFace...")

    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        model_name = "mahmoud1005/lecture_summarizer_bart_large"
        fine_tuned_dir.mkdir(parents=True, exist_ok=True)

        print(f"  Downloading {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        print(f"  Saving model to {fine_tuned_dir}...")
        tokenizer.save_pretrained(str(fine_tuned_dir))
        model.save_pretrained(str(fine_tuned_dir))

        print("  [OK] Fine-tuned summarizer model downloaded successfully!")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to download fine-tuned model: {e}")
        print("  Make sure you have internet connection and try again.")
        return False


if __name__ == "__main__":
    print("Checking models...")
    print("-" * 50)

    whisper_ok = check_whisper_model()
    print()
    fine_tuned_ok = check_fine_tuned_model()

    print("-" * 50)
    if whisper_ok and fine_tuned_ok:
        print("[OK] All models are ready!")
    elif whisper_ok:
        print("[WARNING] Whisper model is ready, but fine-tuned model is missing.")
    else:
        print("[ERROR] Some models are missing. Please download them.")
