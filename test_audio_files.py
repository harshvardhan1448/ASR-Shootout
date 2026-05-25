"""
Quick test to verify audio files can be loaded
"""

import sys
from pathlib import Path
from src.asr_models import validate_audio_quality

recordings_dir = Path("./recordings")
audio_files = sorted([f for f in recordings_dir.glob("*") if str(f).lower().endswith((".wav", ".mp3", ".mpeg", ".wav.mpeg"))])

print(f"Found {len(audio_files)} audio files\n")
print("Testing file loading...")
print("-" * 70)

valid_count = 0
failed_files = []

for i, audio_file in enumerate(audio_files, 1):
    quality = validate_audio_quality(str(audio_file))
    
    if quality.get("valid"):
        print(f"✓ {audio_file.name:40s} {quality['duration_seconds']:6.2f}s")
        valid_count += 1
    else:
        print(f"✗ {audio_file.name:40s} Error: {quality.get('error')[:40]}")
        failed_files.append(audio_file.name)

print("-" * 70)
print(f"\n✅ Valid files: {valid_count}/{len(audio_files)}")

if failed_files:
    print(f"\n❌ Failed to load ({len(failed_files)}):")
    for f in failed_files:
        print(f"  - {f}")
    print("\n⚠️  You may need to convert these files to standard WAV format.")
    print("   Tip: Use FFmpeg to convert: ffmpeg -i file.wav.mpeg -acodec pcm_s16le -ar 16000 file.wav")
else:
    print("\n✅ All files ready for benchmarking!")
