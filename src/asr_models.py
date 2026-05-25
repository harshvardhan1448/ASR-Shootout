"""
ASR Model Interface - Deepgram Only
"""

import os
from typing import Dict, Tuple
from pathlib import Path

# ============ DEEPGRAM ============
def transcribe_deepgram(audio_path: str, api_key: str) -> Tuple[str, Dict]:
    """Transcribe with Deepgram API (REST endpoint)"""
    try:
        import requests
        
        # Read audio file
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        # Deepgram REST API endpoint
        url = "https://api.deepgram.com/v1/listen"
        
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/octet-stream"
        }
        
        params = {
            "model": "nova-2",
            "language": "hi",
            "smart_format": "true"
        }
        
        response = requests.post(url, headers=headers, data=audio_data, params=params, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract transcription
        if "results" in result and "channels" in result["results"]:
            transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
            confidence = result["results"]["channels"][0]["alternatives"][0]["confidence"]
            
            metadata = {
                "model": "deepgram-nova-2",
                "confidence": confidence,
            }
            return transcript, metadata
        else:
            return "", {"error": "Unexpected response format", "model": "deepgram-nova-2"}
    
    except Exception as e:
        return "", {"error": str(e), "model": "deepgram-nova-2"}


# ============ OPENAI WHISPER ============
def transcribe_whisper(audio_path: str, api_key: str, use_api: bool = False) -> Tuple[str, Dict]:
    """
    Transcribe with OpenAI Whisper
    - use_api=False: Use local whisper model (offline, free) - DEFAULT
    - use_api=True: Use OpenAI API (requires API key and credit)
    """
    try:
        if use_api:
            # Use OpenAI API - newer client-based approach
            from openai import OpenAI
            
            client = OpenAI(api_key=api_key)
            
            with open(audio_path, 'rb') as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="hi"
                )
            
            metadata = {
                "model": "whisper-1-api",
                "language": "hi"
            }
            return transcript.text, metadata
        
        else:
            # Local whisper (free) - use audio arrays directly
            import whisper
            import librosa
            import numpy as np
            from pathlib import Path
            
            # Convert to absolute path
            audio_path = str(Path(audio_path).absolute())
            
            try:
                # Load audio with librosa
                y, sr = librosa.load(audio_path, sr=16000, mono=True)
                
                # Normalize to [-1, 1] range (what Whisper expects)
                y = np.clip(y, -1, 1)
                
                # Load and transcribe with Whisper
                # Using the audio array directly instead of temp file
                # This avoids needing ffmpeg
                model = whisper.load_model("base")
                
                # Whisper's transcribe can accept float32 audio directly
                result = model.transcribe(
                    y, 
                    language="hi", 
                    verbose=False
                )
                
                metadata = {
                    "model": "whisper-base-local",
                    "language": "hi"
                }
                return result['text'], metadata
            
            except Exception as e:
                raise Exception(f"Whisper transcription failed: {str(e)}")
    
    except Exception as e:
        return "", {"error": str(e), "model": "whisper"}


# ============ GOOGLE CLOUD SPEECH-TO-TEXT ============
def transcribe_google_speech(audio_path: str, credentials_path: str = None) -> Tuple[str, Dict]:
    """Transcribe with Google Cloud Speech-to-Text API"""
    try:
        from google.cloud import speech_v1
        from google.oauth2 import service_account
        
        # Set up credentials
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            client = speech_v1.SpeechClient(credentials=credentials)
        else:
            client = speech_v1.SpeechClient()
        
        # Read audio file
        with open(audio_path, 'rb') as f:
            content = f.read()
        
        audio = speech_v1.RecognitionAudio(content=content)
        
        config = speech_v1.RecognitionConfig(
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="hi-IN",
            model="default",
        )
        
        response = client.recognize(config=config, audio=audio)
        
        # Extract transcription
        transcript = ""
        confidence = 0.0
        
        if response.results:
            for result in response.results:
                if result.alternatives:
                    transcript += result.alternatives[0].transcript
                    confidence = result.alternatives[0].confidence
        
        metadata = {
            "model": "google-cloud-speech",
            "confidence": confidence,
            "language": "hi-IN"
        }
        
        return transcript, metadata
    
    except Exception as e:
        return "", {"error": str(e), "model": "google-cloud-speech"}



# ============ UTILITY ============
def validate_audio_quality(audio_path: str) -> Dict:
    """Check audio file quality and properties"""
    try:
        import librosa
        
        y, sr = librosa.load(audio_path, sr=None)
        
        duration = librosa.get_duration(y=y, sr=sr)
        rms_energy = librosa.feature.rms(y=y).mean()
        
        return {
            "valid": True,
            "duration_seconds": duration,
            "sample_rate": sr,
            "rms_energy": float(rms_energy),
            "num_samples": len(y)
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }
