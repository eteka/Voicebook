#!/bin/bash
# Lightweight local testing script - NO DOCKER REQUIRED
# Perfect for low-resource systems

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🪶 Voicebook - Lightweight Local Testing${NC}"
echo -e "${BLUE}No Docker required - runs natively with Python${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Step 1: Check Python
echo -e "${BLUE}Step 1: Checking Python...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    echo "Install: https://www.python.org/downloads/"
    ((ERRORS++))
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python installed: ${PYTHON_VERSION}${NC}"

    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 9 ]; then
        echo -e "${GREEN}✅ Python version is 3.9 or higher${NC}"
    else
        echo -e "${RED}❌ Python 3.9+ required, found ${PYTHON_VERSION}${NC}"
        ((ERRORS++))
    fi
fi

echo ""

# Check if we should exit early due to errors
if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}❌ Critical errors found. Please fix Python installation first.${NC}"
    exit 1
fi

# Step 2: Check virtual environment
echo -e "${BLUE}Step 2: Checking virtual environment...${NC}"

if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

echo ""

# Step 3: Activate virtual environment
echo -e "${BLUE}Step 3: Activating virtual environment...${NC}"

# Detect OS and activate appropriately
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Step 4: Check dependencies
echo -e "${BLUE}Step 4: Checking dependencies...${NC}"

if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ requirements.txt found${NC}"

    # Check if packages are installed
    if python3 -c "import streamlit" 2>/dev/null; then
        echo -e "${GREEN}✅ Dependencies appear to be installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Dependencies not installed${NC}"
        echo -e "${BLUE}Installing dependencies...${NC}"
        echo "This may take 2-5 minutes..."
        pip install -q -r requirements.txt
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    fi
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    ((ERRORS++))
fi

echo ""

# Step 5: Check .env file
echo -e "${BLUE}Step 5: Checking environment configuration...${NC}"

if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"

    # Check if API key is set (not checking validity, just presence)
    if grep -q "OPENAI_API_KEY=" .env && ! grep -q "OPENAI_API_KEY=$" .env && ! grep -q "OPENAI_API_KEY=your" .env; then
        echo -e "${GREEN}✅ OPENAI_API_KEY appears to be set${NC}"
    else
        echo -e "${YELLOW}⚠️  OPENAI_API_KEY not configured in .env${NC}"
        echo "   Edit .env and add your OpenAI API key"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    if [ -f ".env.example" ]; then
        echo -e "${BLUE}Copying .env.example to .env...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Please edit .env and add your OPENAI_API_KEY${NC}"
        ((WARNINGS++))
    else
        echo -e "${RED}❌ .env.example not found${NC}"
        ((ERRORS++))
    fi
fi

echo ""

# Step 6: Check source files
echo -e "${BLUE}Step 6: Checking source files...${NC}"

REQUIRED_FILES=(
    "src/ui/app.py"
    "src/api/openai_tts.py"
    "src/cache/audio_cache.py"
    "src/utils/validators.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file - MISSING${NC}"
        ((ERRORS++))
    fi
done

echo ""

# Step 7: Check cache directory
echo -e "${BLUE}Step 7: Checking cache directory...${NC}"

if [ -d "cache" ]; then
    echo -e "${GREEN}✅ cache/ directory exists${NC}"

    # Check permissions
    if [ -w "cache" ]; then
        echo -e "${GREEN}✅ cache/ is writable${NC}"
    else
        echo -e "${RED}❌ cache/ is not writable${NC}"
        echo "   Fix: chmod +w cache/"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⚠️  cache/ directory not found${NC}"
    echo -e "${BLUE}Creating cache/ directory...${NC}"
    mkdir -p cache
    echo -e "${GREEN}✅ cache/ directory created${NC}"
fi

echo ""

# Step 8: Run quick import test
echo -e "${BLUE}Step 8: Testing Python imports...${NC}"

python3 << 'PYEOF'
import sys
errors = []

try:
    import streamlit
    print("✅ streamlit")
except ImportError as e:
    errors.append(f"❌ streamlit - {e}")

try:
    import openai
    print("✅ openai")
except ImportError as e:
    errors.append(f"❌ openai - {e}")

try:
    from src.api.openai_tts import OpenAITTS
    print("✅ src.api.openai_tts")
except ImportError as e:
    errors.append(f"❌ src.api.openai_tts - {e}")

try:
    from src.cache.audio_cache import AudioCache
    print("✅ src.cache.audio_cache")
except ImportError as e:
    errors.append(f"❌ src.cache.audio_cache - {e}")

if errors:
    print("\nImport errors:")
    for error in errors:
        print(error)
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All critical imports successful${NC}"
else
    echo -e "${RED}❌ Import errors detected${NC}"
    ((ERRORS++))
fi

echo ""

# Step 9: Run tests (optional)
echo -e "${BLUE}Step 9: Running tests (optional)...${NC}"

if [ -f "requirements-dev.txt" ]; then
    # Check if pytest is installed
    if python3 -c "import pytest" 2>/dev/null; then
        echo -e "${GREEN}✅ pytest is installed${NC}"

        # Ask user if they want to run tests
        echo -e "${BLUE}Run tests? This will take 30-60 seconds. (y/N)${NC}"
        read -t 10 -n 1 -r RUN_TESTS || RUN_TESTS="n"
        echo ""

        if [[ $RUN_TESTS =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}Running tests...${NC}"
            if pytest tests/ -q --tb=short; then
                echo -e "${GREEN}✅ All tests passed!${NC}"
            else
                echo -e "${YELLOW}⚠️  Some tests failed (this might be OK for development)${NC}"
                ((WARNINGS++))
            fi
        else
            echo -e "${YELLOW}⚠️  Skipped tests${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  pytest not installed${NC}"
        echo "   Install dev dependencies: pip install -r requirements-dev.txt"
    fi
else
    echo -e "${YELLOW}⚠️  requirements-dev.txt not found${NC}"
fi

echo ""

# Step 10: System resource check
echo -e "${BLUE}Step 10: Checking system resources...${NC}"

# Check available memory (Linux/Mac)
if command -v free &> /dev/null; then
    AVAILABLE_MB=$(free -m | awk 'NR==2{print $7}')
    echo -e "${BLUE}Available memory: ${AVAILABLE_MB} MB${NC}"

    if [ "$AVAILABLE_MB" -lt 500 ]; then
        echo -e "${YELLOW}⚠️  Low memory (<500 MB available)${NC}"
        echo "   Close other applications for better performance"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✅ Sufficient memory available${NC}"
    fi
elif command -v vm_stat &> /dev/null; then
    # macOS
    echo -e "${BLUE}macOS detected - checking memory...${NC}"
    FREE_PAGES=$(vm_stat | grep "Pages free" | awk '{print $3}' | tr -d '.')
    AVAILABLE_MB=$((FREE_PAGES * 4096 / 1048576))
    echo -e "${BLUE}Available memory: ~${AVAILABLE_MB} MB${NC}"

    if [ "$AVAILABLE_MB" -lt 500 ]; then
        echo -e "${YELLOW}⚠️  Low memory (<500 MB available)${NC}"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✅ Sufficient memory available${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Could not check available memory${NC}"
fi

# Check disk space
if command -v df &> /dev/null; then
    AVAILABLE_MB=$(df -m . | awk 'NR==2{print $4}')
    echo -e "${BLUE}Available disk space: ${AVAILABLE_MB} MB${NC}"

    if [ "$AVAILABLE_MB" -lt 500 ]; then
        echo -e "${YELLOW}⚠️  Low disk space (<500 MB available)${NC}"
        echo "   Clear cache: rm -rf cache/*"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✅ Sufficient disk space${NC}"
    fi
fi

echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Validation Summary:${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 Perfect! Everything is ready.${NC}"
    echo ""
    echo -e "${BLUE}✨ Start Voicebook:${NC}"
    echo ""
    echo "  streamlit run src/ui/app.py"
    echo ""
    echo -e "${BLUE}Then open: ${GREEN}http://localhost:8501${NC}"
    echo ""
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Warnings: ${WARNINGS}${NC}"
    echo -e "${GREEN}✅ Errors: 0${NC}"
    echo ""
    echo -e "${BLUE}You can proceed, but review warnings above.${NC}"
    echo ""
    echo -e "${BLUE}✨ Start Voicebook:${NC}"
    echo ""
    echo "  streamlit run src/ui/app.py"
    echo ""
else
    echo -e "${RED}❌ Errors: ${ERRORS}${NC}"
    echo -e "${YELLOW}⚠️  Warnings: ${WARNINGS}${NC}"
    echo ""
    echo -e "${RED}Please fix errors before proceeding.${NC}"
    echo ""
    exit 1
fi

# Resource usage estimate
echo -e "${BLUE}📊 Expected Resource Usage:${NC}"
echo "  RAM: ~200-500 MB (minimal!)"
echo "  CPU: ~5-20% (single core)"
echo "  Disk: ~500 MB + cache growth"
echo ""

echo -e "${BLUE}💡 Tips:${NC}"
echo "  - Virtual environment is activated in current shell"
echo "  - Deactivate with: ${YELLOW}deactivate${NC}"
echo "  - Reactivate with: ${YELLOW}source venv/bin/activate${NC}"
echo "  - Stop app with: ${YELLOW}Ctrl+C${NC}"
echo ""

echo -e "${BLUE}📚 Documentation:${NC}"
echo "  - Lightweight Guide: ${GREEN}LIGHTWEIGHT_SETUP.md${NC}"
echo "  - Quick Start:       QUICKSTART.md"
echo "  - Full README:       README.md"
echo ""

exit 0
