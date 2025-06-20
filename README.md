# AI HR System – Fullstack Hackathon Template

Welcome! This is a modern, production-ready template for building AI-powered HR systems with a FastAPI backend and Streamlit frontend. It's designed for rapid hackathon development, local Docker use, and easy Google Cloud deployment.

---

## 🚦 What is this?
- **Backend:** FastAPI (Python 3.11) with AI/LLM integration
- **Frontend:** Streamlit
- **AI/LLM:** LangChain, LangGraph, Groq, Google AI, Ollama support
- **Dev Experience:** VS Code Dev Container, pre-commit hooks, uv for Python deps
- **Deployment:** Docker Compose (local), Google Cloud Run (prod)
- **CI/CD:** GitHub Actions ready

---

## 🏁 Quick Start with Docker

### Option 1: Docker Compose (Recommended for Development)
```bash
# Clone the repository
git clone https://github.com/e-candeloro/Credem_Hack_2025.git
cd Credem_Hack_2025

# Copy environment file
cp env.example .env

# Start all services
docker compose up -d --build

# Check logs
docker compose logs -f

# Stop services
docker compose down
```

**Services available:**
- Backend API: http://localhost:8000
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs

### Option 2: Standalone Docker Container
```bash
# Build the Docker image
docker build -t ai-hr-system .

# Run the container
docker run -it --env-file .env ai-hr-system

# Or run in detached mode
docker run -d --env-file .env -p 8000:8000 ai-hr-system
```

---

## 🛠️ Development Setup

### Prerequisites
- Python 3.11+
- [uv](https://astral.sh/docs/uv/installation/) (recommended package manager)
- Docker and Docker Compose (for containerized development)

### 1. **Clone and Bootstrap**
```bash
git clone https://github.com/e-candeloro/Credem_Hack_2025.git
cd Credem_Hack_2025
cp env.example .env
```

### 2. **Install uv** (if not using the Dev Container)
```bash
# Linux/macOS
curl -Ls https://astral.sh/uv/install.sh | sh

# Or using pipx
pipx install uv

# Verify installation
uv --version
```

### 3. **Set Up Python Environment**
```bash
# Install all dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### 4. **Install pre-commit hooks**
```bash
uv pip install pre-commit
pre-commit install

# Run all checks manually
pre-commit run --all-files
```

### 5. **Environment Configuration**
Edit `.env` file with your configuration:
```bash
# Required for AI features
LLM_MODEL=placeholder

# Optional: Google Cloud settings
GOOGLE_API_KEY=your_google_api_key_here
PROJECT_ID=your_gcp_project_id
```

### 6. **Run Locally (Development Mode)**

#### Backend Only
```bash
# Using uv
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Only
```bash
# Navigate to frontend directory (if it exists)
cd frontend
uv run streamlit run Home.py --server.port 8501 --server.address 0.0.0.0
```

#### Full Stack (Docker Compose)
```bash
docker compose up -d --build
```

---

## 🗂️ Project Structure
```
├── app/                    # FastAPI backend application
│   ├── api/               # API endpoints and routes
│   │   └── v1/
│   │       └── endpoints/ # API endpoint modules
│   ├── core/              # Core application modules
│   │   ├── agent/         # AI agent implementation
│   │   ├── llm/           # LLM factory and configuration
│   │   ├── config.py      # Application settings
│   │   └── database.py    # Database configuration
│   ├── etl/               # ETL pipeline modules
│   ├── ocr/               # Document processing
│   ├── schemas/           # Pydantic models
│   ├── tests/             # Backend tests
│   ├── config.py          # Configuration loading
│   ├── gcs_utils.py       # Google Cloud Storage utilities
│   ├── exporter.py        # Data export utilities
│   └── main.py            # FastAPI application entry point
├── data/                  # Data files (gitignored)
├── documents/             # Documentation and guides
├── media/                 # Media assets
├── notebooks/             # Jupyter notebooks for prototyping
├── tests/                 # Integration tests
├── Dockerfile             # Backend Docker configuration
├── docker-compose.yaml    # Multi-service Docker setup
├── env.example            # Environment variables template
├── pyproject.toml         # Python project configuration
├── requirements.txt       # Legacy requirements (for compatibility)
└── README.md              # This file
```

---

## 🤖 AI/LLM Features

### Supported LLM Providers
- **Groq** (recommended for speed)
- **Google AI** (Gemini models)
- **Ollama** (local models)

### Configuration
Set your preferred LLM in `.env`:
```bash
LLM_VENDOR=groq                    # groq, google, or ollama
LLM_MODEL=llama3-70b-8192         # Model name
LLM_API_KEY=your_api_key_here     # API key for the provider
```

### Available AI Tools
- **Search**: DuckDuckGo web search
- **Wikipedia**: Wikipedia article search
- **Calculator**: Mathematical expression evaluation
- **Database Query**: Placeholder for future database integration

---

## 🧪 Testing

### Run Tests
```bash
# Using uv
uv run pytest

# Or using Python directly
python -m pytest

# Run with coverage
uv run pytest --cov=app
```

### Integration Tests
```bash
uv run pytest tests/integration/
```

---

## 🚀 Deployment

### Local Docker Deployment
```bash
# Build and run with Docker Compose
docker compose up -d --build

# Or build standalone image
docker build -t ai-hr-system .
docker run -d --env-file .env -p 8000:8000 ai-hr-system
```

### Google Cloud Deployment
See [DEPLOYMENT_GCLOUD.md](documents/DEPLOYMENT_GCLOUD.md) for detailed instructions.

---

## 🔐 Environment Variables

### Required Variables
```bash
# LLM Configuration
LLM_API_KEY=your_api_key_here
LLM_VENDOR=groq
LLM_MODEL=llama3-70b-8192

# Application Settings
APP_NAME="AI HR System"
DEBUG=false
ENVIRONMENT=development
```

### Optional Variables
```bash
# Google Cloud (for production features)
PROJECT_ID=your_gcp_project_id
GOOGLE_API_KEY=your_google_api_key
INPUT_BUCKET=your_input_bucket
OUTPUT_BUCKET=your_output_bucket

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

---

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `uv run pytest`
5. Run pre-commit: `pre-commit run --all-files`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to your fork: `git push origin feature/your-feature`
8. Create a Pull Request

### Code Quality
- Use pre-commit hooks for automatic formatting and linting
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed

---

## 📄 License
This project is created for hackathon purposes. See LICENSE for details.

---

**Happy Hacking! 🚀**
