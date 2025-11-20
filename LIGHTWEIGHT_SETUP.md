# 🪶 Voicebook - Lightweight Setup Guide

**Perfect for systems with limited resources!**

No Docker required - run Voicebook directly with Python for minimal resource usage.

---

## 📊 Resource Comparison

| Method | RAM Usage | Disk Space | Startup Time | Best For |
|--------|-----------|------------|--------------|----------|
| **Native Python** | ~200-500 MB | ~500 MB | ~5 seconds | Low-resource systems, development |
| Docker | ~1-2 GB | ~2 GB | ~15 seconds | Consistency, deployment |
| Docker Compose | ~2-4 GB | ~3 GB | ~20 seconds | Multi-service apps |
| Kubernetes | ~4-8 GB | ~5 GB | ~60 seconds | Production, scaling |

✅ **Recommended: Native Python** for your use case

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- **Python 3.9+** ([Download Python](https://www.python.org/downloads/))
- **pip** (included with Python)
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### Step 1: Clone Repository

```bash
git clone https://github.com/eteka/Voicebook.git
cd Voicebook
```

### Step 2: Run Automated Setup

We've created a script that does everything for you:

```bash
chmod +x setup-dev.sh
./setup-dev.sh
```

This script will:
- ✅ Check Python version
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Copy .env.example to .env
- ✅ Run tests
- ✅ Validate setup

**That's it!** Skip to Step 6 if the script succeeds.

---

## 🛠️ Manual Setup (If Script Fails)

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Optional: Install development tools (for testing)
pip install -r requirements-dev.txt
```

### Step 5: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use any text editor
```

Add your API key:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

### Step 6: Run Application

```bash
streamlit run src/ui/app.py
```

**Access:** http://localhost:8501

---

## 🧪 Testing Without Docker

### Run All Tests

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Run tests
pytest tests/
```

### Run Specific Test Suites

```bash
# Unit tests only (fast)
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage report
pytest tests/ --cov=src --cov-report=html

# View coverage
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

### Quick Validation

```bash
# Run our lightweight validation script
chmod +x test-local.sh
./test-local.sh
```

---

## 📁 What Gets Installed?

### Directory Structure

```
Voicebook/
├── venv/                 # Virtual environment (~200 MB)
│   ├── bin/              # Python executables
│   └── lib/              # Installed packages
├── cache/                # Audio cache (grows with use)
│   └── audio_cache.json  # Cache metadata
├── src/                  # Application source code
│   ├── api/              # OpenAI API wrapper
│   ├── cache/            # Caching logic
│   ├── processors/       # Document processing
│   ├── ui/               # Streamlit interface
│   └── utils/            # Utilities
└── tests/                # Test suite
```

### Disk Space Requirements

- **Base Installation:** ~500 MB
  - Python packages: ~300 MB
  - Source code: ~10 MB
  - Virtual environment: ~200 MB

- **Runtime:**
  - Cache grows with usage (~1-5 MB per audiobook)
  - Logs: minimal (~1-10 MB)

---

## 🎯 Daily Workflow

### Starting Development

```bash
# 1. Navigate to project
cd Voicebook

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run application
streamlit run src/ui/app.py
```

### Stopping Application

- Press **Ctrl+C** in terminal
- Or close the terminal window

### Deactivating Virtual Environment

```bash
deactivate
```

---

## 🔧 Development Tools

### Code Formatting

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/
```

### Code Quality Checks

```bash
# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/

# Security scan
bandit -r src/
```

### Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## 📊 Monitor Resource Usage

### Check Memory Usage

**Linux/Mac:**
```bash
# While app is running
ps aux | grep streamlit
```

**Windows:**
```powershell
# Task Manager
# Look for "Python" processes
```

### Typical Resource Usage

- **Idle:** ~150-200 MB RAM
- **Processing Document:** ~300-400 MB RAM
- **Generating Audio:** ~400-500 MB RAM
- **CPU:** 5-20% (single core)

### Reduce Resource Usage

1. **Close browser tabs** you're not using
2. **Clear cache** periodically:
   ```bash
   rm -rf cache/*
   ```
3. **Reduce concurrent processes**:
   - Don't generate multiple audiobooks simultaneously
4. **Use Standard quality** instead of HD (uses less API bandwidth)

---

## 🐛 Troubleshooting

### Issue: "Python not found"

**Solution:**
```bash
# Install Python 3.9+
# Linux:
sudo apt-get install python3 python3-pip python3-venv

# Mac:
brew install python@3.11

# Windows:
# Download from https://www.python.org/downloads/
```

### Issue: "pip install fails"

**Solution:**
```bash
# Upgrade pip
python3 -m pip install --upgrade pip

# Try again
pip install -r requirements.txt
```

### Issue: "Module not found"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port 8501 already in use"

**Solution:**
```bash
# Use different port
streamlit run src/ui/app.py --server.port 8502

# Access: http://localhost:8502
```

### Issue: "Application is slow"

**Possible causes:**
1. **Slow internet:** Audio generation requires API calls
2. **Large document:** Break into smaller chunks
3. **Low memory:** Close other applications
4. **Old Python version:** Upgrade to Python 3.11+

**Solutions:**
```bash
# Check Python version
python3 --version

# Monitor memory
top  # Linux/Mac
# Look for Python process

# Clear cache
rm -rf cache/*
```

### Issue: "Tests failing"

**Solution:**
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests with verbose output
pytest tests/ -v

# Run specific test
pytest tests/unit/test_validators.py -v
```

---

## 🔒 Security Best Practices

### Protect Your API Key

1. **Never commit .env file:**
   ```bash
   # .env is already in .gitignore
   # Verify:
   cat .gitignore | grep .env
   ```

2. **Use environment variables:**
   ```bash
   # Set temporarily
   export OPENAI_API_KEY=sk-your-key-here

   # Run without .env file
   streamlit run src/ui/app.py
   ```

3. **Rotate keys regularly:**
   - Visit OpenAI dashboard
   - Create new key
   - Update .env file
   - Delete old key

### Scan for Secrets

```bash
# Install TruffleHog
pip install trufflehog

# Scan repository
trufflehog filesystem . --json
```

---

## 📈 Performance Tips

### Speed Up Application

1. **Use cache effectively:**
   - Same text + voice + speed = instant from cache
   - Check cache stats in UI

2. **Optimize documents:**
   - Remove unnecessary whitespace
   - Clean formatting before upload

3. **Use Standard quality** for testing:
   - Faster generation
   - Smaller files
   - Switch to HD for final version

4. **Batch similar content:**
   - Generate multiple chapters with same voice
   - Cache will speed up similar content

### Speed Up Tests

```bash
# Run tests in parallel
pytest tests/ -n auto

# Run only fast tests
pytest tests/unit/

# Skip slow integration tests
pytest tests/ -m "not slow"
```

---

## 🧹 Cleanup

### Remove Virtual Environment

```bash
# Deactivate first
deactivate

# Remove directory
rm -rf venv/
```

### Clear Cache

```bash
# Remove all cached audio
rm -rf cache/*

# Or selectively delete old files
find cache/ -type f -mtime +30 -delete  # Older than 30 days
```

### Uninstall Everything

```bash
cd ..
rm -rf Voicebook/
```

---

## 🔄 Updating

### Pull Latest Code

```bash
# Pull from GitHub
git pull origin main

# Reinstall dependencies (in case they changed)
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Update Dependencies

```bash
# Update all packages
pip install -r requirements.txt --upgrade

# Or update specific package
pip install streamlit --upgrade
```

---

## 💡 Tips for Low-Resource Systems

### Minimum Requirements

- **CPU:** 1 core, 1.5 GHz
- **RAM:** 2 GB (1 GB for OS, 1 GB for Python)
- **Disk:** 1 GB free space
- **Internet:** Required for API calls

### Optimize for Your System

1. **Close unnecessary applications**
   - Browser tabs
   - Background processes

2. **Use lightweight browser**
   - Firefox/Chrome use ~500 MB RAM
   - Consider Edge or Safari

3. **Reduce cache size**
   - Set max cache size in settings
   - Clear old files regularly

4. **Generate smaller audiobooks**
   - Process chapters individually
   - Shorter documents use less memory

5. **Use Standard quality**
   - HD uses 2x API quota
   - Larger file sizes

---

## 📚 Learning Resources

### Streamlit Documentation
- **Docs:** https://docs.streamlit.io
- **Gallery:** https://streamlit.io/gallery
- **Forums:** https://discuss.streamlit.io

### Python Virtual Environments
- **venv Guide:** https://docs.python.org/3/tutorial/venv.html
- **Best Practices:** https://realpython.com/python-virtual-environments/

### OpenAI API
- **TTS Docs:** https://platform.openai.com/docs/guides/text-to-speech
- **Pricing:** https://openai.com/pricing
- **Rate Limits:** https://platform.openai.com/docs/guides/rate-limits

---

## ✅ Success Checklist

Before generating your first audiobook:

- [ ] Python 3.9+ installed (`python3 --version`)
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip list`)
- [ ] .env file created with valid API key
- [ ] Application starts without errors
- [ ] Can access UI at localhost:8501
- [ ] Tests pass (optional: `pytest tests/`)
- [ ] Cache directory exists and is writable

---

## 🆘 Need Help?

### Quick Diagnostics

Run our diagnostic script:

```bash
chmod +x validate-setup.sh
./validate-setup.sh
```

This checks:
- ✅ Python version
- ✅ Dependencies installed
- ✅ Environment configured
- ✅ File permissions
- ✅ Directory structure

### Get Support

- **Documentation:** README.md, DOCKER.md, CONTRIBUTING.md
- **Issues:** https://github.com/eteka/Voicebook/issues
- **Discussions:** GitHub Discussions

### Common Questions

**Q: Do I need Docker?**
A: No! Docker is optional. Native Python works great for development and low-resource systems.

**Q: Can I run this on a Raspberry Pi?**
A: Yes! Python 3.9+ and 1 GB RAM minimum. May be slower on RPi 3 or older.

**Q: How much does it cost to run?**
A: Only OpenAI API costs. Free tier includes $5 credit. ~$0.015 per 1000 characters.

**Q: Can I use this offline?**
A: No, requires internet for OpenAI API calls. Cache works offline for previously generated content.

**Q: Is my data secure?**
A: Data is sent to OpenAI API. Read their privacy policy. Run locally = no other third parties.

---

## 🎉 You're All Set!

Voicebook is now running natively on your system with minimal resource usage.

**Next Steps:**

1. **Generate your first audiobook:**
   - Upload a document or paste text
   - Choose voice and settings
   - Click "Generate Audiobook"

2. **Explore features:**
   - Try different voices
   - Test speed variations
   - Check cache statistics

3. **Customize:**
   - Modify UI in `src/ui/app.py`
   - Add features
   - Contribute back!

**Happy Listening! 🎧**

---

## 📖 Related Guides

- **Quick Start:** QUICKSTART.md
- **Docker Guide:** DOCKER.md (if you want to try Docker later)
- **Contributing:** CONTRIBUTING.md
- **Full README:** README.md
