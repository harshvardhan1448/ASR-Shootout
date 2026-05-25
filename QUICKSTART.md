# ASR Benchmark - Quick Start

## 🎬 RIGHT NOW (You're here!)

Your Python pipeline is **ready to run**. All code is written, tested, and documented.

---

## 📋 YOUR TASK: Record 20 Audio Files (~1-2 hours)

### Setup (2 min)
1. Open Voice Memos (iPhone) or Recorder (Android)
2. Move to `Project_Audio/recordings/` folder on your computer - you'll save files here

### Recording Script (20 audio files = 20 localities)

For each locality, record naturally in Hindi/Hinglish:
```
"Main [locality] mein rehta hoon" 
or 
"[Locality], haan wo area hai"
```

**Localities (20 total):**
```
1. Koramangala      11. HSR Layout
2. Indiranagar      12. BTM Layout
3. Whitefield       13. Majestic
4. Electronic City  14. Silk Board
5. Marathahalli     15. Bellandur
6. Jayanagar        16. Sarjapur
7. Rajajinagar      17. Bommanahalli
8. Hebbal           18. KR Puram
9. Yelahanka        19. Peenya
10. Banashankari    20. Yeshwanthpur
```

### Recording Conditions (5 each = 20 total)

- **5 Quiet**: Normal room, clean audio
- **5 Noisy**: Street/traffic noise (play YouTube traffic sounds in background)
- **5 Rushed**: Fast/hurried speech ("I'm in a hurry")
- **5 Phone**: Simulate phone call (lower volume, muffled)

### File Naming (CRITICAL!)
```
locality_condition_number.wav

Examples:
koramangala_quiet_01.wav
indiranagar_noisy_02.wav
whitefield_rushed_03.wav
electronic_city_phone_04.wav
marathahalli_quiet_05.wav
```

---

## ⚙️ SETUP PHASE (After Recording)

### Step 1: Install Dependencies (2 min)
```bash
cd Project_Audio
pip install -r requirements.txt
```

### Step 2: Get API Keys (5 min, free tier)

**Deepgram** (free tier: 50k min/month):
1. Go to https://console.deepgram.com/
2. Sign up → API Keys
3. Copy your API key

**OpenAI/Whisper** (optional - local Whisper works free):
- Already have OpenAI API key? Use it
- Otherwise, local Whisper runs free (no API key needed)

**Google Cloud** (optional - free tier has limits):
- Only if you have budget or free trial credits
- Otherwise skip it

### Step 3: Configure `.env` (2 min)
```bash
cp .env.template .env
```

Edit `.env` and add your keys:
```
DEEPGRAM_API_KEY=sk_...
OPENAI_API_KEY=sk-... (or leave empty for local Whisper)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json (or leave empty to skip)
```

---

## 🚀 RUN THE BENCHMARK (5 min)

```bash
python asr_benchmark.py
```

That's it! The script will:
✓ Load your 20 audio files
✓ Send each to Deepgram + Whisper (+ Google if configured)
✓ Compute accuracy metrics
✓ Generate comparison tables
✓ Save everything to `./outputs/`

---

## 📊 ANALYZE RESULTS (30 min)

Check `./outputs/`:

```
benchmark_results_YYYYMMDD_HHMMSS.csv    ← Detailed results (open in Excel)
comparison_table_YYYYMMDD_HHMMSS.csv     ← Quick model comparison
```

Look for:
- Which model has lowest WER?
- Which condition (quiet/noisy/rushed/phone) is hardest?
- Which localities are commonly misrecognized?
- Failure examples (transcriptions gone wrong)

---

## 📝 WRITE REPORT (Day 3, 2 hours)

Max 3 pages. Sections:

1. **Approach** (0.5 page)
   - Why these models? Why these metrics?
   - Data collection methodology

2. **Findings** (1 page)
   - Summary table (all models vs each other)
   - Metrics by condition
   - Metrics by locality

3. **Failure Analysis** (0.5 page)
   - 3-5 worst cases with actual transcriptions
   - What caused failures? (noise, accent, speed?)

4. **Recommendation** (0.5 page)
   - Which model for which scenario?
   - What are the tradeoffs?

---

## 🎯 Timeline

- **Today (Day 1)**: Record 20 audio files (~1-2 hours)
- **Day 2**: Setup environment → Run benchmark → Review outputs
- **Day 3**: Failure analysis + Report writing

---

## ✅ CHECKLIST

Before recording:
- [ ] Understand the 20 localities
- [ ] Know the sentence structure ("Main [locality] mein rehta hoon")
- [ ] Have your phone + recorder app ready
- [ ] Plan conditions: quiet room, outdoor/traffic, rushed tone, phone simulation

After recording:
- [ ] All 20 files named correctly in `./recordings/`
- [ ] `.env` configured with API keys
- [ ] Run: `pip install -r requirements.txt`
- [ ] Run: `python asr_benchmark.py`
- [ ] Check `./outputs/` for results

---

## ❓ FAQ

**Q: Can I use Whisper only (no Deepgram)?**
A: Yes! Leave `DEEPGRAM_API_KEY` empty. Update `MODELS_TO_TEST` in `asr_benchmark.py`.

**Q: How much will this cost?**
A: 
- Deepgram free tier: 50k min/month (20 files = ~5 min, well under limit)
- Whisper (local): FREE
- Google Cloud: Only if you configure it, otherwise skipped

**Q: My audio files are in `.mp3` format, not `.wav`**
A: The script supports `.wav`, `.mp3`, `.ogg`, `.m4a`, `.flac`. You're good!

**Q: I only have 10 audio files, not 20. Is that OK?**
A: Yes, the assessment values quality over quantity. 10 well-varied files > 20 identical ones.

**Q: What if I don't have a Deepgram/Google API key?**
A: Use just Whisper. Comment out "deepgram" and "google" from `MODELS_TO_TEST` in `asr_benchmark.py`.

---

## 🎬 START NOW

**Right now:** Go record your first audio file. Say "Main Koramangala mein rehta hoon" naturally.

Estimated timeline:
- Recording: 1-2 hours
- Setup: 10 minutes
- Benchmark run: 5 minutes
- Analysis: 30 minutes
- Report: 2 hours

**Total: ~4-5 hours over 3 days**

You've got this! 🚀
