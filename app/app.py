import os
import tempfile
import streamlit as st
import torch
import numpy as np
import soundfile as sf
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from summarizer import summarize_long_text
from pydub import AudioSegment

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
WHISPER_DIR = os.path.join(BASE_DIR, "Model", "whisper-base")

# ----------------------------
# Device check
# ----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
st.write(f"Running on device: {device}")

# ----------------------------
# Load local Whisper model
# ----------------------------
@st.cache_resource(show_spinner=False)
def load_whisper():
    processor = WhisperProcessor.from_pretrained(WHISPER_DIR)
    model = WhisperForConditionalGeneration.from_pretrained(WHISPER_DIR).to(device)
    return processor, model

st.write("Loading Whisper model...")
processor, whisper_model = load_whisper()
st.write("Whisper loaded ✅")

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="AI Lecture Summarizer", layout="wide")
st.title("AI Lecture Video/Audio/Text Summarizer")

input_type = st.radio("Choose input type:", ["Text", "Audio/Video File"])

if input_type == "Text":
    lecture_text = st.text_area("Paste your lecture text here:", height=300)
    if st.button("Summarize Text"):
        if lecture_text.strip():
            with st.spinner("Summarizing..."):
                summary = summarize_long_text(lecture_text)
            st.subheader("Summary:")
            st.write(summary)

elif input_type == "Audio/Video File":
    uploaded_file = st.file_uploader("Upload a video or audio file", type=["mp4","mp3","wav","m4a"])
    if uploaded_file and st.button("Transcribe & Summarize"):
        with st.spinner("Saving uploaded file..."):
            # Save temporary file with original extension
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

        # ----------------------------
        # Convert to WAV if needed
        # ----------------------------
        wav_path = tmp_path
        if suffix.lower() != ".wav":
            audio = AudioSegment.from_file(tmp_path)
            wav_path = tmp_path + ".wav"
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(wav_path, format="wav")

        # ----------------------------
        # Load audio with soundfile
        # ----------------------------
        with st.spinner("Loading audio..."):
            speech, sr = sf.read(wav_path, dtype="float32")
            if len(speech.shape) > 1:  # stereo to mono
                speech = np.mean(speech, axis=1)

        # ----------------------------
        # Transcribe audio in chunks
        # ----------------------------
        chunk_size = 50000  
        transcripts = []
        for start in range(0, len(speech), chunk_size):
            end = min(start + chunk_size, len(speech))
            chunk = speech[start:end]

            input_features = processor(chunk, sampling_rate=sr, return_tensors="pt").input_features.to(device)
            with torch.no_grad():
                pred_ids = whisper_model.generate(input_features, max_new_tokens=400)
            chunk_transcript = processor.batch_decode(pred_ids, skip_special_tokens=True)[0]
            transcripts.append(chunk_transcript)

        transcript = " ".join(transcripts)

        st.subheader("Transcript:")
        st.text_area("Transcript", value=transcript, height=300)

        # ----------------------------
        # Summarize text
        # ----------------------------
        with st.spinner("Summarizing text..."):
            summary = summarize_long_text(transcript)

        st.subheader("Summary:")
        st.text_area("Summary", value=summary, height=200)

