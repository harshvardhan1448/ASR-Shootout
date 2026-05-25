# ASR Benchmark for Indian Conversational Speech

Evaluate multiple Automatic Speech Recognition (ASR) systems on Bangalore locality names recorded in real-world conditions.

## Project Structure

```
Project_Audio/
├── recordings/              # Your 20 audio files go here
├── outputs/                 # Results, CSVs, and analysis
├── src/
│   ├── asr_models.py       # API integrations (Deepgram, Whisper, Google)
│   └── metrics.py          # Evaluation metrics (WER, CER, Entity Accuracy)
├── asr_benchmark.py        # Main pipeline
├── requirements.txt        # Python dependencies
├── .env.template          # Copy to .env and add your API keys
└── README.md              # This file
```

## Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Copy `.env.template` to `.env` and fill in your credentials:

```bash
cp .env.template .env
```

Edit `.env`:
```
DEEPGRAM_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

**Get your API keys:**
- **Deepgram**: Sign up at https://console.deepgram.com → API Keys section (free tier: 50k minutes/month)
- **OpenAI**: Already have this? Use `OPENAI_API_KEY` from your account. Otherwise, local Whisper works free.
- **Google Cloud**: Download credentials JSON from Google Cloud Console (optional)

### 3. Prepare Audio Files
Record your 20 audio files and save them to `./recordings/` with this naming convention:

```
locality_condition_number.wav
```

Example:
```
koramangala_quiet_01.wav
indiranagar_noisy_02.wav
whitefield_rushed_03.wav
electronic_city_phone_04.wav
...
```

**Conditions:**
- `quiet`: Normal room, no background noise
- `noisy`: Street/traffic noise in background
- `rushed`: Fast/hurried speech
- `phone`: Simulated phone call quality

## Running the Benchmark

```bash
python asr_benchmark.py
```

This will:
1. ✓ Discover all audio files in `./recordings/`
2. ✓ Send each to Deepgram, Whisper, and Google Cloud Speech-to-Text
3. ✓ Compute Word Error Rate (WER), Character Error Rate (CER), and Entity-level accuracy
4. ✓ Analyze failures by condition and locality
5. ✓ Save results to `./outputs/`

## Output Files

After running, check `./outputs/`:

```
benchmark_results_YYYYMMDD_HHMMSS.csv     # Detailed results (one row per sample × model)
benchmark_results_YYYYMMDD_HHMMSS.json    # Full metadata and transcriptions
comparison_table_YYYYMMDD_HHMMSS.csv      # Summary comparison across models
```

## Metrics Explained

- **WER (Word Error Rate)**: % of words that differ between expected and transcribed text
  - Lower is better. 0% = perfect, 100% = completely wrong.
  
- **CER (Character Error Rate)**: % of characters that differ
  - Similar to WER but at character level. More sensitive to accent variations.

- **Entity Accuracy**: % of samples where the correct locality name was extracted
  - Binary: 1 if correct, 0 if missed. Most important metric for your hiring platform.

## Model Selection Rationale

### Deepgram (Baseline)
- Fast, real-time conversational speech focused
- Good for noisy environments
- Free tier: 50k minutes/month
- API-based (cloud)

### OpenAI Whisper
- Free local option (no API costs)
- Multilingual, handles code-switching well
- Slower than Deepgram but works offline
- Baseline: `base` model

### Google Cloud Speech-to-Text
- Strong on accented speech
- Supports Indian English and Hindi
- More expensive but highest accuracy
- Optional if budget allows

## Testing Tips

**Fast validation run (5 files instead of 20):**
```bash
# Copy only 5 audio files to ./recordings/
# Run the benchmark - should complete in ~2 minutes
```

**Local Whisper only (free, no API needed):**
```bash
# Leave DEEPGRAM_API_KEY and GOOGLE_CREDENTIALS empty in .env
# Set OPENAI_API_KEY empty as well (forces local Whisper)
# Run: python asr_benchmark.py
```

**Debug single file:**
```python
from src.asr_models import transcribe_whisper
from src.metrics import compute_wer

transcript, meta = transcribe_whisper("./recordings/koramangala_quiet_01.wav", "")
wer = compute_wer("Koramangala", transcript)
print(f"Transcript: {transcript}")
print(f"WER: {wer:.2%}")
```

## Troubleshooting

**"DEEPGRAM_API_KEY not set"**
- Add `DEEPGRAM_API_KEY=...` to `.env`
- Or comment out "deepgram" from `MODELS_TO_TEST` in `asr_benchmark.py`

**"ModuleNotFoundError: No module named 'deepgram'"**
- Run: `pip install deepgram-sdk`

**API quota exceeded**
- Deepgram: Free tier = 50k minutes/month. Switch to local Whisper.
- Google: May require paid account for speech-to-text. Consider Deepgram free tier instead.

**Audio files not found**
- Ensure files are in `./recordings/` (exact folder name)
- Use `.wav`, `.mp3`, `.ogg`, `.m4a`, or `.flac` extensions

**Slow performance**
- Deepgram should be <5 sec per file over internet
- Whisper: `base` model ~10-15 sec per file locally
- If too slow, try Deepgram API instead of local Whisper

## Analysis for Your Report

The outputs give you raw data. For your 3-page report, focus on:

1. **Model Selection**: Why Deepgram + Whisper + Google?
2. **Key Findings**: 
   - Which model performed best overall?
   - Entity accuracy by condition (quiet vs noisy)?
   - Which localities are hardest to recognize?
3. **Failure Analysis**: Show 3-5 worst cases with transcriptions
4. **Recommendation**: Under what constraints would you pick which model?

Example insights to dig into:
- Does Deepgram's real-time focus help with conversational speech?
- How much do phone conditions degrade accuracy?
- Are certain localities systematically misrecognized?

## Tips for Strong Results

✓ Varied recordings (5 quiet, 5 noisy, 5 rushed, 5 phone calls)
✓ Natural speech (conversational, not robotic)
✓ Use phone mic (not studio-quality)
✓ Multiple models compared fairly
✓ Analyze failures, not just aggregate scores
✓ Acknowledge limitations (e.g., "Google was too expensive to fully test")

## Next Steps

1. Record 20 audio files (~1-2 hours)
2. Add API keys to `.env` (~2 minutes)
3. Run benchmark (~5-10 minutes depending on models + internet)
4. Review `outputs/` CSVs (~10 minutes)
5. Write report and identify top 3-5 insights (~2 hours)

---

Questions? The assessment values your ability to make reasonable decisions under ambiguity. Don't over-engineer—aim for clarity and thoughtful choices.

Good luck! 🎙️
