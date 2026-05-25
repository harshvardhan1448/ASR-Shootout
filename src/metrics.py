"""
Evaluation metrics for ASR benchmarking
- WER (Word Error Rate)
- Entity-level accuracy for locality names
- Condition-based analysis
"""

import numpy as np
from jiwer import wer, cer
from typing import Dict, List, Tuple
import re

# Bangalore localities (English romanization)
LOCALITIES = {
    "koramangala", "indiranagar", "whitefield", "electronic city", "marathahalli",
    "jayanagar", "rajajinagar", "hebbal", "yelahanka", "banashankari",
    "hsr layout", "btm layout", "majestic", "silk board", "bellandur",
    "sarjapur", "bommanahalli", "kr puram", "peenya", "yeshwanthpur"
}

# Hindi to English locality mapping (Devanagari script to romanization)
HINDI_TO_ENGLISH = {
    # Exact Hindi spellings from transcriptions
    "बनाशंकरी": "banashankari",
    "बेलंदूर": "bellandur",
    "बोम्मनहल्ली": "bommanahalli",
    "इंदिरा नगर": "indiranagar",
    "जयनगर": "jayanagar",
    "कोरामंगला": "koramangala",
    "व्हाइटफील्ड": "whitefield",
    "मैराथाहल्ली": "marathahalli",
    "हैबल": "hebbal",
    "येलहंका": "yelahanka",
    "एचएसआर": "hsr",
    "बीटीएम": "btm",
    "मैजेस्टिक": "majestic",
    "सिल्क बोर्ड": "silk board",
    "सरजापुर": "sarjapur",
    "केआर": "kr",
    "पीनिया": "peenya",
    "यशवंतपुर": "yeshwanthpur",
    "राजा जिनगर": "rajajinagar",
    # Variant spellings found in transcriptions
    "white field": "whitefield",
    "jaya nagar": "jayanagar",
    "जया नगर": "jayanagar",
    "baiendoor": "bellandur",  # Deepgram spelling variant
    "btm": "btm layout",
    "हsr": "hsr layout",
    "राजा": "rajajinagar",  # Partial Hindi word
}

def compute_wer(reference: str, hypothesis: str) -> float:
    """Compute Word Error Rate"""
    ref = reference.lower().strip()
    hyp = hypothesis.lower().strip()
    return wer(ref, hyp)

def compute_cer(reference: str, hypothesis: str) -> float:
    """Compute Character Error Rate"""
    ref = reference.lower().strip()
    hyp = hypothesis.lower().strip()
    return cer(ref, hyp)

def extract_locality_entity(text: str) -> str:
    """Extract locality name from transcription
    
    Handles:
    - Case-insensitive matching
    - Hindi (Devanagari script) locality names
    - Multi-word localities like "silk board", "electronic city"
    - Transcription variants and Deepgram spelling differences
    """
    text_lower = text.lower()
    text_no_spaces = text_lower.replace(" ", "").replace("_", "")
    
    # Strategy 1: Try Hindi→English mapped words first
    for hindi, english in HINDI_TO_ENGLISH.items():
        if hindi in text:  # Hindi text is case-sensitive, don't lowercase
            return english
    
    # Strategy 1b: Try English variants (lowercase)
    for english_variant in ["baiendoor"]:
        if english_variant in text_lower:
            if english_variant == "baiendoor":
                return "bellandur"
    
    # Strategy 2: Try to find COMPLETE multi-word localities first
    for locality in LOCALITIES:
        if " " in locality:  # Multi-word locality like "silk board"
            phrase_normalized = locality.replace(" ", "")
            if phrase_normalized in text_no_spaces:
                return locality
            if locality in text_lower:
                return locality
    
    # Strategy 3: Exact substring match (case-insensitive, space-normalized)
    for locality in LOCALITIES:
        locality_normalized = locality.replace(" ", "")
        if locality_normalized in text_no_spaces:
            return locality
    
    # Strategy 4: Look for first word of multi-word localities
    text_words = text_lower.split()
    for locality in LOCALITIES:
        if " " in locality:
            words = locality.split()
            for word in words:
                if word in text_words:
                    return locality  # Return full multi-word locality
    
    # Strategy 5: Look for locality within first 15 words
    words = text_lower.split()[:15]
    for locality in LOCALITIES:
        locality_words = locality.split()
        
        # Try consecutive word sequences
        for i in range(len(words) - len(locality_words) + 1):
            candidate = " ".join(words[i:i+len(locality_words)])
            if candidate.replace(" ", "") == locality.replace(" ", ""):
                return locality
    
    # Strategy 6: Partial word matching
    for text_word in words:
        for locality in LOCALITIES:
            locality_words = locality.split()
            for loc_word in locality_words:
                loc_normalized = loc_word.replace(" ", "")
                word_normalized = text_word.replace(" ", "")
                
                if len(loc_normalized) >= 4 and len(word_normalized) >= 4:
                    overlap = sum(1 for c in loc_normalized if c in word_normalized)
                    if overlap / len(loc_normalized) > 0.6:
                        return locality
    
    return ""

def entity_level_accuracy(reference_locality: str, hypothesis_text: str) -> bool:
    """Check if the correct locality was extracted from hypothesis
    
    reference_locality: What we expect (from reference_map, e.g., "Electronic City", "Bellandur")
    hypothesis_text: Full transcription from Deepgram
    
    Returns True if locality is correctly identified in the transcription
    """
    extracted = extract_locality_entity(hypothesis_text)
    reference_lower = reference_locality.lower()
    
    # Normalize both for comparison
    # Remove spaces for matching (e.g., "electronic city" vs "electroniccity")
    ref_normalized = reference_lower.replace(" ", "")
    ext_normalized = extracted.replace(" ", "")
    
    # Strategy 1: Exact match
    if ext_normalized == ref_normalized:
        return True
    
    # Strategy 2: Reference word appears in extracted  
    # e.g., "electronic" matches "electronic city"
    ref_words = reference_lower.split()
    ext_words = extracted.split()
    
    # If extracted is a substring of reference or vice versa
    if any(ref_word in extracted for ref_word in ref_words):
        return True
    if any(ext_word in reference_lower for ext_word in ext_words):
        return True
    
    # Strategy 3: Both contain the same main locality word
    # e.g., both mention "koramangala"
    for ref_word in ref_words:
        for ext_word in ext_words:
            if len(ref_word) >= 4 and len(ext_word) >= 4:
                # Partial character match
                overlap = sum(1 for c in ref_word if c in ext_word)
                if overlap / len(ref_word) > 0.7:
                    return True
    
    return False

def parse_condition_from_filename(filename: str) -> str:
    """Extract condition from filename: locality_condition_number.wav"""
    parts = filename.replace(".wav", "").replace(".mp3", "").split("_")
    if len(parts) >= 2:
        return parts[-2]  # Return condition (quiet, noisy, rushed, phone)
    return "unknown"

def parse_locality_from_filename(filename: str) -> str:
    """Extract locality from filename"""
    parts = filename.replace(".wav", "").replace(".mp3", "").replace(".mpeg", "").replace(".wav.mpeg", "").split("_")
    if parts:
        return parts[0].lower()
    return "unknown"

def compute_metrics_per_condition(results: List[Dict]) -> Dict[str, Dict]:
    """Aggregate metrics by audio condition"""
    condition_metrics = {}
    
    for result in results:
        condition = result.get("condition", "unknown")
        if condition not in condition_metrics:
            condition_metrics[condition] = {
                "wer_scores": [],
                "cer_scores": [],
                "entity_correct": [],
                "count": 0
            }
        
        condition_metrics[condition]["wer_scores"].append(result.get("wer", 1.0))
        condition_metrics[condition]["cer_scores"].append(result.get("cer", 1.0))
        condition_metrics[condition]["entity_correct"].append(result.get("entity_correct", False))
        condition_metrics[condition]["count"] += 1
    
    # Compute aggregates
    aggregated = {}
    for condition, metrics in condition_metrics.items():
        aggregated[condition] = {
            "avg_wer": np.mean(metrics["wer_scores"]),
            "avg_cer": np.mean(metrics["cer_scores"]),
            "entity_accuracy": np.mean(metrics["entity_correct"]) * 100,
            "count": metrics["count"]
        }
    
    return aggregated

def compute_metrics_per_locality(results: List[Dict]) -> Dict[str, Dict]:
    """Aggregate metrics by locality"""
    locality_metrics = {}
    
    for result in results:
        locality = result.get("locality", "unknown")
        if locality not in locality_metrics:
            locality_metrics[locality] = {
                "wer_scores": [],
                "cer_scores": [],
                "entity_correct": [],
                "count": 0
            }
        
        locality_metrics[locality]["wer_scores"].append(result.get("wer", 1.0))
        locality_metrics[locality]["cer_scores"].append(result.get("cer", 1.0))
        locality_metrics[locality]["entity_correct"].append(result.get("entity_correct", False))
        locality_metrics[locality]["count"] += 1
    
    # Compute aggregates
    aggregated = {}
    for locality, metrics in locality_metrics.items():
        aggregated[locality] = {
            "avg_wer": np.mean(metrics["wer_scores"]),
            "avg_cer": np.mean(metrics["cer_scores"]),
            "entity_accuracy": np.mean(metrics["entity_correct"]) * 100,
            "count": metrics["count"]
        }
    
    return aggregated

def find_worst_performers(results: List[Dict], model: str, top_n: int = 5) -> List[Dict]:
    """Find top N worst performing samples for a model"""
    model_results = [r for r in results if r.get("model") == model]
    sorted_results = sorted(model_results, key=lambda x: x.get("wer", 1.0), reverse=True)
    return sorted_results[:top_n]
