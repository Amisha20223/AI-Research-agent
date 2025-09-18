# Deployment Guide

This guide provides detailed instructions for deploying the AI Research Agent to various cloud platforms.

## 🏗️ Architecture Decisions

### Technology Stack Rationale

- **FastAPI**: High-performance Python web framework with automatic API documentation
- **PostgreSQL**: Robust relational database with excellent JSON support
- **Redis**: In-memory data store for Celery message brokering and caching
- **Celery**: Distributed task queue for background processing
- **Next.js**: React framework with excellent developer experience and deployment options
- **Docker**: Containerization for consistent deployments across environments

### Scalability Considerations

- **Horizontal Scaling**: Multiple Celery workers can be deployed
- **Database Optimization**: Indexed queries and connection pooling
- **Caching Strategy**: Redis for session storage and API response caching
- **Load Balancing**: Nginx reverse proxy with upstream configuration

## 🚀 Cloud Platform Deployments

### 1. Vercel + Railway (Recommended)

**Frontend on Vercel, Backend on Railway**

#### Vercel Setup (Frontend)

1. **Connect Repository**
   \`\`\`bash
   # Push your code to GitHub
   git push origin main
   \`\`\`

2. **Import to Vercel**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Framework Preset: Next.js
   - Root Directory: `.` (default)

3. **Environment Variables**
   \`\`\`
   NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app
   \`\`\`

4. **Deploy**
   - Automatic deployment on every push to main branch

#### Railway Setup (Backend)

1. **Create Railway Account**
   - Go to https://railway.app
   - Connect your GitHub account

2. **Deploy Services**

   **PostgreSQL Database:**
   \`\`\`bash
   # Add PostgreSQL service
   railway add postgresql
   \`\`\`

   **Redis Service:**
   \`\`\`bash
   # Add Redis service
   railway add redis
   \`\`\`

   **Backend API:**
   \`\`\`bash
   # Create new service from GitHub repo
   # Set build command: pip install -r backend/requirements.txt
   # Set start command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   \`\`\`

   **Celery Worker:**
   \`\`\`bash
   # Create new service from same repo
   # Set build command: pip install -r backend/requirements.txt
   # Set start command: cd backend && celery -A celery_app worker --loglevel=info
   \`\`\`

   **Celery Beat:**
   \`\`\`bash
   # Create new service from same repo
   # Set build command: pip install -r backend/requirements.txt
   # Set start command: cd backend && celery -A celery_app beat --loglevel=info
   \`\`\`

3. **Environment Variables** (for all backend services)
   \`\`\`
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   CELERY_BROKER_URL=${{Redis.REDIS_URL}}
   CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
   NEWS_API_KEY=your_news_api_key
   ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
   \`\`\`

### 2. Render Deployment

#### Backend on Render

1. **Create Web Service**
   - Connect GitHub repository
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Create Background Worker**
   - Same repository
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && celery -A celery_app worker --loglevel=info`

3. **Add PostgreSQL Database**
   - Create PostgreSQL service
   - Note the connection string

4. **Add Redis Instance**
   - Create Redis service
   - Note the connection string

5. **Environment Variables**
   \`\`\`
   DATABASE_URL=postgresql://...
   CELERY_BROKER_URL=redis://...
   CELERY_RESULT_BACKEND=redis://...
   NEWS_API_KEY=your_key
   \`\`\`

### 3. AWS Deployment

#### Using AWS ECS with Fargate

1. **Build and Push Images**
   \`\`\`bash
   # Build images
   docker build -t ai-research-backend ./backend
   docker build -t ai-research-frontend .

   # Tag for ECR
   docker tag ai-research-backend:latest 123456789.dkr.ecr.region.amazonaws.com/ai-research-backend:latest
   docker tag ai-research-frontend:latest 123456789.dkr.ecr.region.amazonaws.com/ai-research-frontend:latest

   # Push to ECR
   docker push 123456789.dkr.ecr.region.amazonaws.com/ai-research-backend:latest
   docker push 123456789.dkr.ecr.region.amazonaws.com/ai-research-frontend:latest
   \`\`\`

2. **Create ECS Task Definitions**
   \`\`\`json
   {
     "family": "ai-research-backend",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "123456789.dkr.ecr.region.amazonaws.com/ai-research-backend:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "DATABASE_URL",
             "value": "postgresql://..."
           }
         ]
       }
     ]
   }
   \`\`\`

3. **Create RDS PostgreSQL Instance**
   \`\`\`bash
   aws rds create-db-instance \
     --db-instance-identifier ai-research-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username postgres \
     --master-user-password your-password \
     --allocated-storage 20
   \`\`\`

4. **Create ElastiCache Redis Cluster**
   \`\`\`bash
   aws elasticache create-cache-cluster \
     --cache-cluster-id ai-research-redis \
     --cache-node-type cache.t3.micro \
     --engine redis \
     --num-cache-nodes 1
   \`\`\`

### 4. Google Cloud Platform

#### Using Cloud Run

1. **Build and Deploy Backend**
   \`\`\`bash
   # Build and submit to Cloud Build
   gcloud builds submit --tag gcr.io/PROJECT_ID/ai-research-backend ./backend

   # Deploy to Cloud Run
   gcloud run deploy ai-research-backend \
     --image gcr.io/PROJECT_ID/ai-research-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   \`\`\`

2. **Create Cloud SQL PostgreSQL Instance**
   \`\`\`bash
   gcloud sql instances create ai-research-db \
     --database-version=POSTGRES_13 \
     --tier=db-f1-micro \
     --region=us-central1
   \`\`\`

3. **Create Memorystore Redis Instance**
   \`\`\`bash
   gcloud redis instances create ai-research-redis \
     --size=1 \
     --region=us-central1
   \`\`\`

### 5. Azure Deployment

#### Using Container Instances

1. **Create Resource Group**
   \`\`\`bash
   az group create --name ai-research-rg --location eastus
   \`\`\`

2. **Create PostgreSQL Database**
   \`\`\`bash
   az postgres server create \
     --resource-group ai-research-rg \
     --name ai-research-db \
     --location eastus \
     --admin-user postgres \
     --admin-password your-password \
     --sku-name B_Gen5_1
   \`\`\`

3. **Create Redis Cache**
   \`\`\`bash
   az redis create \
     --resource-group ai-research-rg \
     --name ai-research-redis \
     --location eastus \
     --sku Basic \
     --vm-size c0
   \`\`\`

4. **Deploy Container Instances**
   \`\`\`bash
   az container create \
     --resource-group ai-research-rg \
     --name ai-research-backend \
     --image your-registry/ai-research-backend:latest \
     --ports 8000 \
     --environment-variables \
       DATABASE_URL="postgresql://..." \
       CELERY_BROKER_URL="redis://..."
   \`\`\`

## 🔧 Production Configuration

### Environment Variables

Create a comprehensive `.env` file for production:

\`\`\`env
# Database
DATABASE_URL=postgresql://user:password@host:5432/database
POSTGRES_DB=research_agent
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password_here

# Redis/Celery
CELERY_BROKER_URL=redis://redis-host:6379/0
CELERY_RESULT_BACKEND=redis://redis-host:6379/0

# External APIs
NEWS_API_KEY=your_news_api_key_here

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://your-frontend-domain.com

# Performance
CELERY_WORKER_CONCURRENCY=4
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
LOG_LEVEL=INFO
\`\`\`

### SSL/TLS Configuration

For production deployments, configure SSL certificates:

\`\`\`nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
}
\`\`\`

### Database Optimization

\`\`\`sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_research_topics_status_created 
ON research_topics(status, created_at DESC);

CREATE INDEX CONCURRENTLY idx_workflow_logs_topic_step 
ON workflow_logs(research_topic_id, step_number);

-- Configure PostgreSQL for production
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
\`\`\`

## 📊 Monitoring and Observability

### Health Checks

Implement comprehensive health checks:

\`\`\`python
# Add to main.py
@app.get("/health/detailed")
async def detailed_health_check():
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "celery": await check_celery_workers(),
        "external_apis": await check_external_apis()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
\`\`\`

### Logging Configuration

\`\`\`python
import logging
import sys
from pythonjsonlogger import jsonlogger

# Configure structured logging
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
\`\`\`

### Metrics and Alerting

Consider integrating with monitoring services:

- **Sentry**: Error tracking and performance monitoring
- **DataDog**: Infrastructure and application monitoring
- **New Relic**: Full-stack observability
- **Prometheus + Grafana**: Open-source monitoring stack

## 🔒 Security Best Practices

### API Security

\`\`\`python
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    # Implement token verification logic
    if not verify_jwt_token(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
\`\`\`

### Rate Limiting

\`\`\`python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/research")
@limiter.limit("10/minute")
async def create_research_topic(request: Request, ...):
    # Implementation
\`\`\`

### Database Security

\`\`\`sql
-- Create read-only user for monitoring
CREATE USER monitoring_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE research_agent TO monitoring_user;
GRANT USAGE ON SCHEMA public TO monitoring_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitoring_user;

-- Enable row-level security if needed
ALTER TABLE research_topics ENABLE ROW LEVEL SECURITY;
\`\`\`

## 🚨 Disaster Recovery

### Backup Strategy

\`\`\`bash
#!/bin/bash
# backup.sh - Automated backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup
pg_dump $DATABASE_URL > "$BACKUP_DIR/db_backup_$DATE.sql"

# Redis backup
redis-cli --rdb "$BACKUP_DIR/redis_backup_$DATE.rdb"

# Upload to cloud storage
aws s3 cp "$BACKUP_DIR/" s3://your-backup-bucket/ --recursive

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
\`\`\`

### Recovery Procedures

\`\`\`bash
# Database recovery
psql $DATABASE_URL < backup_file.sql

# Redis recovery
redis-cli --rdb backup_file.rdb

# Application recovery
docker-compose -f docker-compose.prod.yml up -d
\`\`\`

## 📈 Performance Optimization

### Caching Strategy

\`\`\`python
import redis
from functools import wraps

redis_client = redis.Redis.from_url(CELERY_BROKER_URL)

def cache_result(expiration=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator
\`\`\`

### Database Connection Pooling

\`\`\`python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
\`\`\`

This comprehensive deployment guide covers all major cloud platforms and production considerations for the AI Research Agent.
