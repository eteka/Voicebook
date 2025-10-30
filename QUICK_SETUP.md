# Quick Setup with IDE Assistant

## 🚀 Super Short Prompt (Copy This!)

```
Help me set up Voicebook locally:

1. Check Python 3.9+ is installed
2. Run: pip install -r requirements.txt
3. Create .env file from .env.example
4. Add my OpenAI API key to .env (OPENAI_API_KEY=sk-...)
5. Run: python run.py
6. Open http://localhost:8501

Guide me through each step and troubleshoot any errors.
```

---

## 📋 Medium Prompt (More Guidance)

```
I have a Streamlit TTS audiobook app called Voicebook that I need to run locally.

Setup needed:
- Install Python packages from requirements.txt
- Create .env file with my OpenAI API key
- Run the Streamlit app

Please:
1. Verify I have Python 3.9+
2. Install dependencies: pip install -r requirements.txt
3. Help me create .env from .env.example
4. Guide me to get OpenAI API key: https://platform.openai.com/api-keys
5. Show me how to run: python run.py
6. Troubleshoot any issues

The app should open at http://localhost:8501
```

---

## 🔧 Detailed Prompt (Full Context)

**For a more comprehensive setup experience, use the prompt in `SETUP_PROMPT.md`**

---

## Platform-Specific Quick Commands

### Windows
```bash
# Check Python
python --version

# Install
pip install -r requirements.txt

# Setup
copy .env.example .env
notepad .env

# Run
python run.py
```

### Mac/Linux
```bash
# Check Python
python3 --version

# Install
pip3 install -r requirements.txt

# Setup
cp .env.example .env
nano .env  # or: vim .env, code .env

# Run
python3 run.py
```

---

## What to Add to .env

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get your key from: https://platform.openai.com/api-keys

---

## Expected Result

✅ Terminal shows: "You can now view your Streamlit app in your browser"
✅ Browser opens automatically to http://localhost:8501
✅ You see the Voicebook interface with upload/paste options

---

## Common Issues & Fixes

**"Python not found"**
- Windows: Install from python.org
- Mac: `brew install python3`
- Linux: `sudo apt install python3 python3-pip`

**"Module not found" errors**
- Run: `pip install -r requirements.txt` again
- Try: `pip3` instead of `pip`

**"OpenAI API key not found"**
- Make sure .env file exists
- Check: `OPENAI_API_KEY=sk-...` (no quotes, no spaces around =)
- Restart the app after adding key

**App won't start**
- Check Python version: `python --version` (need 3.9+)
- Try: `streamlit run src/ui/app.py` directly
- Check if port 8501 is already in use

---

## Just Want It Running? Use This:

**Windows:**
```powershell
python --version
pip install -r requirements.txt
copy .env.example .env
echo Add your API key to .env, then:
python run.py
```

**Mac/Linux:**
```bash
python3 --version
pip3 install -r requirements.txt
cp .env.example .env
echo "Add your API key to .env, then:"
python3 run.py
```
