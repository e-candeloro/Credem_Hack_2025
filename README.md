# AI HR System - Hackathon Project

A simplified scaffold for an AI-powered Human Resources system built with FastAPI backend and Streamlit frontend, designed for hackathon development with Docker containerization.

## 🚀 Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Streamlit
- **Package Manager**: uv (with lock file)
- **Development**: VS Code Dev Container
- **Containerization**: Docker & Docker Compose
- **HTTP Client**: httpx (async)
- **Code Quality**: pre-commit hooks (black, isort, flake8, mypy, bandit)

## 📋 Prerequisites

### Local Development

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [VS Code](https://code.visualstudio.com/) with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) (optional)

### Alternative: Local Python Development

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Python 3.11+

## 🔧 Development Setup

### Environment Variables & Secrets Management

This project uses environment variables for configuration management across development and production environments.

#### Quick Setup

1. **Copy the example environment file:**

   ```bash
   cp env.example .env
   ```

2. **Edit `.env` with your settings:**
   ```bash
   # Edit the .env file with your configuration
   nano .env
   ```

#### Environment Variables

**Backend Configuration:**

- `APP_NAME` - Application name
- `VERSION` - Application version
- `ENVIRONMENT` - Environment (development/staging/production)
- `DEBUG` - Debug mode (true/false)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `SECRET_KEY` - Secret key for JWT tokens
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `DATABASE_URL` - Database connection string (future use)
- `OPENAI_API_KEY` - OpenAI API key (future use)
- `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated)
- `LOG_LEVEL` - Logging level (INFO/DEBUG/WARNING/ERROR)

**Frontend Configuration:**

- `STREAMLIT_SERVER_PORT` - Streamlit server port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS` - Streamlit server address (default: 0.0.0.0)
- `API_BASE_URL` - Backend API URL
- `ENVIRONMENT` - Environment (development/staging/production)
- `DEBUG` - Debug mode (true/false)

#### Development vs Production

**Development (.env file):**

```bash
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-dev-secret-key
API_BASE_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:8501,http://localhost:3000
```

**Production (Google Cloud Run):**

```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key
API_BASE_URL=https://your-api-domain.com
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

#### Google Cloud Production Setup

1. **Create a secret in Google Secret Manager:**

   ```bash
   # Create the secret
   gcloud secrets create ai-hr-secret-key --data-file=- <<< "your-super-secure-production-key"

   # Grant access to Cloud Run service account
   gcloud secrets add-iam-policy-binding ai-hr-secret-key \
     --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

2. **Update the Cloud Run configuration:**

   - Edit `gcp/run.yaml` with your project ID and domain names
   - Update the secret reference to match your secret name

3. **Deploy with environment variables:**

   ```bash
   # Deploy backend
   gcloud run deploy ai-hr-backend \
     --image gcr.io/PROJECT_ID/ai-hr-backend:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ENVIRONMENT=production,DEBUG=false

   # Deploy frontend
   gcloud run deploy ai-hr-frontend \
     --image gcr.io/PROJECT_ID/ai-hr-frontend:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ENVIRONMENT=production,DEBUG=false,API_BASE_URL=https://ai-hr-backend-xxxxx-uc.a.run.app
   ```

#### Security Best Practices

- **Never commit `.env` files** to version control (already in `.gitignore`)
- **Use strong, unique secret keys** in production
- **Rotate secrets regularly** in production environments
- **Use Google Secret Manager** for production secrets
- **Limit CORS origins** to only necessary domains
- **Disable debug mode** in production

### Dependency Management & requirements.txt

- **Automated requirements.txt**: This project uses [uv](https://docs.astral.sh/uv/) for dependency management. The `requirements.txt` file is always kept in sync automatically by pre-commit using the official [uv-export](https://github.com/astral-sh/uv-pre-commit) hook.
- **Do not manually edit `requirements.txt`**. Instead, add/remove dependencies with `uv add` or `uv remove`, then let pre-commit update `requirements.txt` for you.
- This ensures Docker and CI always use the correct, locked dependencies.

### Pre-commit Hooks Setup

This project uses pre-commit hooks to ensure code quality. Set up pre-commit after cloning:

```bash
# Install pre-commit using uv
uv add pre-commit

# Install the git hook scripts
pre-commit install

# Run against all files (optional)
pre-commit run --all-files
```

**Pre-commit hooks include:**

- **Code Formatting**: Black (code formatter)
- **Import Sorting**: isort (import organization)
- **Linting**: flake8 (style guide enforcement)
- **Type Checking**: mypy (static type checking)
- **Security**: bandit (security vulnerability scanner)
- **General Checks**: trailing whitespace, file endings, YAML validation
- **Testing**: pytest (runs tests automatically using uv)

**Pre-commit commands:**

```bash
# Run on staged files (automatic on commit)
pre-commit run

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black
pre-commit run flake8

# Update hooks to latest versions
pre-commit autoupdate
```

## 🛠️ Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd Credem_Hack_2025
   ```

2. **Build and run with Docker Compose:**

   ```bash
   # Build the images
   docker compose build

   # Start the services
   docker compose up -d
   ```

3. **Access the applications:**
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Frontend Dashboard**: http://localhost:8501

### Option 2: Local Development

1. **Install uv:**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc  # or restart terminal
   ```

2. **Install dependencies:**

   ```bash
   uv sync
   ```

3. **Run the applications:**

   ```bash
   # Terminal 1: Start backend
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Terminal 2: Start frontend
   uv run streamlit run frontend/Home.py --server.port 8501 --server.address 0.0.0.0
   ```

## 🐳 Docker Commands

### Basic Operations

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# View running services
docker compose ps

# View logs
docker compose logs
docker compose logs backend
docker compose logs frontend

# Stop services
docker compose down

# Rebuild and restart
docker compose up -d --build
```

### Development Commands

```bash
# Run in foreground (see logs)
docker compose up

# Run specific service
docker compose up backend
docker compose up frontend

# Execute commands in containers
docker compose exec backend python -c "print('Hello from backend')"
docker compose exec frontend streamlit --version
```

### Troubleshooting

```bash
# Check container health
docker compose ps

# View detailed logs
docker compose logs --tail=100

# Restart specific service
docker compose restart backend

# Remove all containers and volumes
docker compose down -v
```

> **Note:** The Docker build always uses the auto-generated `requirements.txt` (kept in sync by pre-commit and uv). You never need to manually update this file.

## 🧪 Testing

### Run tests locally:

```bash
uv run python -m pytest app/tests/ -v
```

### Test Docker setup:

```bash
# Test backend health
curl http://localhost:8000/api/v1/health

# Test frontend accessibility
curl http://localhost:8501

# Test inter-container communication
docker exec ai-hr-frontend curl http://backend:8000/api/v1/health
```

## 📁 Project Structure

```
├── app/                   # FastAPI backend
│   ├── main.py           # Application entry point
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings and environment
│   │   └── database.py   # Database configuration
│   ├── api/v1/           # API routes
│   │   └── endpoints/    # API endpoints
│   └── tests/            # Backend tests
├── frontend/             # Streamlit UI
│   ├── Home.py           # Main dashboard
│   └── Dockerfile        # Frontend container
├── .devcontainer/        # VS Code dev container
├── Dockerfile            # Backend container
├── docker-compose.yaml   # Multi-service orchestration
├── pyproject.toml        # Project dependencies (uv)
├── requirements.txt      # Dependencies for Docker
└── README.md
```

## 🔧 API Endpoints

### Health & Status

- `GET /` - Root endpoint with API information
- `GET /api/v1/health` - Health check status
- `GET /api/v1/ping` - Simple ping for load balancers

### Documentation

- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## 🎯 Frontend Features

### Dashboard

- **API Status Monitoring** - Real-time health checks
- **Metrics Display** - Response times, uptime, status
- **Quick Actions** - Refresh status, view docs

### API Health Monitor

- **Async Health Checks** - Non-blocking API calls
- **Detailed Status** - System information and checks
- **Manual Testing** - Interactive health check tools

### About Page

- **Project Information** - Tech stack and features
- **Development Guide** - Extension points and next steps

## 🔧 Development Workflow

1. **Set up pre-commit** (first time only):

   ```bash
   uv add pre-commit
   pre-commit install
   ```

2. **Make changes** to code

3. **Pre-commit runs automatically** on staged files when you commit

4. **Test locally** with `uv run python -m pytest`

5. **Rebuild Docker** if needed: `docker compose up -d --build`

6. **Check logs**: `docker compose logs -f`

**Manual pre-commit checks:**

```bash
# Run on all files
pre-commit run --all-files

# Run specific checks
pre-commit run black
pre-commit run flake8
pre-commit run mypy
```

## 🚀 Deployment

### Production Deployment

```bash
# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Build and deploy
docker compose -f docker-compose.yaml up -d
```

### Environment Variables

```bash
# Backend
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Frontend
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
API_BASE_URL=http://backend:8000
```

## 🐛 Troubleshooting

### Common Issues

**Docker containers won't start:**

```bash
# Check Docker is running
docker --version

# Check available ports
netstat -tulpn | grep :8000
netstat -tulpn | grep :8501
```

**Frontend can't reach backend:**

```bash
# Check network connectivity
docker network ls
docker network inspect credem_hack_2025_ai-hr-network

# Test inter-container communication
docker exec ai-hr-frontend curl http://backend:8000/api/v1/health
```

**Port conflicts:**

```bash
# Modify ports in docker-compose.yaml
ports:
  - "8001:8000"  # Change host port
```

### Logs and Debugging

```bash
# View all logs
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View specific service logs
docker compose logs backend --tail=50
```

## 📚 Next Steps

This scaffold is ready for extension with:

- **User Management** - Authentication and authorization
- **HR Processes** - Employee management, performance reviews
- **AI/ML Integration** - Resume parsing, skill matching
- **Database Models** - SQLAlchemy models and migrations
- **Additional APIs** - More business logic endpoints

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. **Set up pre-commit hooks:**
   ```bash
   uv add pre-commit
   pre-commit install
   ```
4. Make changes
5. **Pre-commit runs automatically** on commit
6. Test with Docker: `docker compose up -d --build`
7. Submit pull request

## 📄 License

This project is created for hackathon purposes. See LICENSE file for details.

---

**Happy Hacking! 🚀**
