# FastAPI Metrics Monitoring System - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the FastAPI Metrics Monitoring System in various environments, from local development to production Kubernetes clusters.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Monitoring Setup](#monitoring-setup)
- [Security Considerations](#security-considerations)
- [Performance Tuning](#performance-tuning)
- [Backup and Recovery](#backup-and-recovery)

## Prerequisites

### System Requirements

**Minimum Requirements**:
- CPU: 1 core
- RAM: 512 MB
- Storage: 2 GB
- Network: Internet access for Docker images

**Recommended Requirements**:
- CPU: 2 cores
- RAM: 2 GB
- Storage: 10 GB
- Network: Stable internet connection

**Production Requirements**:
- CPU: 4 cores
- RAM: 4 GB
- Storage: 50 GB SSD
- Network: High-bandwidth, low-latency connection

### Software Dependencies

**Required**:
- Docker 20.10+
- Docker Compose 2.0+
- Git (for cloning repository)

**Optional**:
- Python 3.8+ (for local development)
- kubectl (for Kubernetes deployment)
- Helm 3.0+ (for Kubernetes package management)

### Port Requirements

Ensure the following ports are available:
- **8000**: FastAPI application
- **9090**: Prometheus
- **3000**: Grafana
- **9100**: Node Exporter (optional)

## Local Development

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd fastapi-metrics-app

# Start the development environment
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### Development with Hot Reloading

```bash
# Create environment file
cp .env.example .env

# Edit configuration for development
cat > .env << EOF
DEBUG=true
METRICS_COLLECTION_INTERVAL=5
CORS_ORIGINS=*
EOF

# Start with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### Native Python Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DEBUG=true
export METRICS_COLLECTION_INTERVAL=5

# Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker Deployment

### Single Container Deployment

```bash
# Build the application image
docker build -t fastapi-metrics-app:latest .

# Run the application container
docker run -d \
  --name fastapi-app \
  -p 8000:8000 \
  -e DEBUG=false \
  -e METRICS_COLLECTION_INTERVAL=10 \
  fastapi-metrics-app:latest

# Check container status
docker ps
docker logs fastapi-app
```

### Multi-Container Deployment with Docker Compose

```bash
# Clone and navigate to project
git clone <repository-url>
cd fastapi-metrics-app

# Create production environment file
cat > .env << EOF
DEBUG=false
METRICS_COLLECTION_INTERVAL=15
CORS_ORIGINS=https://yourdomain.com
GF_SECURITY_ADMIN_PASSWORD=your-secure-password
EOF

# Start the complete stack
docker-compose up -d

# Verify all services are healthy
docker-compose ps
docker-compose logs --tail=50

# Scale the application if needed
docker-compose up -d --scale fastapi-app=3
```

### Docker Compose with External Networks

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  fastapi-app:
    build: .
    networks:
      - monitoring
      - external-network
    environment:
      - DEBUG=false
      - METRICS_COLLECTION_INTERVAL=30

networks:
  monitoring:
    driver: bridge
  external-network:
    external: true
    name: production-network
```

```bash
# Deploy with external network
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Production Deployment

### Production Environment Setup

```bash
# Create production directory
sudo mkdir -p /opt/fastapi-metrics-app
cd /opt/fastapi-metrics-app

# Clone repository
sudo git clone <repository-url> .

# Set proper ownership
sudo chown -R $USER:$USER .

# Create production environment file
sudo tee .env << EOF
DEBUG=false
METRICS_COLLECTION_INTERVAL=30
CORS_ORIGINS=https://api.yourdomain.com,https://app.yourdomain.com
GF_SECURITY_ADMIN_PASSWORD=$(openssl rand -base64 32)
PROMETHEUS_RETENTION_TIME=30d
PROMETHEUS_RETENTION_SIZE=5GB
EOF

# Set secure permissions
sudo chmod 600 .env
```

### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  fastapi-app:
    build: .
    restart: unless-stopped
    environment:
      - DEBUG=false
      - METRICS_COLLECTION_INTERVAL=30
    volumes:
      - ./logs:/app/logs
    networks:
      - monitoring
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  prometheus:
    image: prom/prometheus:v2.40.7
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--storage.tsdb.retention.size=5GB'
      - '--web.enable-lifecycle'
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - monitoring
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G

  grafana:
    image: grafana/grafana:9.5.2
    restart: unless-stopped
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_admin_password
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_DOMAIN=grafana.yourdomain.com
      - GF_SERVER_ROOT_URL=https://grafana.yourdomain.com
    secrets:
      - grafana_admin_password
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    networks:
      - monitoring
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    networks:
      - monitoring
    depends_on:
      - fastapi-app
      - grafana

secrets:
  grafana_admin_password:
    file: ./secrets/grafana_admin_password.txt

volumes:
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

networks:
  monitoring:
    driver: bridge
```

### Nginx Reverse Proxy Configuration

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream fastapi_backend {
        server fastapi-app:8000;
    }

    upstream grafana_backend {
        server grafana:3000;
    }

    # FastAPI Application
    server {
        listen 80;
        server_name api.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/api.yourdomain.com.crt;
        ssl_certificate_key /etc/nginx/ssl/api.yourdomain.com.key;

        location / {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # Grafana Dashboard
    server {
        listen 80;
        server_name grafana.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name grafana.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/grafana.yourdomain.com.crt;
        ssl_certificate_key /etc/nginx/ssl/grafana.yourdomain.com.key;

        location / {
            proxy_pass http://grafana_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### SSL Certificate Setup

```bash
# Using Let's Encrypt with Certbot
sudo apt-get update
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d api.yourdomain.com
sudo certbot certonly --standalone -d grafana.yourdomain.com

# Copy certificates to nginx directory
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem nginx/ssl/api.yourdomain.com.crt
sudo cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem nginx/ssl/api.yourdomain.com.key
sudo cp /etc/letsencrypt/live/grafana.yourdomain.com/fullchain.pem nginx/ssl/grafana.yourdomain.com.crt
sudo cp /etc/letsencrypt/live/grafana.yourdomain.com/privkey.pem nginx/ssl/grafana.yourdomain.com.key

# Set proper permissions
sudo chmod 644 nginx/ssl/*.crt
sudo chmod 600 nginx/ssl/*.key
```

### Production Deployment Commands

```bash
# Deploy production stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose ps
docker-compose logs --tail=100

# Test endpoints
curl -k https://api.yourdomain.com/health
curl -k https://grafana.yourdomain.com/api/health

# Monitor resource usage
docker stats
```

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
curl https://get.helm.sh/helm-v3.10.0-linux-amd64.tar.gz | tar xz
sudo mv linux-amd64/helm /usr/local/bin/

# Verify cluster access
kubectl cluster-info
```

### Namespace Setup

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fastapi-metrics
  labels:
    name: fastapi-metrics
```

```bash
kubectl apply -f k8s/namespace.yaml
```

### ConfigMap and Secrets

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-config
  namespace: fastapi-metrics
data:
  DEBUG: "false"
  METRICS_COLLECTION_INTERVAL: "30"
  CORS_ORIGINS: "https://api.yourdomain.com"
```

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: fastapi-secrets
  namespace: fastapi-metrics
type: Opaque
data:
  grafana-admin-password: <base64-encoded-password>
```

```bash
# Create secret
kubectl create secret generic fastapi-secrets \
  --from-literal=grafana-admin-password=your-secure-password \
  -n fastapi-metrics

# Apply configmap
kubectl apply -f k8s/configmap.yaml
```

### FastAPI Application Deployment

```yaml
# k8s/fastapi-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
  namespace: fastapi-metrics
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi-app
        image: fastapi-metrics-app:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: fastapi-config
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
  namespace: fastapi-metrics
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/metrics"
spec:
  selector:
    app: fastapi-app
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

### Prometheus Deployment

```yaml
# k8s/prometheus-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: fastapi-metrics
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v2.40.7
        ports:
        - containerPort: 9090
        args:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus'
          - '--storage.tsdb.retention.time=30d'
          - '--web.enable-lifecycle'
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus
        - name: prometheus-storage
          mountPath: /prometheus
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
      - name: prometheus-storage
        persistentVolumeClaim:
          claimName: prometheus-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus-service
  namespace: fastapi-metrics
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: prometheus-pvc
  namespace: fastapi-metrics
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### Grafana Deployment

```yaml
# k8s/grafana-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: fastapi-metrics
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:9.5.2
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: fastapi-secrets
              key: grafana-admin-password
        - name: GF_USERS_ALLOW_SIGN_UP
          value: "false"
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
        - name: grafana-provisioning
          mountPath: /etc/grafana/provisioning
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: grafana-storage
        persistentVolumeClaim:
          claimName: grafana-pvc
      - name: grafana-provisioning
        configMap:
          name: grafana-provisioning
---
apiVersion: v1
kind: Service
metadata:
  name: grafana-service
  namespace: fastapi-metrics
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: grafana-pvc
  namespace: fastapi-metrics
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### Ingress Configuration

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-ingress
  namespace: fastapi-metrics
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    - grafana.yourdomain.com
    secretName: fastapi-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fastapi-service
            port:
              number: 80
  - host: grafana.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            nam
(Content truncated due to size limit. Use line ranges to read in chunks)