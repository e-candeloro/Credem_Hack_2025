# Credem Hack 2025 - AI Document Processing Pipeline

This project is a data processing pipeline built for the Credem Hackathon 2025. It leverages Google Cloud AI services, including Document AI and Gemini, to extract information from documents and process it through an ETL pipeline.
---
## 🚦 What is this?
- **Core Engine:** Python 3.11
- **AI/OCR:** Google Document AI, Google Gemini (via LangChain)
- **Data Processing:** Pandas
- **Dev Experience:** VS Code Dev Container, pre-commit hooks, `uv` for Python dependency management.
- **Deployment:** Docker for containerization.
---
## 🏁 Quick Start with Docker

### 1. **Clone and Configure**
```bash
# Clone the repository
git clone https://github.com/e-candeloro/Credem_Hack_2025.git
cd Credem_Hack_2025
# Copy environment file and add your credentials
cp env.example .env
```
### 2. **Build and Run**
```bash
# Build the Docker image
docker build -t credem-hack-2025 .

# Run the pipeline inside the container
docker run --env-file .env credem-hack-2025
```
---
## 🛠️ Local Development Setup

### Prerequisites
- Python 3.11+
- [uv](https://astral.sh/docs/uv/installation/) (the recommended package manager)

### 1. **Clone and Bootstrap**
```bash
git clone https://github.com/e-candeloro/Credem_Hack_2025.git
cd Credem_Hack_2025
cp env.example .env
```

### 2. **Set Up Python Environment with `uv`**
```bash
# Install all dependencies from pyproject.toml
uv sync

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### 3. **Install pre-commit hooks**
This ensures code quality and formatting standards are met before committing.
```bash
# Install pre-commit into the virtual environment
uv pip install pre-commit
# Set up the git hooks
pre-commit install
# Run all checks manually on all files
pre-commit run --all-files
```

### 4. **Environment Configuration**
Edit the `.env` file with your configuration. You will need Google Cloud credentials for the pipeline to work with real data.
```env
# Google Cloud Settings
PROJECT_ID="your_gcp_project_id"
GOOGLE_API_KEY="your_google_api_key"
# Document AI Processor details
DOCAI_LOCATION="eu" # e.g. "us" or "eu"
DOCAI_PROCESSOR_ID="your_processor_id"

# GCS Buckets for file I/O
INPUT_BUCKET="your_input_bucket"
OUTPUT_BUCKET="your_output_bucket"
```

### 5. **Run the Pipeline Locally**
Execute the main script to run the entire pipeline.
```bash
python app/main.py
```
---
## 🧪 Testing
To ensure the application is working correctly, run the test suite.
### Run Tests
```bash
# Using uv
uv run pytest

# Or using Python directly from the activated venv
python -m pytest

# Run with coverage report
uv run pytest --cov=app
```
---
## 🗂️ Project Structure
```
├── app/                    # Main application source code
│   ├── etl/               # ETL pipeline modules
│   │   └── pipeline.py
│   ├── ocr/               # Document processing with Document AI
│   │   └── document_ai.py
│   ├── schemas/           # Pydantic models (if any)
│   ├── tests/             # Unit and integration tests for the app
│   ├── config.py          # Configuration loading
│   ├── exporter.py        # Data export utilities
│   ├── gcs_utils.py       # Google Cloud Storage utilities
│   └── main.py            # Main pipeline entry point
├── data/                   # Local data files (gitignored)
├── documents/              # Project documentation and specifications
├── notebooks/              # Jupyter notebooks for exploration
├── tests/                  # Higher-level integration tests
├── Dockerfile              # Docker configuration for the application
├── docker-compose.yaml     # Docker Compose for multi-service setup (if needed)
├── env.example             # Environment variables template
├── pyproject.toml          # Python project configuration and dependencies (for uv)
└── README.md               # This file
```
---
## 🔐 Environment Variables

### Required Variables
These must be set in your `.env` file for the application to run.
```env
# Google Cloud
PROJECT_ID="your_gcp_project_id"
GOOGLE_API_KEY="your_google_api_key"
DOCAI_LOCATION="eu"
DOCAI_PROCESSOR_ID="your_processor_id"

# GCS Buckets
INPUT_BUCKET="your_input_bucket"
OUTPUT_BUCKET="your_output_bucket"
```
---
## 🤝 Contributing

### Development Workflow
1.  Create a feature branch: `git checkout -b feature/your-feature`
2.  Make your changes.
3.  Ensure tests pass: `uv run pytest`
4.  Run pre-commit hooks to format and lint: `pre-commit run --all-files`
5.  Commit your changes: `git commit -m "feat: Add your amazing feature"`
6.  Push to your branch and create a Pull Request.

---
**Happy Hacking! 🚀**
