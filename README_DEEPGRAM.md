# ASR Benchmark - Deepgram Nova-2 Only

Evaluate Deepgram Nova-2 on 20 Bangalore locality names recorded in real-world conditions.

## ⚡ Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Deepgram API Key
- Go to: https://console.deepgram.com/
- Sign up → Copy API key
- Free tier: 50k minutes/month (more than enough for this task)

### 3. Configure Key
```bash
cp .env.template .env
```

Edit `.env` and add your key:
```
DEEPGRAM_API_KEY=sk_your_key_here_12345
```

### 4. Run Benchmark
```bash
python asr_benchmark.py
```

**Time to complete:** ~2-3 minutes

## 📊 What You Get

After running, check `./outputs/`:

- `benchmark_results_*.csv` - All 20 transcriptions + metrics
- `comparison_table_*.csv` - Performance summary
- `failure_analysis.txt` - Detailed error cases
- PNG charts (condition analysis, locality difficulty, etc.)

## 📈 Metrics

- **WER**: Word Error Rate (% of words wrong)
- **CER**: Character Error Rate (% of characters wrong)  
- **Entity Accuracy**: Did we extract the correct locality? (most important for your platform)

## 🎯 For Your Report

1. **Performance:** Average WER, CER, Entity Accuracy across all 20 files
2. **By Condition:** How does noise/rushed speech/phone quality affect accuracy?
3. **Failure Analysis:** Show 3-5 actual transcriptions that went wrong
4. **Recommendation:** Is Deepgram good enough for your hiring platform?

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "DEEPGRAM_API_KEY not set" | Add key to `.env` file |
| "Audio files not found" | Put files in `./recordings/` folder |
| "API quota exceeded" | Deepgram free tier = 50k min/month (you have ~20 min of audio, so you're fine) |

## 📁 File Structure

```
Project_Audio/
├── asr_benchmark.py          # Main pipeline (run this)
├── analyze_results.py        # Generate charts & analysis
├── src/
│   ├── asr_models.py         # Deepgram API
│   ├── metrics.py            # WER, CER, Entity Accuracy
│   └── __init__.py
├── requirements.txt          # Dependencies
├── .env.template             # Config template
├── recordings/               # Your 20 audio files
└── outputs/                  # Results
```

---

**That's it!** Record your 20 audio files, add your API key, and run the benchmark. Your results will be ready in minutes.
