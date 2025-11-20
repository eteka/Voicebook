#!/bin/bash
# Quick local testing script for Voicebook containerization

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Voicebook - Local Container Testing${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker installed: $(docker --version)${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  docker-compose not found, trying docker compose...${NC}"
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Neither docker-compose nor docker compose is available${NC}"
        exit 1
    fi
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi
echo -e "${GREEN}✅ Docker Compose available${NC}"

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo -e "${BLUE}Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env and add your OPENAI_API_KEY${NC}"
    echo -e "${YELLOW}   You can use a test key or skip API-dependent features${NC}"
fi

echo ""

# Step 2: Build Docker image
echo -e "${BLUE}Step 2: Building Docker image...${NC}"
echo "This may take a few minutes on first build..."
docker build -t voicebook:latest . --quiet
echo -e "${GREEN}✅ Docker image built successfully${NC}"

# Check image size
IMAGE_SIZE=$(docker images voicebook:latest --format "{{.Size}}")
echo -e "${GREEN}   Image size: ${IMAGE_SIZE}${NC}"

echo ""

# Step 3: Run container structure tests (if available)
echo -e "${BLUE}Step 3: Running container validation tests...${NC}"
if command -v container-structure-test &> /dev/null; then
    container-structure-test test \
        --image voicebook:latest \
        --config container-structure-test.yaml
    echo -e "${GREEN}✅ Container structure tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  container-structure-test not installed (optional)${NC}"
    echo "   Install: https://github.com/GoogleContainerTools/container-structure-test"
fi

echo ""

# Step 4: Security scan (if available)
echo -e "${BLUE}Step 4: Security scanning...${NC}"
if command -v trivy &> /dev/null; then
    echo "Running Trivy scan..."
    trivy image --severity HIGH,CRITICAL voicebook:latest
    echo -e "${GREEN}✅ Security scan complete${NC}"
else
    echo -e "${YELLOW}⚠️  Trivy not installed (recommended for production)${NC}"
    echo "   Install: https://aquasecurity.github.io/trivy/"
fi

echo ""

# Step 5: Start container
echo -e "${BLUE}Step 5: Starting container...${NC}"

# Stop any existing container
docker stop voicebook-test 2>/dev/null || true
docker rm voicebook-test 2>/dev/null || true

# Run container
docker run -d \
    --name voicebook-test \
    -p 8501:8501 \
    --env-file .env \
    -v $(pwd)/cache:/app/cache \
    voicebook:latest

echo -e "${GREEN}✅ Container started${NC}"
echo ""

# Step 6: Wait for health check
echo -e "${BLUE}Step 6: Waiting for application to be ready...${NC}"
echo "Checking health endpoint..."

for i in {1..30}; do
    if curl -sf http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Application is healthy!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Health check timeout${NC}"
        echo "Check logs with: docker logs voicebook-test"
        exit 1
    fi
    echo -n "."
    sleep 2
done

echo ""

# Step 7: Show status
echo -e "${BLUE}Step 7: Container status${NC}"
docker ps --filter name=voicebook-test --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo -e "${GREEN}🎉 Success! Voicebook is running${NC}"
echo ""
echo -e "${BLUE}Access the application:${NC}"
echo "  🌐 http://localhost:8501"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  📋 View logs:        docker logs -f voicebook-test"
echo "  🔍 Inspect:          docker inspect voicebook-test"
echo "  🖥️  Execute shell:    docker exec -it voicebook-test bash"
echo "  🛑 Stop container:   docker stop voicebook-test"
echo "  🗑️  Remove container: docker rm voicebook-test"
echo ""
echo -e "${YELLOW}Press Ctrl+C when ready to stop testing${NC}"
echo ""

# Follow logs
docker logs -f voicebook-test
