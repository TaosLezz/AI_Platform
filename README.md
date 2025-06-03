# 🚀 AI Portfolio Platform - Enterprise Edition

A comprehensive enterprise-grade AI platform with advanced MLOps capabilities, supporting multiple AI models, custom model management, and real-time analytics.

## 🌟 Features

### 🤖 AI Services
- **Image Generation** - Create stunning images from text prompts using DALL-E
- **Image Classification** - Identify objects and scenes in images with confidence scores
- **Object Detection** - Locate and identify multiple objects with bounding boxes
- **Image Segmentation** - Pixel-level image analysis and masking
- **AI Chat** - Intelligent chatbot with context-aware responses

### 🏢 Enterprise Features
- **Custom Model Management** - Upload and deploy your own PyTorch models
- **Batch Processing** - Handle thousands of files efficiently with queue management
- **A/B Testing** - Compare model performance with statistical analysis
- **Role-Based Access** - FREE, PREMIUM, DEVELOPER, and ADMIN user tiers
- **Admin Dashboard** - Complete platform management and user controls

### 📊 MLOps & Analytics
- **MLflow Integration** - Complete experiment tracking and model versioning
- **Real-time Monitoring** - System performance and health dashboards
- **Redis Caching** - Intelligent caching with hit rate optimization
- **Usage Analytics** - Detailed insights into platform usage and trends
- **Performance Metrics** - Track response times, success rates, and resource usage

### 🔐 Security & Authentication
- **JWT Authentication** - Secure token-based authentication
- **OAuth Integration** - Google and GitHub social login
- **Rate Limiting** - Role-based API rate limiting
- **File Validation** - Secure file upload with type and size validation

## 🛠 Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** with shadcn/ui components
- **TanStack Query** for data fetching and caching
- **Recharts** for analytics visualization
- **Framer Motion** for animations

### Backend
- **FastAPI** with Python 3.11+
- **SQLAlchemy** with PostgreSQL database
- **Celery** for background task processing
- **Redis** for caching and task queuing
- **MLflow** for experiment tracking
- **OpenAI API** integration

### Production Infrastructure
- **Docker** containerization
- **PostgreSQL** database
- **Redis** cache and message broker
- **Prometheus** metrics collection
- **Grafana** monitoring dashboards
- **Nginx** load balancing (optional)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (for production)

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/TaosLezz/AI_Platform.git
cd ai-showcase-platform

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` file with your settings:

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services
OPENAI_API_KEY=your-openai-api-key-here

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-here
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
GITHUB_CLIENT_ID=your-github-oauth-client-id
GITHUB_CLIENT_SECRET=your-github-oauth-client-secret

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
```

### 3. Backend Setup

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server
python main.py
```

The backend will be available at http://localhost:8000

### 4. Frontend Setup

```bash
# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at http://localhost:3000

## 🐳 Docker Deployment

### Production Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **MLflow**: http://localhost:5000
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090

### Development with Docker

```bash
# Start only infrastructure services
docker-compose up -d postgres redis mlflow

# Run backend and frontend locally
python run_fastapi.py  # Terminal 1
npm run dev           # Terminal 2
```

## 📁 Project Structure

```
├── backend/                    # FastAPI backend
│   ├── auth/                  # Authentication modules
│   ├── models/                # Database models
│   ├── routes/                # API routes
│   ├── services/              # Business logic services
│   ├── config/                # Configuration
│   └── main.py                # FastAPI application
├── client/                     # React frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   ├── pages/             # Application pages
│   │   ├── lib/               # Utilities and API client
│   │   └── store/             # State management
│   └── index.html
├── docker-compose.yml          # Production deployment
├── .env.example               # Environment template
└── README.md                  # This file
```

## 🔑 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/google` - Google OAuth
- `GET /api/v1/auth/github` - GitHub OAuth

### AI Services
- `POST /api/v1/generate` - Generate images from text
- `POST /api/v1/classify` - Classify uploaded images
- `POST /api/v1/detect` - Detect objects in images
- `POST /api/v1/segment` - Segment images
- `POST /api/v1/chat` - Chat with AI assistant

### Custom Models
- `POST /api/v1/models/upload` - Upload custom model
- `GET /api/v1/models/list` - List available models
- `POST /api/v1/models/compare` - A/B testing setup

### Batch Processing
- `POST /api/v1/batch/process` - Create batch job
- `GET /api/v1/batch/{job_id}/status` - Check job status
- `GET /api/v1/batch/{job_id}/download` - Download results

### Analytics & Monitoring
- `GET /api/v1/experiments` - MLflow experiments
- `GET /api/v1/runs` - MLflow runs
- `GET /api/v1/metrics/dashboard` - Platform analytics
- `GET /api/v1/performance/stats` - System metrics
- `GET /api/v1/cache/stats` - Cache statistics

### Admin (Admin role required)
- `GET /api/v1/admin/users` - User management
- `POST /api/v1/admin/users/{id}/role` - Update user role
- `GET /api/v1/admin/analytics` - Platform analytics
- `GET /api/v1/admin/models` - Model management

## 🎯 User Roles & Permissions

### FREE Tier
- Basic AI services (limited requests)
- Standard response times
- Community support

### PREMIUM Tier
- Higher request limits
- Priority processing
- Advanced analytics access

### DEVELOPER Tier
- Custom model uploads
- Batch processing
- A/B testing tools
- API documentation access

### ADMIN Tier
- Full platform management
- User role management
- System configuration
- Advanced monitoring

## 📊 Monitoring & Analytics

### MLflow Integration
- Experiment tracking for all AI requests
- Model versioning and comparison
- Performance metrics logging
- Artifact storage

### Real-time Dashboards
- System performance monitoring
- Cache hit rates and optimization
- User activity and service usage
- Error tracking and alerting

### Grafana Dashboards
- Infrastructure metrics
- Application performance
- Business intelligence
- Custom alerting rules

## 🔧 Configuration

### Custom Models
Supported formats:
- PyTorch (.pt, .pth)
- ONNX (.onnx)
- Safetensors (.safetensors)
- Pickle (.pkl)

Maximum model size: 5GB
Supported types: image, text, multimodal

### Batch Processing
- Maximum files per job: 1,000
- Supported formats: JPG, PNG, TXT, CSV, JSON
- Maximum total size: 1GB per job
- Output formats: JSON, CSV

### Caching Strategy
- Image classification: 7 days TTL
- Object detection: 7 days TTL
- Image generation: 3 days TTL
- Chat responses: 1 day TTL

## 🚨 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python dependencies
pip install -r backend/requirements.txt

# Verify database connection
python -c "from backend.database import engine; print('DB OK')"
```

**Frontend build errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Docker issues:**
```bash
# Reset Docker environment
docker-compose down -v
docker-compose up -d --build
```

### Performance Optimization

**Database:**
- Enable connection pooling
- Configure proper indexes
- Regular VACUUM operations

**Redis:**
- Monitor memory usage
- Configure appropriate eviction policies
- Use Redis Cluster for scaling

**MLflow:**
- Configure artifact storage (S3/GCS)
- Regular cleanup of old experiments
- Database backend for meta_data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write comprehensive tests
- Update documentation for new features

## 📄 License

This project is licensed under the Apache License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- API Documentation: http://localhost:8000/docs
- Interactive API Explorer: http://localhost:8000/redoc

### Community
- GitHub Issues for bug reports
- Discussions for feature requests
- Wiki for additional documentation

### Enterprise Support
Contact our team for:
- Custom model development
- Enterprise deployment assistance
- Training and consultation
- SLA agreements

## 🔮 Roadmap

### Version 2.1 (Coming Soon)
- [ ] Multi-tenant architecture
- [ ] Advanced model marketplace
- [ ] Real-time collaboration
- [ ] Mobile app support

### Version 2.2 (Planned)
- [ ] Edge deployment support
- [ ] Advanced security features
- [ ] Custom UI themes
- [ ] Workflow automation

---

**Built with ❤️ using FastAPI, React, and modern DevOps practices**

For questions or support, please open an issue or contact our team.