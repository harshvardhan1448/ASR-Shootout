"""
ASR Benchmark Pipeline - Deepgram vs Whisper Comparison
Evaluates multiple ASR models on Indian locality names
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Import local modules
from src.asr_models import transcribe_deepgram, transcribe_whisper, validate_audio_quality
from src.metrics import (
    compute_wer,
    compute_cer,
    extract_locality_entity,
    entity_level_accuracy,
    parse_condition_from_filename,
    parse_locality_from_filename,
    compute_metrics_per_condition,
    compute_metrics_per_locality,
)

# Load environment variables
load_dotenv()

# Configuration
RECORDINGS_DIR = Path("./recordings")
OUTPUTS_DIR = Path("./outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Models to benchmark
MODELS_TO_TEST = ["deepgram", "whisper"]  # Compare both models


class ASRBenchmark:
    def __init__(self):
        self.results = []
        self.audio_files = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def discover_audio_files(self) -> List[Path]:
        """Find all audio files in recordings directory"""
        if not RECORDINGS_DIR.exists():
            print(f"❌ Recordings directory not found: {RECORDINGS_DIR}")
            return []
        
        audio_extensions = {".wav", ".mp3", ".ogg", ".m4a", ".flac", ".mpeg", ".wav.mpeg"}
        audio_files = [
            f for f in RECORDINGS_DIR.glob("*")
            if f.suffix.lower() in audio_extensions or str(f).lower().endswith((".wav.mpeg", ".mp3.mpeg"))
        ]
        
        print(f"✓ Found {len(audio_files)} audio files")
        self.audio_files = sorted(audio_files)
        return self.audio_files
    
    def transcribe_with_model(self, audio_path: Path, model: str) -> Tuple[str, Dict]:
        """Run inference on a single audio file with specified model"""
        
        if model == "deepgram":
            print(f"  → deepgram      : ", end="", flush=True)
            try:
                if not DEEPGRAM_API_KEY:
                    raise ValueError("DEEPGRAM_API_KEY not set in .env")
                
                transcript, metadata = transcribe_deepgram(str(audio_path), DEEPGRAM_API_KEY)
                
                if "error" in metadata:
                    print(f"❌ Error: {metadata['error']}")
                    return "", metadata
                
                print(f"✓ {len(transcript)} chars")
                return transcript, metadata
            
            except Exception as e:
                print(f"❌ {str(e)[:50]}")
                return "", {"error": str(e)}
        
        elif model == "whisper":
            print(f"  → whisper       : ", end="", flush=True)
            try:
                # Use LOCAL Whisper model (free, no API key needed)
                transcript, metadata = transcribe_whisper(str(audio_path), api_key="", use_api=False)
                
                if "error" in metadata:
                    print(f"❌ Error: {metadata['error']}")
                    return "", metadata
                
                print(f"✓ {len(transcript)} chars")
                return transcript, metadata
            
            except Exception as e:
                print(f"❌ {str(e)[:50]}")
                return "", {"error": str(e)}
        
        else:
            return "", {"error": f"Unknown model: {model}"}
    
    def evaluate_audio_file(self, audio_path: Path, expected_locality: str):
        """Run all models on a single audio file and compute metrics"""
        print(f"\n📁 {audio_path.name}")
        
        # Validate audio quality
        quality = validate_audio_quality(str(audio_path))
        if not quality.get("valid"):
            print(f"  ❌ Audio validation failed: {quality.get('error')}")
            return
        
        print(f"  📊 Duration: {quality['duration_seconds']:.2f}s, Energy: {quality['rms_energy']:.4f}")
        
        # Parse metadata from filename
        condition = parse_condition_from_filename(audio_path.name)
        locality = parse_locality_from_filename(audio_path.name)
        
        # Run each model
        for model in MODELS_TO_TEST:
            transcript, metadata = self.transcribe_with_model(audio_path, model)
            
            if not transcript and "error" in metadata:
                continue
            
            # Compute metrics
            wer_score = compute_wer(expected_locality, transcript)
            cer_score = compute_cer(expected_locality, transcript)
            entity_correct = entity_level_accuracy(locality, transcript)
            
            # Store result
            result = {
                "timestamp": self.timestamp,
                "filename": audio_path.name,
                "model": model,
                "condition": condition,
                "locality": locality,
                "expected": expected_locality,
                "transcription": transcript,
                "wer": wer_score,
                "cer": cer_score,
                "entity_correct": entity_correct,
                "duration_sec": quality.get("duration_seconds"),
                **metadata
            }
            
            self.results.append(result)
            print(f"       WER: {wer_score:.2%} | CER: {cer_score:.2%} | Entity: {'✓' if entity_correct else '✗'}")
    
    def run_benchmark(self):
        """Run full benchmark pipeline"""
        print("\n" + "="*70)
        print("ASR BENCHMARK PIPELINE")
        print("="*70)
        
        # Discover files
        audio_files = self.discover_audio_files()
        if not audio_files:
            print("❌ No audio files found!")
            return
        
        # Build reference map from filenames (includes alternate spellings)
        reference_map = {
            "koramangala": "Koramangala",
            "indiranagar": "Indiranagar",
            "whitefield": "Whitefield",
            "electronic_city": "Electronic City",
            "marathahalli": "Marathahalli",
            "jayanagar": "Jayanagar",
            "rajajinagar": "Rajajinagar",
            "hebbal": "Hebbal",
            "yelahanka": "Yelahanka",
            "yellanka": "Yelahanka",  # Alternate spelling
            "banashankari": "Banashankari",
            "banashankri": "Banashankari",  # Alternate spelling
            "hsr_layout": "HSR Layout",
            "bts_layout": "BTM Layout",  # Alternate spelling
            "btm_layout": "BTM Layout",
            "majestic": "Majestic",
            "silk_board": "Silk Board",
            "bellandur": "Bellandur",
            "bellendor": "Bellandur",  # Alternate spelling
            "sarjapur": "Sarjapur",
            "bommanahalli": "Bommanahalli",
            "bommanalli": "Bommanahalli",  # Alternate spelling
            "kr_puram": "KR Puram",
            "kr_pyram": "KR Puram",  # Alternate spelling
            "peenya": "Peenya",
            "pennya": "Peenya",  # Alternate spelling
            "yeshwanthpur": "Yeshwanthpur",
            "yashvantpuram": "Yeshwanthpur"  # Alternate spelling
        }
        
        # Process each audio file
        for i, audio_path in enumerate(audio_files, 1):
            locality = parse_locality_from_filename(audio_path.name)
            expected = reference_map.get(locality, locality.title())
            
            print(f"\n[{i}/{len(audio_files)}] Processing: {audio_path.name}")
            self.evaluate_audio_file(audio_path, expected)
        
        print("\n" + "="*70)
        print("BENCHMARK COMPLETE")
        print("="*70)
    
    def save_results(self):
        """Save results to CSV and JSON"""
        if not self.results:
            print("⚠ No results to save")
            return
        
        # Save to CSV
        csv_path = OUTPUTS_DIR / f"benchmark_results_{self.timestamp}.csv"
        df = pd.DataFrame(self.results)
        df.to_csv(csv_path, index=False)
        print(f"\n✓ Results saved to: {csv_path}")
        
        # Save to JSON (for detailed metadata)
        json_path = OUTPUTS_DIR / f"benchmark_results_{self.timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"✓ Details saved to: {json_path}")
        
        return csv_path, json_path
    
    def generate_summary(self):
        """Generate summary statistics and analysis"""
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
        
        print("\n" + "="*70)
        print("SUMMARY STATISTICS")
        print("="*70)
        
        # Deepgram Stats
        model_data = df[df["model"] == "deepgram-nova-2"]
        if len(model_data) > 0:
            avg_wer = model_data["wer"].mean()
            avg_cer = model_data["cer"].mean()
            entity_acc = (model_data["entity_correct"].sum() / len(model_data)) * 100
            
            print(f"\n📊 DEEPGRAM NOVA-2 PERFORMANCE:")
            print(f"    Avg WER:        {avg_wer:.2%}")
            print(f"    Avg CER:        {avg_cer:.2%}")
            print(f"    Entity Accuracy: {entity_acc:.1f}%")
        
        # By Condition
        print("\n\n📊 METRICS BY AUDIO CONDITION:")
        condition_metrics = compute_metrics_per_condition(self.results)
        for condition, metrics in sorted(condition_metrics.items()):
            print(f"\n  {condition.upper()}:")
            print(f"    Avg WER:        {metrics['avg_wer']:.2%}")
            print(f"    Avg CER:        {metrics['avg_cer']:.2%}")
            print(f"    Entity Accuracy: {metrics['entity_accuracy']:.1f}%")
        
        # Worst performers
        print("\n\n❌ WORST PERFORMING SAMPLES (Top 5):")
        worst = sorted(self.results, key=lambda x: x["wer"], reverse=True)[:5]
        for i, w in enumerate(worst, 1):
            print(f"\n{i}. {w['filename']:40s}")
            print(f"   Condition: {w['condition']:8s} | WER: {w['wer']:.0%}")
            print(f"   Expected: '{w['expected']}'")
            print(f"   Got:      '{w['transcription'][:70]}'...")
    
    def generate_comparison_table(self):
        """Generate comparison table for report"""
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
        
        # Deepgram stats
        model_data = df[df["model"] == "deepgram-nova-2"]
        if len(model_data) > 0:
            comparison = [{
                "Model": "DEEPGRAM-NOVA-2",
                "Samples": len(model_data),
                "Avg WER": f"{model_data['wer'].mean():.2%}",
                "Avg CER": f"{model_data['cer'].mean():.2%}",
                "Entity Accuracy": f"{(model_data['entity_correct'].sum() / len(model_data)) * 100:.1f}%",
            }]
        
            comp_df = pd.DataFrame(comparison)
            table_path = OUTPUTS_DIR / f"comparison_table_{self.timestamp}.csv"
            comp_df.to_csv(table_path, index=False)
            print(f"\n✓ Comparison table saved to: {table_path}")
            
            print("\n" + "="*70)
            print("DEEPGRAM PERFORMANCE SUMMARY")
            print("="*70)
            print(comp_df.to_string(index=False))


def main():
    benchmark = ASRBenchmark()
    
    # Run benchmark
    benchmark.run_benchmark()
    
    # Generate summary
    benchmark.generate_summary()
    
    # Save results
    benchmark.save_results()
    
    # Generate comparison table
    benchmark.generate_comparison_table()
    
    print("\n✅ Benchmark pipeline completed!")


if __name__ == "__main__":
    main()
