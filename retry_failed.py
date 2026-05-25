#!/usr/bin/env python
"""Retry failed Deepgram samples"""
import os
from pathlib import Path
from dotenv import load_dotenv
from src.asr_models import transcribe_deepgram

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
audio_file = Path("./recordings/yellanka_rushed_03.wav.mpeg")

print(f"Retrying: {audio_file.name}")
print("=" * 60)

try:
    transcript, metadata = transcribe_deepgram(str(audio_file), DEEPGRAM_API_KEY)
    
    if "error" in metadata:
        print(f"❌ Still failed: {metadata['error']}")
    else:
        print(f"✅ Success!")
        print(f"Transcript: {transcript[:100]}")
        print(f"Metadata: {metadata}")
except Exception as e:
    print(f"❌ Error: {e}")
