# AI Research Agent

An intelligent research automation platform that accepts research topics, runs automated workflows, and returns structured results with detailed execution logs.

## 🏗️ Architecture Overview

\`\`\`
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   APIs          │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        │
                    ┌─────────────────┐                │
                    │   PostgreSQL    │                │
                    │   Database      │                │
                    └─────────────────┘                │
                              │                        │
                              ▼                        │
                    ┌─────────────────┐                │
                    │   Redis         │                │
                    │   (Celery)      │                │
                    └─────────────────┘                │
                              │                        │
                              ▼                        │
                    ┌─────────────────┐                │
                    │   Celery        │                │
                    │   Workers       │◄───────────────┘
                    └─────────────────┘
\`\`\`

## 🚀 Features

- **Intelligent Research Workflow**: 5-step automated research process
- **Multiple Data Sources**: Wikipedia, NewsAPI, HackerNews, Reddit integration
- **Real-time Progress Tracking**: Step-by-step workflow logs with execution times
- **Background Processing**: Celery-based asynchronous task processing
- **Modern UI**: Professional React/Next.js interface with real-time updates
- **Scalable Architecture**: Docker-based microservices architecture
- **Production Ready**: Comprehensive deployment configurations

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- PostgreSQL 15+ (if running without Docker)
- Redis 7+ (if running without Docker)

## 🛠️ Quick Start

### 1. Clone the Repository

\`\`\`bash
git clone <repository-url>
cd ai-research-agent
\`\`\`

### 2. Environment Setup

\`\`\`bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
\`\`\`

Required environment variables:
\`\`\`env
POSTGRES_PASSWORD=your_secure_password
NEWS_API_KEY=your_news_api_key_here  # Optional but recommended
\`\`\`

### 3. Start with Docker (Recommended)

\`\`\`bash
# Build and start all services
make build
make up

# Or using docker-compose directly
docker-compose up -d
\`\`\`

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Development Setup

### Backend Development

\`\`\`bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/research_agent"
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"

# Run database migrations
python -c "from database import create_tables; create_tables()"

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In separate terminals, start Celery worker and beat
celery -A celery_app worker --loglevel=info
celery -A celery_app beat --loglevel=info
\`\`\`

### Frontend Development

\`\`\`bash
# Install dependencies
npm install

# Start development server
npm run dev
\`\`\`

## 🐳 Docker Commands

### Development

\`\`\`bash
# Build all images
make build

# Start all services
make up

# View logs
make logs

# Stop all services
make down

# Clean up everything
make clean
\`\`\`

### Production

\`\`\`bash
# Start production services
make up-prod

# Monitor services
make status
make health
\`\`\`

## 📊 API Endpoints

### Research Management

- `POST /research` - Submit new research topic
- `GET /research` - List all research topics
- `GET /research/{id}` - Get detailed research results

### System

- `GET /health` - Health check endpoint

### Example API Usage

\`\`\`bash
# Submit research topic
curl -X POST "http://localhost:8000/research" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Artificial Intelligence in Healthcare"}'

# Get research results
curl "http://localhost:8000/research/1"
\`\`\`

## 🔄 Workflow Process

The AI Research Agent follows a 5-step workflow:

1. **Input Parsing**: Validates and stores the research topic
2. **Data Gathering**: Fetches articles from multiple external APIs
3. **Processing**: Summarizes articles and extracts keywords
4. **Result Persistence**: Saves processed results to database
5. **Completion**: Finalizes workflow and updates status

Each step is logged with execution time and detailed messages.

## 🌐 Deployment

### Vercel (Frontend)

1. Connect your GitHub repository to Vercel
2. Set environment variables:
   \`\`\`
   NEXT_PUBLIC_API_URL=https://your-backend-domain.com
   \`\`\`
3. Deploy automatically on push to main branch

### Railway (Backend)

1. Connect your GitHub repository to Railway
2. Set environment variables:
   \`\`\`
   DATABASE_URL=postgresql://...
   CELERY_BROKER_URL=redis://...
   NEWS_API_KEY=your_key_here
   \`\`\`
3. Deploy backend, worker, and beat as separate services

### Render (Alternative Backend)

1. Create new Web Service from GitHub
2. Set build command: `pip install -r backend/requirements.txt`
3. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Create separate Background Worker for Celery

### AWS/GCP/Azure

Use the provided `docker-compose.prod.yml` for container orchestration:

\`\`\`bash
# Deploy to cloud with Docker
docker-compose -f docker-compose.prod.yml up -d
\`\`\`

## 🔒 Security Considerations

- Set strong passwords for PostgreSQL
- Use HTTPS in production (configure SSL in nginx.conf)
- Implement rate limiting (configured in nginx.conf)
- Secure API keys and environment variables
- Regular security updates for dependencies

## 📈 Monitoring and Logging

### Health Checks

\`\`\`bash
# Check all services
make health

# Individual service health
curl http://localhost:8000/health
\`\`\`

### Logs

\`\`\`bash
# All services
make logs

# Specific services
make logs-backend
make logs-celery
\`\`\`

### Database Management

\`\`\`bash
# Database shell
make db-shell

# Backup database
make db-backup

# Restore database
make db-restore
\`\`\`

## 🧪 Testing

\`\`\`bash
# Run tests
make test

# Code quality
make lint
make format
\`\`\`

## 🔧 Configuration

### External API Keys

- **NewsAPI**: Get free API key from https://newsapi.org/
- **Wikipedia**: No API key required
- **HackerNews**: No API key required
- **Reddit**: No API key required for public posts

### Performance Tuning

- Adjust Celery worker concurrency in `docker-compose.yml`
- Configure PostgreSQL connection pooling
- Implement Redis caching for frequently accessed data
- Use CDN for static assets

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   \`\`\`bash
   # Check PostgreSQL status
   docker-compose ps postgres
   
   # View PostgreSQL logs
   docker-compose logs postgres
   \`\`\`

2. **Celery Tasks Not Processing**
   \`\`\`bash
   # Check Redis connection
   docker-compose exec redis redis-cli ping
   
   # View Celery worker logs
   docker-compose logs celery-worker
   \`\`\`

3. **Frontend API Connection Issues**
   \`\`\`bash
   # Check backend health
   curl http://localhost:8000/health
   
   # Verify CORS configuration
   \`\`\`

### Debug Mode

Enable debug logging by setting `DEBUG=true` in environment variables.

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run linting and tests
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent Python web framework
- Next.js for the React framework
- Celery for background task processing
- PostgreSQL for reliable data storage
- Redis for caching and message brokering
