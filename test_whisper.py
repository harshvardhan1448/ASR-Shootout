#!/usr/bin/env python
"""Test Whisper transcription with direct audio array"""
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("Testing Whisper transcription with direct audio array...")

try:
    import whisper
    print("✓ Whisper imported")
    
    import librosa
    import numpy as np
    print("✓ Librosa and NumPy imported")
    
    from pathlib import Path
    
    # Load audio with librosa
    audio_path = Path("./recordings/banashankri_rushed_03.wav.mpeg").absolute()
    print(f"Loading: {audio_path}")
    
    y, sr = librosa.load(str(audio_path), sr=16000, mono=True)
    print(f"✓ Audio loaded: {len(y)} samples @ {sr}Hz")
    
    # Normalize
    y = np.clip(y, -1, 1)
    print(f"✓ Audio normalized")
    
    # Load model
    model = whisper.load_model("base")
    print("✓ Whisper model loaded")
    
    # Transcribe using audio array directly (no file needed!)
    print("Transcribing...")
    result = model.transcribe(y, language="hi", verbose=False)
    print(f"✓ Transcription: {result['text'][:100]}")
    print("✓ Success!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
