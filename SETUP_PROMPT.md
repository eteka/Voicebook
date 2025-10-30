# Prompt for IDE Assistant (Cursor/Windsurf/etc.)

Copy and paste this prompt to your IDE assistant to get help setting up Voicebook locally:

---

I need help setting up and running Voicebook, a Text-to-Speech audiobook generator application, on my local machine.

## Project Overview

Voicebook is a Python Streamlit application that converts documents (TXT, PDF, DOCX) into audiobooks using OpenAI's Text-to-Speech API. It features smart caching to minimize costs and supports multiple voices and quality settings.

## Current State

The project code is already in my workspace at the following location:
- Repository: Voicebook/
- Main application: `src/ui/app.py`
- Configuration template: `.env.example`

## What I Need Help With

Please help me:

1. **Verify Prerequisites**
   - Check if I have Python 3.9+ installed
   - Verify pip is available
   - List any missing dependencies

2. **Install Python Dependencies**
   - Install packages from `requirements.txt`
   - Alert me if any installations fail
   - Suggest fixes for common installation issues

3. **Configure Environment**
   - Help me create a `.env` file from `.env.example`
   - Guide me on where to get an OpenAI API key (https://platform.openai.com/api-keys)
   - Help me add the API key to `.env` in the format: `OPENAI_API_KEY=sk-...`
   - Ensure the `.env` file is properly formatted

4. **Run the Application**
   - Start the Streamlit app using the `run.py` script
   - OR run it directly: `streamlit run src/ui/app.py`
   - Show me the command to run and what output to expect
   - Help troubleshoot if the app doesn't start

5. **Verify Everything Works**
   - Confirm the app opens at `http://localhost:8501`
   - Check that all features are accessible
   - Help me test with the sample document at `samples/sample_document.txt`

## Technical Details

**Tech Stack:**
- Python 3.9+
- Streamlit (web UI framework)
- OpenAI Python SDK (for TTS API)
- PyPDF2/pypdf (PDF parsing)
- python-docx (Word document parsing)

**Key Files:**
- `run.py` - Quick launch script
- `src/ui/app.py` - Main Streamlit application
- `.env.example` - Configuration template
- `requirements.txt` - Python dependencies
- `README.md` - Full documentation

**Important Notes:**
- The `.env` file should NOT be committed to git (already in .gitignore)
- OpenAI API key is required - I need to create one at https://platform.openai.com/api-keys
- The app will create `cache/` and `uploads/` directories automatically
- API usage costs money ($15 per 1M characters), but caching saves 95% on repeated content

## Expected Outcome

After setup, I should be able to:
1. Run `python run.py` (or `streamlit run src/ui/app.py`)
2. See the app open in my browser at `http://localhost:8501`
3. Upload a document or paste text
4. Select a voice and generate audio
5. Play and download the generated audiobook

## Platform-Specific Help

I'm running on: [YOUR OS - Windows/Mac/Linux]

Please provide platform-specific commands and troubleshooting if needed.

## Questions to Answer

1. What Python version do I currently have?
2. Are all required packages installable on my system?
3. What's the exact command to run the app?
4. How do I stop the app when I'm done?
5. Where can I find generated audio files?

Please walk me through each step and verify it works before moving to the next one. Let me know if you need to see any files or error messages.

---

## Additional Context (Optional)

If the assistant asks for more information, you can share:

**Common Issues:**
- Windows users may need `python-magic-bin` instead of `python-magic`
- Mac users might need to install Python via Homebrew
- Linux users should have most dependencies available via package manager

**Cost Information:**
- Sample document (~3,000 words) costs ~$0.30 to generate
- Regenerating with same settings costs $0.00 (cached)
- Set OpenAI spending limits to avoid surprises

**Getting OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with "sk-")
5. Add to `.env` file

---

## Quick Reference Commands

```bash
# Check Python version
python --version  # or python3 --version

# Install dependencies
pip install -r requirements.txt  # or pip3 install -r requirements.txt

# Create .env file (then edit it)
cp .env.example .env

# Run the application
python run.py  # or: streamlit run src/ui/app.py

# Stop the application
# Press Ctrl+C in the terminal
```

---

**Start by checking my Python version and then guide me through each step systematically.**
