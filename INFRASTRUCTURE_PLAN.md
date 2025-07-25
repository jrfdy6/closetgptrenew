# ClosetGPT Infrastructure Plan & Architecture

## 🏗️ Current Stack Analysis

### Frontend
- **Framework**: Next.js 14 (React)
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: React hooks + context
- **Analytics**: Custom analytics system (no external SDKs)
- **Build Tool**: Vite/Turbopack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Firebase Firestore (NoSQL)
- **Authentication**: Firebase Auth + JWT
- **File Storage**: Firebase Storage
- **AI Services**: OpenAI GPT-4 Vision + CLIP
- **Image Processing**: PIL, OpenCV
- **Monitoring**: Custom logging + analytics

### DevOps
- **Containerization**: Docker + docker-compose
- **CI/CD**: GitHub Actions
- **Reverse Proxy**: Nginx
- **Process Manager**: PM2 (Node.js)

---

## 🚀 Production Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PRODUCTION INFRASTRUCTURE                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CDN/EDGE      │    │   LOAD BALANCER │    │   FIREWALL      │
│   (Cloudflare)  │◄──►│   (Nginx/ALB)   │◄──►│   (WAF)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   FRONTEND      │    │   BACKEND API   │    │   STATIC ASSETS │         │
│  │   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Images/CSS)  │         │
│  │   Port: 3000    │    │   Port: 3001    │    │   Port: 80      │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   FIRESTORE     │    │   FIREBASE      │    │   FIREBASE      │         │
│  │   (Database)    │◄──►│   AUTH          │◄──►│   STORAGE       │         │
│  │   (NoSQL)       │    │   (Users)       │    │   (Images)      │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL SERVICES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   OPENAI API    │    │   WEATHER API   │    │   MONITORING    │         │
│  │   (GPT-4)       │◄──►│   (OpenWeather) │◄──►│   (Sentry/Logs) │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Recommended Cloud Providers

### Option 1: Google Cloud Platform (Recommended)
**Why GCP?** Native Firebase integration, excellent AI/ML services, cost-effective

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              GCP ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cloud CDN     │    │   Load Balancer │    │   Cloud Armor   │
│   (Static)      │◄──►│   (HTTPS)       │◄──►│   (WAF)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              COMPUTE ENGINE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   Frontend      │    │   Backend       │    │   Monitoring    │         │
│  │   (GCE VM)      │◄──►│   (GCE VM)      │◄──►│   (Stackdriver) │         │
│  │   n1-standard-2 │    │   n1-standard-4 │    │   (Logs)        │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FIREBASE SUITE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   Firestore     │    │   Auth          │    │   Storage       │         │
│  │   (Database)    │◄──►│   (Users)       │◄──►│   (Images)      │         │
│  │   (Auto-scaling)│    │   (JWT)         │    │   (CDN)         │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Option 2: AWS (Alternative)
**Why AWS?** Extensive services, mature ecosystem, global presence

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS ARCHITECTURE                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CloudFront    │    │   ALB           │    │   WAF           │
│   (CDN)         │◄──►│   (HTTPS)       │◄──►│   (Security)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ECS/FARGATE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   Frontend      │    │   Backend       │    │   Monitoring    │         │
│  │   (Container)   │◄──►│   (Container)   │◄──►│   (CloudWatch)  │         │
│  │   (Auto-scaling)│    │   (Auto-scaling)│    │   (Logs)        │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FIREBASE SUITE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   Firestore     │    │   Auth          │    │   Storage       │         │
│  │   (Database)    │◄──►│   (Users)       │◄──►│   (Images)      │         │
│  │   (External)    │    │   (JWT)         │    │   (CDN)         │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Infrastructure Components

### 1. Container Orchestration
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://api.closetgpt.com
    restart: unless-stopped
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "3001:3001"
    environment:
      - ENVIRONMENT=production
      - FIREBASE_PROJECT_ID=closetgpt-prod
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

### 2. Nginx Configuration
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:3001;
    }

    server {
        listen 80;
        server_name closetgpt.com www.closetgpt.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name closetgpt.com www.closetgpt.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health checks
        location /health {
            proxy_pass http://backend/health;
        }
    }
}
```

### 3. Environment Configuration
```bash
# .env.production
# Frontend
NEXT_PUBLIC_API_URL=https://api.closetgpt.com
NEXT_PUBLIC_FIREBASE_API_KEY=your_firebase_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=closetgpt.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=closetgpt-prod

# Backend
ENVIRONMENT=production
FIREBASE_PROJECT_ID=closetgpt-prod
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@closetgpt.iam.gserviceaccount.com
OPENAI_API_KEY=your_openai_api_key
JWT_SECRET_KEY=your_jwt_secret_key
CORS_ORIGINS=https://closetgpt.com,https://www.closetgpt.com
```

---

## 🚀 Deployment Strategy

### 1. CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Backend Tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
      - name: Run Frontend Tests
        run: |
          cd frontend
          npm install
          npm run test

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker images
        run: |
          docker build -t closetgpt-frontend ./frontend
          docker build -t closetgpt-backend ./backend
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push closetgpt-frontend:latest
          docker push closetgpt-backend:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deploy to your cloud provider
          # This varies by provider
```

### 2. Blue-Green Deployment
```bash
# deployment script
#!/bin/bash

# Deploy new version
docker-compose -f docker-compose.prod.yml up -d --no-deps backend

# Health check
for i in {1..30}; do
  if curl -f http://localhost:3001/health; then
    echo "Backend healthy"
    break
  fi
  sleep 2
done

# Deploy frontend
docker-compose -f docker-compose.prod.yml up -d --no-deps frontend

# Rollback if needed
if [ $? -ne 0 ]; then
  echo "Deployment failed, rolling back..."
  docker-compose -f docker-compose.prod.yml up -d --no-deps backend:previous
fi
```

---

## 📊 Monitoring & Observability

### 1. Application Monitoring
```python
# backend/src/core/monitoring.py
import logging
from prometheus_client import Counter, Histogram, Gauge
from functools import wraps
import time

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
OUTFIT_GENERATIONS = Counter('outfit_generations_total', 'Total outfit generations')

def monitor_request(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            REQUEST_COUNT.labels(method='GET', endpoint=func.__name__, status=200).inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(method='GET', endpoint=func.__name__, status=500).inc()
            raise
        finally:
            REQUEST_DURATION.observe(time.time() - start_time)
    return wrapper
```

### 2. Infrastructure Monitoring
```yaml
# monitoring/docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

  alertmanager:
    image: prom/alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
```

---

## 🔒 Security Hardening

### 1. Network Security
```bash
# Firewall rules (iptables)
# Allow only necessary ports
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -j DROP
```

### 2. SSL/TLS Configuration
```nginx
# SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### 3. Secret Management
```bash
# Use environment variables or secret management service
# Never commit secrets to git
export FIREBASE_PRIVATE_KEY="$(cat /path/to/private-key.json)"
export OPENAI_API_KEY="sk-..."
export JWT_SECRET_KEY="$(openssl rand -hex 32)"
```

---

## 💰 Cost Optimization

### 1. Resource Sizing
```yaml
# Resource limits
services:
  frontend:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'

  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
```

### 2. Auto-scaling
```yaml
# Auto-scaling configuration
services:
  backend:
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

---

## 📋 Implementation Checklist

### Phase 1: Foundation
- [ ] Set up cloud provider account (GCP/AWS)
- [ ] Configure domain and DNS
- [ ] Set up SSL certificates
- [ ] Create production environment variables
- [ ] Configure Firebase project for production

### Phase 2: Infrastructure
- [ ] Deploy Docker containers
- [ ] Configure Nginx reverse proxy
- [ ] Set up load balancer
- [ ] Configure auto-scaling
- [ ] Set up monitoring and alerting

### Phase 3: Security
- [ ] Configure firewall rules
- [ ] Set up WAF (Web Application Firewall)
- [ ] Implement secret management
- [ ] Configure backup strategies
- [ ] Set up disaster recovery

### Phase 4: Optimization
- [ ] Configure CDN for static assets
- [ ] Optimize database queries
- [ ] Set up caching strategies
- [ ] Monitor and optimize costs
- [ ] Performance testing

---

## 🎯 Next Steps

1. **Choose your cloud provider** (GCP recommended for Firebase integration)
2. **Set up domain and DNS** (closetgpt.com)
3. **Configure production environment** variables
4. **Deploy using Docker** containers
5. **Set up monitoring** and alerting
6. **Configure auto-scaling** based on traffic
7. **Implement backup** and disaster recovery

Would you like me to help you implement any specific part of this infrastructure plan? 