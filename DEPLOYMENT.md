# Deployment Guide - Streamlit Cloud

## Why Streamlit Cloud?

Streamlit Cloud is the recommended platform for deploying Streamlit applications. It's free for public apps and specifically designed for Python/Streamlit projects.

## Prerequisites

- GitHub account
- Streamlit Cloud account (free): https://streamlit.io/cloud
- OpenAI API key

## Step-by-Step Deployment

### 1. Prepare Repository

Ensure your code is pushed to GitHub:

```bash
git checkout main  # or create a deployment branch
git merge claude/tts-audiobook-app-011CUdAh2N716kbvYWApGuUn
git push origin main
```

### 2. Sign Up for Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "Sign up" and authenticate with GitHub
3. Grant Streamlit access to your repositories

### 3. Deploy Your App

1. Click "New app" in Streamlit Cloud dashboard
2. Fill in deployment settings:
   - **Repository**: `eteka/Voicebook`
   - **Branch**: `main` (or your deployment branch)
   - **Main file path**: `src/ui/app.py`
3. Click "Deploy"

### 4. Configure Secrets (API Key)

**Important:** Never commit API keys to GitHub. Use Streamlit secrets instead.

1. In your app dashboard, click the hamburger menu (⋮)
2. Select "Settings"
3. Go to "Secrets" tab
4. Copy content from `.streamlit/secrets.toml.example`
5. Paste and update with your actual API key:

```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
DEFAULT_VOICE = "nova"
DEFAULT_SPEED = "1.0"
DEFAULT_QUALITY = "standard"
MAX_FILE_SIZE_MB = "50"
MAX_CHARACTERS = "500000"
WARN_COST_THRESHOLD = "2.00"
MONTHLY_BUDGET_USD = "50"
```

6. Click "Save"

### 5. Access Your App

Your app will be available at:
```
https://share.streamlit.io/[your-username]/voicebook/[branch]/src/ui/app.py
```

Or get a custom subdomain like:
```
https://voicebook-[username].streamlit.app
```

## Important Considerations

### Cost Management

**OpenAI API costs still apply** even on Streamlit Cloud:
- You'll be charged for each audio generation
- Cache still works to save money
- Set `WARN_COST_THRESHOLD` low if sharing publicly

### Privacy & Security

**If deployed publicly:**
- ⚠️ Anyone can access your app
- ⚠️ Anyone can generate audio using YOUR API key
- ⚠️ Your OpenAI costs could increase unexpectedly

**Solutions:**
1. **Make app private** (requires Streamlit Cloud Pro - $20/month)
2. **Add authentication** (requires code changes)
3. **Set OpenAI spending limits** (in OpenAI dashboard)
4. **Monitor usage** (check OpenAI usage dashboard regularly)

### Recommended: Local Deployment for Personal Use

For personal document conversion, **local deployment is better**:
- ✅ No hosting costs
- ✅ Private by default
- ✅ Full control over API usage
- ✅ Documents stay on your machine

Simply run:
```bash
python run.py
```

## Alternative Cloud Platforms

### Railway.app

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**Pricing:** $5 credit/month free tier

### Render.com

1. Create new "Web Service"
2. Connect GitHub repository
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run src/ui/app.py --server.port=$PORT`

**Pricing:** Free tier available with limits

### Heroku

```bash
# Create Procfile
echo "web: streamlit run src/ui/app.py --server.port=$PORT" > Procfile

# Deploy
heroku create voicebook
git push heroku main
```

**Note:** Heroku no longer has a free tier ($5-7/month minimum)

## Troubleshooting

### "ModuleNotFoundError"
- Ensure `requirements.txt` is complete
- Verify Python version in `.streamlit/config.toml`

### "API key not found"
- Check secrets are configured in Streamlit Cloud settings
- Verify secret name matches: `OPENAI_API_KEY`

### "App keeps sleeping"
- Free tier apps sleep after inactivity
- Upgrade to paid tier for always-on hosting
- Or use local deployment

### High costs
- Monitor OpenAI usage dashboard
- Set spending limits in OpenAI account
- Consider making app private
- Add authentication if public

## Recommendation

**For personal use (converting your own documents):**
→ Use local deployment: `python run.py`

**For sharing with team/organization:**
→ Deploy to Streamlit Cloud with authentication

**For public/portfolio project:**
→ Deploy to Streamlit Cloud with strict rate limiting

## Need Help?

- Streamlit Docs: https://docs.streamlit.io/streamlit-community-cloud
- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
