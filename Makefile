.PHONY: help build run stop clean test lint format security docker-compose k8s-deploy k8s-delete

# Variables
IMAGE_NAME := voicebook
IMAGE_TAG := latest
CONTAINER_NAME := voicebook-app
PORT := 8501
REGISTRY := ghcr.io/eteka

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Help target
help: ## Show this help message
	@echo "$(BLUE)Voicebook - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ================================
# Development
# ================================

setup: ## Set up development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	chmod +x setup-dev.sh
	./setup-dev.sh

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install -r requirements.txt -r requirements-dev.txt

test: ## Run tests with coverage
	@echo "$(BLUE)Running tests...$(NC)"
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest tests/integration/ -v

coverage: ## Generate coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	pytest tests/ --cov=src --cov-report=html
	@echo "$(GREEN)Coverage report: htmlcov/index.html$(NC)"

lint: ## Run linting checks
	@echo "$(BLUE)Running linters...$(NC)"
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/
	mypy src/

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	black src/ tests/
	isort src/ tests/

security: ## Run security checks
	@echo "$(BLUE)Running security scans...$(NC)"
	bandit -r src/
	safety check

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files

# ================================
# Docker
# ================================

build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

build-no-cache: ## Build Docker image without cache
	@echo "$(BLUE)Building Docker image (no cache)...$(NC)"
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .

run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p $(PORT):8501 \
		--env-file .env \
		-v $(PWD)/cache:/app/cache \
		$(IMAGE_NAME):$(IMAGE_TAG)
	@echo "$(GREEN)Container started at http://localhost:$(PORT)$(NC)"

run-it: ## Run Docker container interactively
	@echo "$(BLUE)Running Docker container (interactive)...$(NC)"
	docker run -it --rm \
		--name $(CONTAINER_NAME)-interactive \
		-p $(PORT):8501 \
		--env-file .env \
		-v $(PWD)/cache:/app/cache \
		$(IMAGE_NAME):$(IMAGE_TAG)

exec: ## Execute bash in running container
	@echo "$(BLUE)Executing bash in container...$(NC)"
	docker exec -it $(CONTAINER_NAME) bash

logs: ## Show container logs
	@echo "$(BLUE)Showing container logs...$(NC)"
	docker logs -f $(CONTAINER_NAME)

stop: ## Stop Docker container
	@echo "$(BLUE)Stopping container...$(NC)"
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true

clean: ## Clean up Docker resources
	@echo "$(BLUE)Cleaning up Docker resources...$(NC)"
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) || true
	docker system prune -f

scan: ## Scan Docker image for vulnerabilities
	@echo "$(BLUE)Scanning Docker image...$(NC)"
	trivy image $(IMAGE_NAME):$(IMAGE_TAG)

scan-critical: ## Scan for critical vulnerabilities only
	@echo "$(BLUE)Scanning for critical vulnerabilities...$(NC)"
	trivy image --severity CRITICAL,HIGH $(IMAGE_NAME):$(IMAGE_TAG)

push: ## Push image to registry
	@echo "$(BLUE)Pushing image to registry...$(NC)"
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

# ================================
# Docker Compose
# ================================

up: ## Start services with docker-compose
	@echo "$(BLUE)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started$(NC)"

up-build: ## Build and start services
	@echo "$(BLUE)Building and starting services...$(NC)"
	docker-compose up -d --build

down: ## Stop docker-compose services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose down

down-v: ## Stop services and remove volumes
	@echo "$(BLUE)Stopping services and removing volumes...$(NC)"
	docker-compose down -v

dev: ## Start in development mode
	@echo "$(BLUE)Starting in development mode...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

ps: ## Show running containers
	@echo "$(BLUE)Running containers:$(NC)"
	docker-compose ps

# ================================
# Kubernetes
# ================================

k8s-deploy: ## Deploy to Kubernetes
	@echo "$(BLUE)Deploying to Kubernetes...$(NC)"
	kubectl apply -f k8s/

k8s-delete: ## Delete from Kubernetes
	@echo "$(BLUE)Deleting from Kubernetes...$(NC)"
	kubectl delete -f k8s/

k8s-status: ## Check Kubernetes deployment status
	@echo "$(BLUE)Checking deployment status...$(NC)"
	kubectl get pods -l app=voicebook
	kubectl get svc voicebook
	kubectl get ingress voicebook-ingress

k8s-logs: ## Show Kubernetes logs
	@echo "$(BLUE)Showing Kubernetes logs...$(NC)"
	kubectl logs -f -l app=voicebook

k8s-describe: ## Describe Kubernetes resources
	@echo "$(BLUE)Describing Kubernetes resources...$(NC)"
	kubectl describe deployment voicebook
	kubectl describe svc voicebook

k8s-port-forward: ## Port forward to Kubernetes service
	@echo "$(BLUE)Port forwarding to Kubernetes service...$(NC)"
	kubectl port-forward svc/voicebook $(PORT):80

# ================================
# CI/CD
# ================================

ci: lint test ## Run CI checks locally
	@echo "$(GREEN)All CI checks passed!$(NC)"

ci-security: security scan ## Run security checks
	@echo "$(GREEN)Security checks complete!$(NC)"

# ================================
# Documentation
# ================================

docs: ## Open documentation
	@echo "$(BLUE)Opening documentation...$(NC)"
	@echo "README: README.md"
	@echo "Docker Guide: DOCKER.md"
	@echo "Contributing: CONTRIBUTING.md"
	@echo "CI/CD Setup: .github/CI_CD_SETUP.md"
	@echo "Tests: tests/README.md"

# ================================
# Utilities
# ================================

version: ## Show version information
	@echo "$(BLUE)Version Information:$(NC)"
	@echo "Python: $$(python --version)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"
	@echo "kubectl: $$(kubectl version --client --short 2>/dev/null || echo 'Not installed')"

check-env: ## Check if .env file exists
	@if [ ! -f .env ]; then \
		echo "$(RED)Error: .env file not found$(NC)"; \
		echo "$(YELLOW)Run: cp .env.example .env$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN).env file exists$(NC)"; \
	fi

# Default target
.DEFAULT_GOAL := help
