#!/bin/bash
# Validation script to check all files and configurations before local testing

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Voicebook - Setup Validation${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $1${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 - MISSING${NC}"
        ((ERRORS++))
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅ $1/${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  $1/ - MISSING (will be created)${NC}"
        ((WARNINGS++))
        return 1
    fi
}

# Check Docker files
echo -e "${BLUE}📦 Docker Files:${NC}"
check_file "Dockerfile"
check_file ".dockerignore"
check_file "docker-compose.yml"
check_file "docker-compose.dev.yml"
check_file "container-structure-test.yaml"
echo ""

# Check Kubernetes manifests
echo -e "${BLUE}☸️  Kubernetes Manifests:${NC}"
check_dir "k8s"
if [ -d "k8s" ]; then
    check_file "k8s/deployment.yml"
    check_file "k8s/service.yml"
    check_file "k8s/configmap.yml"
    check_file "k8s/secrets.yml"
    check_file "k8s/pvc.yml"
    check_file "k8s/rbac.yml"
    check_file "k8s/hpa.yml"
    check_file "k8s/ingress.yml"
fi
echo ""

# Check source code
echo -e "${BLUE}📝 Source Code:${NC}"
check_dir "src"
if [ -d "src" ]; then
    check_dir "src/api"
    check_dir "src/cache"
    check_dir "src/processors"
    check_dir "src/utils"
    check_dir "src/ui"
fi
echo ""

# Check tests
echo -e "${BLUE}🧪 Tests:${NC}"
check_dir "tests"
if [ -d "tests" ]; then
    check_dir "tests/unit"
    check_dir "tests/integration"
    check_file "tests/conftest.py"
    check_file "pytest.ini"
fi
echo ""

# Check configuration files
echo -e "${BLUE}⚙️  Configuration Files:${NC}"
check_file "requirements.txt"
check_file "requirements-dev.txt"
check_file "pyproject.toml"
check_file ".env.example"
check_file ".gitignore"

if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env${NC}"
else
    echo -e "${YELLOW}⚠️  .env - MISSING (copy from .env.example)${NC}"
    ((WARNINGS++))
fi
echo ""

# Check documentation
echo -e "${BLUE}📚 Documentation:${NC}"
check_file "README.md"
check_file "DOCKER.md"
check_file "CONTRIBUTING.md"
check_file "LICENSE"
check_file "QUICKSTART.md"
echo ""

# Check CI/CD
echo -e "${BLUE}🔄 CI/CD Files:${NC}"
check_dir ".github"
if [ -d ".github" ]; then
    check_dir ".github/workflows"
    check_file ".github/workflows/ci.yml"
    check_file ".github/workflows/code-quality.yml"
    check_file ".github/workflows/security.yml"
    check_file ".github/workflows/container-security.yml"
    check_file ".github/dependabot.yml"
fi
check_file ".pre-commit-config.yaml"
echo ""

# Check helper scripts
echo -e "${BLUE}🛠️  Helper Scripts:${NC}"
check_file "Makefile"
check_file "setup-dev.sh"
check_file "test-docker.sh"
check_file "validate-setup.sh"
echo ""

# Check cache directory
echo -e "${BLUE}💾 Cache Directory:${NC}"
check_dir "cache"
echo ""

# Validate Dockerfile syntax
echo -e "${BLUE}🔍 Dockerfile Validation:${NC}"
if [ -f "Dockerfile" ]; then
    # Check for common issues
    if grep -q "COPY \. \." Dockerfile; then
        echo -e "${GREEN}✅ Dockerfile uses proper COPY syntax${NC}"
    fi

    if grep -q "USER voicebook" Dockerfile; then
        echo -e "${GREEN}✅ Dockerfile runs as non-root user${NC}"
    fi

    if grep -q "HEALTHCHECK" Dockerfile; then
        echo -e "${GREEN}✅ Dockerfile includes health check${NC}"
    fi

    if grep -q "FROM.*as builder" Dockerfile; then
        echo -e "${GREEN}✅ Dockerfile uses multi-stage build${NC}"
    fi
fi
echo ""

# Validate docker-compose.yml syntax
echo -e "${BLUE}🔍 Docker Compose Validation:${NC}"
if command -v docker-compose &> /dev/null; then
    if docker-compose config > /dev/null 2>&1; then
        echo -e "${GREEN}✅ docker-compose.yml is valid${NC}"
    else
        echo -e "${RED}❌ docker-compose.yml has errors${NC}"
        ((ERRORS++))
    fi
elif command -v docker &> /dev/null; then
    if docker compose config > /dev/null 2>&1; then
        echo -e "${GREEN}✅ docker-compose.yml is valid${NC}"
    else
        echo -e "${RED}❌ docker-compose.yml has errors${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⚠️  Docker not installed - cannot validate${NC}"
    ((WARNINGS++))
fi
echo ""

# Check Python version
echo -e "${BLUE}🐍 Python Environment:${NC}"
if command -v python3 &> /dev/null; then
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
else
    echo -e "${RED}❌ Python3 not installed${NC}"
    ((ERRORS++))
fi
echo ""

# Check Docker
echo -e "${BLUE}🐳 Docker Environment:${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo -e "${GREEN}✅ Docker installed: ${DOCKER_VERSION}${NC}"

    if docker ps > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker daemon is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Docker daemon not running${NC}"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠️  Docker not installed (optional for local Python development)${NC}"
    ((WARNINGS++))
fi
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Validation Summary:${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 Perfect! All checks passed.${NC}"
    echo ""
    echo -e "${BLUE}✨ You're ready to:${NC}"
    echo "  1. Run locally:     ./test-docker.sh"
    echo "  2. Use Makefile:    make build && make run"
    echo "  3. Use Compose:     docker-compose up"
    echo ""
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Warnings: ${WARNINGS}${NC}"
    echo -e "${GREEN}✅ Errors: 0${NC}"
    echo ""
    echo -e "${BLUE}You can proceed, but review warnings above.${NC}"
    echo ""
else
    echo -e "${RED}❌ Errors: ${ERRORS}${NC}"
    echo -e "${YELLOW}⚠️  Warnings: ${WARNINGS}${NC}"
    echo ""
    echo -e "${RED}Please fix errors before proceeding.${NC}"
    echo ""
    exit 1
fi

# Next steps
echo -e "${BLUE}📖 Documentation:${NC}"
echo "  - Quick Start:      cat QUICKSTART.md"
echo "  - Docker Guide:     cat DOCKER.md"
echo "  - Full README:      cat README.md"
echo ""

echo -e "${BLUE}🚀 Quick Commands:${NC}"
echo "  - See all commands: make help"
echo "  - Run tests:        make test"
echo "  - Build Docker:     make build"
echo "  - Start app:        make run"
echo ""

exit 0
