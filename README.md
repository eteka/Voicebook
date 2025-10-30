# 📖 Voicebook - Text-to-Speech Audiobook Generator

Transform your documents into high-quality audiobooks using OpenAI's Text-to-Speech API. Voicebook is designed for **cost-effective** conversion of official documents, reports, and articles into audio format for personal use.

## ✨ Features

### Phase 1 (Current Release)
- ✅ **Multiple Document Formats**: TXT, PDF, DOCX support
- ✅ **6 Premium Voices**: Choose from alloy, echo, fable, onyx, nova, and shimmer
- ✅ **Smart Caching**: Never pay twice for the same audio (95% cost savings on repeated content)
- ✅ **Cost Transparency**: See estimated costs before generating
- ✅ **Real-time Progress**: Visual feedback for long documents
- ✅ **Quality Options**: Standard and HD audio quality
- ✅ **Speed Control**: Adjust playback speed (0.25x to 4.0x)
- ✅ **Clean UI**: User-friendly Streamlit interface
- ✅ **Text Preprocessing**: Automatic cleaning of page numbers, URLs, and formatting artifacts

## 💰 Cost Optimization

Voicebook is built with cost-efficiency in mind:

- **Hash-based caching**: Identical text + voice + settings = $0 on regeneration
- **Clear cost estimates**: Know the exact cost before generating
- **Safeguards**: Confirmation required for expensive operations (>$2)
- **Usage tracking**: Monitor your spending with cache statistics

### Pricing Reference
- **Standard Quality (tts-1)**: $15.00 per 1M characters ≈ $0.75 per 10,000-word document
- **HD Quality (tts-1-hd)**: $30.00 per 1M characters ≈ $1.50 per 10,000-word document

**With caching**: After first generation, repeated audio costs **$0**!

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.9 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone or download this repository**

```bash
git clone <repository-url>
cd voicebook
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key**

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

4. **Run the application**

```bash
python run.py
```

The app will automatically open in your browser at `http://localhost:8501`

## ☁️ Cloud Deployment

**Important:** Voicebook is a Python/Streamlit application that requires a server. It **cannot run on GitHub Pages** (which only hosts static HTML files).

### Deployment Options

| Platform | Best For | Cost | Setup Time |
|----------|----------|------|------------|
| **Local** | Personal use | FREE | 5 minutes |
| **Streamlit Cloud** | Easy sharing | FREE tier | 10 minutes |
| **Railway/Render** | Custom hosting | ~$5/month | 15 minutes |

**Recommended for personal use:** Run locally with `python run.py` (simple, free, private)

**For cloud deployment:** See detailed instructions in [DEPLOYMENT.md](DEPLOYMENT.md)

### Quick Streamlit Cloud Deploy

1. Push code to GitHub
2. Sign up at https://streamlit.io/cloud
3. Create new app → Select repository → Set main file: `src/ui/app.py`
4. Add secret in dashboard: `OPENAI_API_KEY = your-key`
5. Deploy!

⚠️ **Warning:** Public deployments mean anyone can use YOUR API key. Set spending limits in OpenAI dashboard!

## 🔑 Getting an OpenAI API Key

### Step-by-Step Guide

1. **Visit OpenAI Platform**: Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

2. **Sign up or log in** to your OpenAI account

3. **Create a new API key**:
   - Click "Create new secret key"
   - Give it a name (e.g., "Voicebook")
   - Copy the key immediately (you won't see it again!)

4. **Add billing information** (if not already done):
   - Go to [Billing Settings](https://platform.openai.com/account/billing)
   - Add a payment method
   - Set a usage limit to control spending (recommended: $10-20/month for personal use)

5. **Initial credits**: New accounts often receive $5 in free credits
   - This covers approximately 330 standard-quality document conversions (10,000 words each)
   - Check your balance at [Usage Dashboard](https://platform.openai.com/account/usage)

### Cost Expectations

| Document Size | Characters | Standard Cost | HD Cost |
|--------------|------------|---------------|---------|
| Short article | 5,000 chars | ~$0.08 | ~$0.15 |
| Medium report | 25,000 chars | ~$0.38 | ~$0.75 |
| Long document | 50,000 chars | ~$0.75 | ~$1.50 |

💡 **Pro Tip**: Start with standard quality - it's excellent for most content and costs 50% less than HD.

## 📖 How to Use

### Method 1: Upload a Document

1. Start the app: `python run.py`
2. Select **"Upload Document"**
3. Choose your file (TXT, PDF, or DOCX)
4. Review the extracted text and cost estimate
5. Select voice and settings in the sidebar
6. Click **"Generate Audio"**
7. Play or download your audiobook!

### Method 2: Paste Text

1. Start the app: `python run.py`
2. Select **"Paste Text"**
3. Paste your content into the text area
4. Review cost estimate
5. Select voice and settings
6. Click **"Generate Audio"**

### Choosing a Voice

| Voice | Description | Best For |
|-------|-------------|----------|
| **nova** | Friendly and conversational | General content (recommended default) |
| **alloy** | Neutral and balanced | Any content type |
| **echo** | Clear and articulate | Technical content, tutorials |
| **fable** | Warm and expressive | Stories, narratives |
| **onyx** | Deep and authoritative | Formal documents, reports |
| **shimmer** | Smooth and professional | Business content, presentations |

## 🎛️ Settings Guide

### Voice Settings
- **Voice**: Select from 6 premium voices (see descriptions above)
- **Speed**: Adjust playback speed
  - 0.25x - 0.75x: Slower (learning, non-native speakers)
  - 1.0x: Normal speed (recommended)
  - 1.25x - 2.0x: Faster (experienced listeners, time-saving)
  - 2.0x - 4.0x: Very fast (review, skimming)

### Quality Settings
- **Standard (tts-1)**: High quality, cost-effective (recommended for most use cases)
- **HD (tts-1-hd)**: Ultra-high fidelity, 2x cost (for critical listening)

### Cost Controls
- Set `WARN_COST_THRESHOLD` in `.env` to customize warning level (default: $2.00)
- Set `MONTHLY_BUDGET_USD` to track spending (default: $50)

## 💾 Cache Management

The cache system saves you money by storing generated audio and reusing it when you generate identical content again.

### How It Works
1. Text + Voice + Speed + Quality → Unique cache key (MD5 hash)
2. First generation → Costs normal API fee, saves to cache
3. Subsequent identical requests → **$0 cost**, retrieves from cache

### Cache Statistics
View cache stats in the sidebar:
- **Cached Files**: Number of unique audio files stored
- **Cache Size**: Total disk space used
- **Cache Hits**: Number of times cache saved you money

### Managing Cache
- **Clear Cache**: Remove all cached files (use if running low on disk space)
- **Cache Location**: `./cache/` directory (can be changed in `.env`)

💡 **When cache saves money**:
- Regenerating same document with different settings → Cache miss (different parameters)
- Regenerating same document with same settings → **Cache hit ($0 cost)**
- Processing similar but slightly different text → Cache miss (different content)

## 📁 Project Structure

```
voicebook/
├── src/
│   ├── api/
│   │   └── openai_tts.py          # OpenAI TTS client
│   ├── processors/
│   │   ├── document_parser.py     # Extract text from files
│   │   └── text_cleaner.py        # Preprocess text
│   ├── cache/
│   │   └── audio_cache.py         # Caching logic
│   ├── utils/
│   │   ├── cost_calculator.py     # Cost estimation
│   │   └── validators.py          # Input validation
│   └── ui/
│       └── app.py                 # Main Streamlit UI
├── cache/                          # Cached audio files (auto-created)
├── uploads/                        # Temporary uploads (auto-created)
├── samples/                        # Sample documents
│   └── sample_document.txt        # Test document
├── .env                           # Your configuration (create this)
├── .env.example                   # Configuration template
├── requirements.txt               # Python dependencies
├── run.py                         # Quick launch script
└── README.md                      # This file
```

## 🛠️ Configuration

Edit `.env` to customize behavior:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Defaults
DEFAULT_VOICE=nova
DEFAULT_SPEED=1.0
DEFAULT_QUALITY=standard

# Limits
MAX_FILE_SIZE_MB=50
MAX_CHARACTERS=500000

# Cache
CACHE_DIRECTORY=./cache
ENABLE_CACHE=true

# Cost Controls
MONTHLY_BUDGET_USD=50
WARN_COST_THRESHOLD=2.00
```

## 🔍 Troubleshooting

### "OpenAI API key not found"
- Ensure `.env` file exists in project root
- Verify `OPENAI_API_KEY=sk-...` is set correctly
- Restart the application after editing `.env`

### "Invalid API key format"
- API keys should start with `sk-`
- Copy the entire key from OpenAI platform
- Don't include quotes in `.env` file

### "Error parsing PDF"
- Ensure PDF contains selectable text (not scanned images)
- Try copying text from PDF and using "Paste Text" method
- Check if PDF is password-protected or corrupted

### "Error parsing DOCX"
- Ensure file is valid Microsoft Word format (.docx, not .doc)
- Try saving document as .txt first
- Check if file is password-protected

### "Text too long"
- Current limit: 500,000 characters
- Split large documents into smaller parts
- Alternatively, increase `MAX_CHARACTERS` in `.env`

### High costs / Unexpected charges
- Always check cost estimate before generating
- Use cache - regenerating identical content is free
- Consider using standard quality instead of HD
- Set `WARN_COST_THRESHOLD` lower for more warnings

### Cache not working
- Verify `ENABLE_CACHE=true` in `.env`
- Check that `./cache/` directory exists and is writable
- Cache only works for **identical** text + voice + speed + quality

## 🚧 Future Enhancements (Phase 2 & 3)

### Phase 2 - Planned
- [ ] Batch processing queue
- [ ] Audio history/library view
- [ ] Advanced cache management UI
- [ ] Cost tracking dashboard
- [ ] Audio preview (first 30 seconds)
- [ ] Chapter detection and markers

### Phase 3 - Advanced
- [ ] Kokoro-82M backend integration (free, self-hosted alternative)
- [ ] Multiple format support (EPUB, HTML)
- [ ] Export with metadata
- [ ] API mode for automation
- [ ] Docker deployment option

## 💡 Tips for Best Results

### Cost Optimization
1. **Use the cache**: Regenerating with same settings is free
2. **Start with standard quality**: HD costs 2x, difference is subtle for most content
3. **Test with short excerpts first**: Validate settings before generating full documents
4. **Set spending limits**: Configure budget alerts in `.env`

### Audio Quality
1. **Clean your text**: Remove headers, footers, page numbers (done automatically)
2. **Choose appropriate voice**: Match voice to content type
3. **Adjust speed for content**: Slower for technical content, faster for familiar material
4. **Use HD selectively**: Reserve for final versions of important content

### Document Preparation
1. **TXT files work best**: Cleanest, most predictable results
2. **Export PDFs from source**: Text-based PDFs are better than scanned documents
3. **Clean up before uploading**: Remove unnecessary content to reduce costs
4. **Test with sample**: Use provided `samples/sample_document.txt` to test setup

## 📊 Sample Cost Analysis

**Scenario**: Converting 10 business reports per month

| Metric | Without Cache | With Cache (80% reuse) |
|--------|---------------|------------------------|
| Reports | 10 reports | 10 reports |
| Avg. size | 20,000 chars | 20,000 chars |
| First-time cost | $3.00 | $3.00 |
| Regeneration cost | $27.00 | $0.00 |
| **Total** | **$30.00** | **$3.00** |
| **Savings** | - | **90%** |

## 🔒 Privacy & Security

- **Local processing**: Documents are processed locally on your machine
- **No cloud storage**: Files are not stored on external servers
- **API calls only**: Only text is sent to OpenAI for audio generation
- **Cache is local**: Generated audio stored on your machine
- **Temporary uploads**: Uploaded files are deleted after processing
- **API key security**: Never commit `.env` file to version control

## 📄 License

This project is provided as-is for personal use. OpenAI TTS usage is subject to [OpenAI's Terms of Service](https://openai.com/policies/terms-of-use).

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI Text-to-Speech API](https://platform.openai.com/docs/guides/text-to-speech)
- Document parsing: [pypdf](https://github.com/py-pdf/pypdf) and [python-docx](https://python-docx.readthedocs.io/)

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review your `.env` configuration
3. Verify your OpenAI API key is valid and has billing enabled
4. Check [OpenAI Status](https://status.openai.com/) for API outages

## 🎉 Ready to Get Started?

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env with your API key

# Run the app
python run.py
```

**Happy audiobook generation!** 📖 → 🎧
