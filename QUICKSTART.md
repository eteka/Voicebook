# 🚀 Voicebook - Quick Start Guide

Get Voicebook running locally in under 5 minutes!

## 📋 Prerequisites

- **Docker** 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ (included with Docker Desktop)
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

## ⚡ Quick Test (Recommended)

Use our automated test script:

```bash
# 1. Clone repository
git clone https://github.com/eteka/Voicebook.git
cd Voicebook

# 2. Run automated test
./test-docker.sh
```

This script will:
- ✅ Check prerequisites
- ✅ Build Docker image
- ✅ Run security scan (if Trivy installed)
- ✅ Start container
- ✅ Verify health
- ✅ Show logs

**Access:** http://localhost:8501

---

## 🐳 Method 1: Docker (Simple)

### Step 1: Build Image

```bash
docker build -t voicebook:latest .
```

### Step 2: Create .env File

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Step 3: Run Container

```bash
docker run -d \
  --name voicebook \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/cache:/app/cache \
  voicebook:latest
```

### Step 4: Access Application

Open browser: http://localhost:8501

### View Logs

```bash
docker logs -f voicebook
```

### Stop Container

```bash
docker stop voicebook
docker rm voicebook
```

---

## 🔧 Method 2: Docker Compose (Easier)

### Step 1: Create .env File

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Step 2: Start Services

```bash
docker-compose up -d
```

Or use the Makefile:

```bash
make up
```

### Step 3: Access Application

Open browser: http://localhost:8501

### View Logs

```bash
docker-compose logs -f voicebook
```

### Stop Services

```bash
docker-compose down
```

Or:

```bash
make down
```

---

## 🛠️ Method 3: Development Mode (Hot Reload)

Perfect for development with automatic code reloading:

```bash
# Start in development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

Or:

```bash
make dev
```

**Benefits:**
- ✅ Auto-reload on code changes
- ✅ Debug port exposed (5678)
- ✅ Source code mounted
- ✅ Test runner available

---

## 🧪 Method 4: Using Makefile (Easiest)

We provide a Makefile with 30+ commands:

```bash
# Build image
make build

# Run container
make run

# View logs
make logs

# Stop container
make stop

# Run tests
make test

# Security scan
make scan

# See all commands
make help
```

---

## 🔍 Verify Installation

### Check Container is Running

```bash
docker ps | grep voicebook
```

Expected output:
```
voicebook-app   Up X minutes   0.0.0.0:8501->8501/tcp
```

### Check Health

```bash
curl http://localhost:8501/_stcore/health
```

Expected: `{"status": "ok"}`

### Check Logs

```bash
docker logs voicebook
```

Should see: `You can now view your Streamlit app in your browser.`

---

## 🧹 Cleanup

### Stop and Remove Container

```bash
docker stop voicebook
docker rm voicebook
```

Or with Compose:

```bash
docker-compose down
```

### Remove Image

```bash
docker rmi voicebook:latest
```

### Clean Everything

```bash
make clean
```

---

## 🎯 What to Test

Once running, try these features:

1. **Upload a Document**
   - TXT, PDF, or DOCX file
   - Use sample: `samples/sample_document.txt`

2. **Paste Text**
   - Copy any text
   - Paste in the text area

3. **Choose Voice**
   - Try different voices: nova, alloy, echo, etc.
   - Each has unique characteristics

4. **Adjust Settings**
   - Quality: Standard or HD
   - Speed: 0.25x to 4.0x

5. **Generate Audio**
   - Click "Generate Audiobook"
   - Download MP3 file

6. **Test Caching**
   - Generate same text twice
   - Second time should be instant (cached)
   - Check cache statistics

---

## 🔒 Security Testing (Optional but Recommended)

### Install Trivy

```bash
# macOS
brew install aquasecurity/trivy/trivy

# Linux
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# Or use Docker
alias trivy="docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy"
```

### Scan Image

```bash
trivy image voicebook:latest
```

Or:

```bash
make scan
```

---

## 🐛 Troubleshooting

### Issue: Port 8501 already in use

**Solution:** Use different port

```bash
docker run -d \
  --name voicebook \
  -p 8502:8501 \  # Changed port
  --env-file .env \
  voicebook:latest
```

Access: http://localhost:8502

### Issue: Container keeps restarting

**Check logs:**

```bash
docker logs voicebook
```

**Common causes:**
- Missing OPENAI_API_KEY in .env
- Invalid API key format
- Port conflict

### Issue: Can't access application

**Check container status:**

```bash
docker ps -a | grep voicebook
```

**Check if running:**

```bash
docker inspect voicebook | grep Status
```

**Test from inside container:**

```bash
docker exec -it voicebook curl localhost:8501/_stcore/health
```

### Issue: Build fails

**Clear Docker cache:**

```bash
docker builder prune -a
docker build --no-cache -t voicebook:latest .
```

### Issue: Permission denied for cache directory

**Fix permissions:**

```bash
sudo chown -R $USER:$USER cache/
```

---

## 📊 Resource Usage

### Check Container Resources

```bash
docker stats voicebook
```

Shows:
- CPU usage
- Memory usage
- Network I/O
- Disk I/O

### Set Resource Limits

```bash
docker run -d \
  --name voicebook \
  --memory="1g" \
  --cpus="1.0" \
  -p 8501:8501 \
  --env-file .env \
  voicebook:latest
```

---

## 🔄 Updates

### Pull Latest Code

```bash
git pull origin main
```

### Rebuild Image

```bash
docker build -t voicebook:latest .
```

### Restart Container

```bash
docker-compose down
docker-compose up -d --build
```

Or:

```bash
make up-build
```

---

## 📚 Next Steps

After local testing:

1. **Read Full Docker Guide:** See `DOCKER.md`
2. **Deploy to Cloud:** AWS, GCP, or Azure
3. **Set up Kubernetes:** See `k8s/` manifests
4. **Enable Monitoring:** Prometheus + Grafana
5. **Configure CI/CD:** Already set up in `.github/workflows/`

---

## 🆘 Need Help?

- **Documentation:** See README.md
- **Docker Guide:** See DOCKER.md
- **Issues:** https://github.com/eteka/Voicebook/issues
- **Discussions:** GitHub Discussions

---

## ✅ Success Checklist

Before moving to production:

- [ ] Local Docker test passes
- [ ] Security scan shows no critical vulnerabilities
- [ ] Application loads at localhost:8501
- [ ] Can upload and process documents
- [ ] Audio generation works
- [ ] Cache is persisting
- [ ] Container health check passes
- [ ] Logs show no errors

---

**Happy Testing! 🎉**

Once local testing is successful, you're ready to deploy to production!
