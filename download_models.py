"""
Helper script to download required models.
Run this once to download Whisper and verify T5 model is present.
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

def check_t5_model():
    """Check if T5 summarizer model exists."""
    t5_dir = PROJECT_ROOT / "model" / "Lecture_summarizer"
    config_file = t5_dir / "config.json"
    
    if config_file.exists():
        print("[OK] T5 summarizer model found")
        return True
    
    print("[MISSING] T5 summarizer model not found")
    print(f"  Location: {t5_dir}")
    print("  This model should be trained/fine-tuned separately.")
    return False

if __name__ == "__main__":
    print("Checking models...")
    print("-" * 50)
    
    whisper_ok = check_whisper_model()
    print()
    t5_ok = check_t5_model()
    
    print("-" * 50)
    if whisper_ok and t5_ok:
        print("[OK] All models are ready!")
    elif whisper_ok:
        print("[WARNING] Whisper model is ready, but T5 model is missing.")
    else:
        print("[ERROR] Some models are missing. Please download them.")

