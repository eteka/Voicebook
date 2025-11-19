# Docker Deployment Guide

Complete guide for deploying Voicebook using Docker and Kubernetes.

## 📋 Table of Contents

- [Quick Start with Docker](#quick-start-with-docker)
- [Docker Compose](#docker-compose)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Container Security](#container-security)
- [Production Best Practices](#production-best-practices)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start with Docker

### Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ (for docker-compose usage)
- OpenAI API key

### Build the Image

```bash
# Clone repository
git clone https://github.com/eteka/Voicebook.git
cd Voicebook

# Build the Docker image
docker build -t voicebook:latest .

# Or use buildx for multi-platform builds
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t voicebook:latest \
  --push .
```

### Run the Container

```bash
# Run with environment variable
docker run -d \
  --name voicebook \
  -p 8501:8501 \
  -e OPENAI_API_KEY=your-api-key-here \
  -v $(pwd)/cache:/app/cache \
  voicebook:latest

# Or using .env file
docker run -d \
  --name voicebook \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/cache:/app/cache \
  voicebook:latest
```

### Access the Application

Open your browser to: http://localhost:8501

### View Logs

```bash
# Follow logs
docker logs -f voicebook

# Last 100 lines
docker logs --tail 100 voicebook
```

### Stop and Remove

```bash
# Stop container
docker stop voicebook

# Remove container
docker rm voicebook

# Remove image
docker rmi voicebook:latest
```

---

## 🐳 Docker Compose

### Basic Usage

**1. Create .env file:**

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

**2. Start services:**

```bash
# Start in background
docker-compose up -d

# Start and view logs
docker-compose up

# Start specific service
docker-compose up voicebook
```

**3. View status:**

```bash
# List running containers
docker-compose ps

# View logs
docker-compose logs -f voicebook
```

**4. Stop services:**

```bash
# Stop containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

### Development Mode

Use the development compose file for hot-reload and debugging:

```bash
# Start with dev configuration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Run tests in container
docker-compose --profile testing up test-runner

# Run linting
docker-compose --profile quality up linter
```

### Useful Commands

```bash
# Rebuild containers
docker-compose up --build

# Scale application
docker-compose up --scale voicebook=3

# Execute commands in running container
docker-compose exec voicebook bash

# View resource usage
docker-compose top
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- Container registry access (Docker Hub, GHCR, etc.)

### Quick Deploy

**1. Build and push image:**

```bash
# Tag for registry
docker tag voicebook:latest ghcr.io/YOUR_USERNAME/voicebook:latest

# Push to registry
docker push ghcr.io/YOUR_USERNAME/voicebook:latest
```

**2. Create namespace (optional):**

```bash
kubectl create namespace voicebook
```

**3. Create secrets:**

```bash
kubectl create secret generic voicebook-secrets \
  --from-literal=openai-api-key=your-api-key-here \
  -n default
```

**4. Deploy application:**

```bash
# Apply all manifests
kubectl apply -f k8s/

# Or apply individually
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/secrets.yml
kubectl apply -f k8s/pvc.yml
kubectl apply -f k8s/rbac.yml
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/hpa.yml
kubectl apply -f k8s/ingress.yml
```

**5. Verify deployment:**

```bash
# Check pods
kubectl get pods -l app=voicebook

# Check services
kubectl get svc voicebook

# Check ingress
kubectl get ingress voicebook-ingress

# View logs
kubectl logs -f -l app=voicebook

# Describe deployment
kubectl describe deployment voicebook
```

### Access the Application

**Via LoadBalancer:**
```bash
# Get external IP
kubectl get svc voicebook

# Access via browser
http://<EXTERNAL-IP>
```

**Via Port Forward (for testing):**
```bash
kubectl port-forward svc/voicebook 8501:80

# Access via browser
http://localhost:8501
```

**Via Ingress:**
```bash
# Get ingress address
kubectl get ingress voicebook-ingress

# Configure DNS to point to ingress address
# Access via configured domain: https://voicebook.example.com
```

### Kubernetes Management

**Scaling:**
```bash
# Manual scaling
kubectl scale deployment voicebook --replicas=5

# Autoscaling is configured via HPA (see k8s/hpa.yml)
kubectl get hpa voicebook-hpa
```

**Updates:**
```bash
# Rolling update with new image
kubectl set image deployment/voicebook \
  voicebook=ghcr.io/YOUR_USERNAME/voicebook:v1.1.0

# Check rollout status
kubectl rollout status deployment/voicebook

# Rollback if needed
kubectl rollout undo deployment/voicebook

# View rollout history
kubectl rollout history deployment/voicebook
```

**Health Checks:**
```bash
# Check pod health
kubectl get pods -l app=voicebook

# Describe pod to see health check status
kubectl describe pod <pod-name>

# View events
kubectl get events --sort-by='.metadata.creationTimestamp'
```

**Resource Usage:**
```bash
# View resource usage
kubectl top pods -l app=voicebook

# View node usage
kubectl top nodes
```

### Cloud-Specific Deployment

#### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name voicebook-cluster \
  --region us-east-1 \
  --nodes 3 \
  --node-type t3.medium

# Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name voicebook-cluster

# Deploy
kubectl apply -f k8s/

# Install AWS Load Balancer Controller (for ingress)
# https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html
```

#### Google GKE

```bash
# Create GKE cluster
gcloud container clusters create voicebook-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2

# Get credentials
gcloud container clusters get-credentials voicebook-cluster \
  --zone us-central1-a

# Deploy
kubectl apply -f k8s/
```

#### Azure AKS

```bash
# Create resource group
az group create --name voicebook-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group voicebook-rg \
  --name voicebook-cluster \
  --node-count 3 \
  --node-vm-size Standard_D2_v2

# Get credentials
az aks get-credentials \
  --resource-group voicebook-rg \
  --name voicebook-cluster

# Deploy
kubectl apply -f k8s/
```

---

## 🔒 Container Security

### Security Scanning

**Trivy (Vulnerability Scanner):**
```bash
# Scan local image
trivy image voicebook:latest

# Scan with severity filter
trivy image --severity HIGH,CRITICAL voicebook:latest

# Generate report
trivy image --format json --output trivy-report.json voicebook:latest
```

**Grype (Alternative Scanner):**
```bash
grype voicebook:latest
```

**Hadolint (Dockerfile Linter):**
```bash
hadolint Dockerfile
```

**Dockle (Container Linter):**
```bash
dockle voicebook:latest
```

### Security Best Practices

Our Docker image implements security best practices:

✅ **Multi-stage builds** - Smaller final image, fewer vulnerabilities
✅ **Non-root user** - Runs as user `voicebook` (UID 1000)
✅ **Minimal base image** - Python 3.11-slim (Debian-based)
✅ **No unnecessary packages** - Only runtime dependencies
✅ **Read-only filesystem** - Where possible
✅ **Health checks** - Built-in liveness/readiness probes
✅ **Security scanning** - Automated in CI/CD

**Kubernetes Security:**
✅ **Security contexts** - runAsNonRoot, drop capabilities
✅ **RBAC** - Least privilege service accounts
✅ **Network policies** - Control pod-to-pod communication
✅ **Pod security standards** - Restricted profile
✅ **Secrets management** - External Secrets Operator compatible
✅ **Resource limits** - Prevent resource exhaustion

### Vulnerability Management

**Automated Scanning:**
- GitHub Actions scans on every build
- Weekly scheduled scans
- Results in Security tab

**Response Process:**
1. Review security alerts
2. Check severity and exploitability
3. Update dependencies if needed
4. Rebuild and redeploy image
5. Verify fix with rescan

---

## 🏭 Production Best Practices

### Image Management

**Tagging Strategy:**
```bash
# Use semantic versioning
docker tag voicebook:latest voicebook:1.0.0
docker tag voicebook:latest voicebook:1.0
docker tag voicebook:latest voicebook:1

# Tag with git commit
docker tag voicebook:latest voicebook:$(git rev-parse --short HEAD)

# Tag with timestamp
docker tag voicebook:latest voicebook:$(date +%Y%m%d-%H%M%S)
```

**Registry Best Practices:**
- Use private registry for production
- Enable vulnerability scanning
- Use image signing (cosign, Notary)
- Implement retention policies
- Use pull-through cache

### Resource Optimization

**Image Size:**
```bash
# Check image size
docker images voicebook:latest

# Analyze layers with dive
dive voicebook:latest

# Multi-platform builds
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t voicebook:latest .
```

**Layer Caching:**
- Order Dockerfile instructions by change frequency
- Copy requirements.txt before source code
- Use `.dockerignore` to exclude unnecessary files

### Monitoring & Logging

**Docker Logging:**
```bash
# Configure logging driver
docker run -d \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  voicebook:latest
```

**Kubernetes Logging:**
```yaml
# In deployment.yml, logs are sent to stdout/stderr
# Use log aggregation tools:
# - ELK Stack (Elasticsearch, Logstash, Kibana)
# - Loki + Grafana
# - CloudWatch (AWS)
# - Cloud Logging (GCP)
# - Azure Monitor (Azure)
```

### Backup & Disaster Recovery

**Cache Persistence:**
```bash
# Backup cache directory
docker run --rm \
  -v $(pwd)/cache:/backup \
  -v voicebook_cache:/data \
  alpine tar czf /backup/cache-backup.tar.gz -C /data .

# Restore cache
docker run --rm \
  -v $(pwd)/cache-backup.tar.gz:/backup.tar.gz \
  -v voicebook_cache:/data \
  alpine tar xzf /backup.tar.gz -C /data
```

**Kubernetes Backup:**
```bash
# Backup PVC using Velero
velero backup create voicebook-backup \
  --include-namespaces default \
  --include-resources pvc,pv

# Restore
velero restore create --from-backup voicebook-backup
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Container won't start**

```bash
# Check logs
docker logs voicebook

# Common causes:
# - Missing API key
# - Permission issues
# - Port already in use

# Solution:
docker run -d \
  -p 8502:8501 \  # Try different port
  -e OPENAI_API_KEY=your-key \
  voicebook:latest
```

**2. Application not accessible**

```bash
# Check if container is running
docker ps

# Check port mapping
docker port voicebook

# Check firewall
sudo ufw status

# Test from inside container
docker exec -it voicebook curl localhost:8501/_stcore/health
```

**3. High memory usage**

```bash
# Set memory limits
docker run -d \
  --memory=1g \
  --memory-swap=1g \
  voicebook:latest

# In Kubernetes (already configured in deployment.yml):
# resources:
#   limits:
#     memory: "1Gi"
```

**4. Cache not persisting**

```bash
# Ensure volume is mounted correctly
docker run -d \
  -v $(pwd)/cache:/app/cache:rw \  # :rw for read-write
  voicebook:latest

# Check permissions
ls -la cache/
```

### Debugging

**Interactive Shell:**
```bash
# Docker
docker exec -it voicebook bash

# Kubernetes
kubectl exec -it <pod-name> -- bash
```

**Check Environment:**
```bash
# List environment variables
docker exec voicebook env

# Kubernetes
kubectl exec <pod-name> -- env
```

**Network Debugging:**
```bash
# Test connectivity
docker exec voicebook curl https://api.openai.com/v1/models

# Check DNS
docker exec voicebook nslookup api.openai.com
```

### Performance Tuning

**CPU Optimization:**
```bash
# Limit CPU usage
docker run -d \
  --cpus=2 \
  voicebook:latest
```

**I/O Optimization:**
```bash
# Use faster storage driver
docker run -d \
  --storage-opt size=20G \
  voicebook:latest
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Container Security Best Practices](https://sysdig.com/blog/dockerfile-best-practices/)

---

## 🆘 Support

For issues related to:
- **Docker builds:** Check Dockerfile and build logs
- **Kubernetes deployment:** Check pod events and logs
- **Application errors:** Check application logs
- **Security issues:** Run security scans

Report issues: https://github.com/eteka/Voicebook/issues

---

**Last Updated:** 2025
**Docker Version:** 20.10+
**Kubernetes Version:** 1.25+
