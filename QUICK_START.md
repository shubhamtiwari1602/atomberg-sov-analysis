# Quick Start Guide

## 🚀 How to Run the Atomberg SoV Analysis

### Option 1: Standalone Demo (No Dependencies)
```bash
# Run the working demo
python3 standalone_demo.py
```

### Option 2: Full System (With API Keys)
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export YOUTUBE_API_KEY="your_youtube_api_key"
export TWITTER_BEARER_TOKEN="your_twitter_bearer_token"

# Run full analysis
python3 main.py --keywords "smart fan" --platforms youtube,twitter,google --results 50
```

### Option 3: Custom Analysis
```bash
# Analyze multiple keywords
python3 main.py --keywords "smart fan,IoT fan,BLDC fan" --platforms all --results 100

# Analyze specific platform
python3 main.py --keywords "smart ceiling fan" --platforms youtube --results 30
```

## 📊 Output Files

After running the analysis, check these directories:
- `data/` - Raw analysis data (JSON format)
- `reports/` - Generated reports and charts
- `ATOMBERG_SOV_REPORT.md` - Main findings document

## 🔧 Configuration

Edit `config/settings.py` to customize:
- Competitor brands to track
- Analysis parameters
- API settings
- Output preferences

## 📈 Understanding Results

Key metrics in the output:
- **Overall SoV**: Atomberg's share of brand conversations
- **Platform Breakdown**: Performance by platform
- **Sentiment Analysis**: Positive vs negative mentions
- **Engagement Metrics**: Interaction rates and reach

## 🎯 Key Findings from Demo

The demo analysis shows:
- Atomberg has **44.16% Share of Voice** (strong performance)
- **Twitter is the best platform** (64.3% SoV)
- **22 out of 30 posts** mention Atomberg
- Positive brand sentiment overall

## 📞 Next Steps

1. Set up real API keys for live data
2. Run analysis with broader keyword sets
3. Schedule regular monitoring
4. Implement recommendations from the report
