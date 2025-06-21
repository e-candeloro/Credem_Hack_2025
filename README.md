# Credem Hack 2025 - AI Document Processing Pipeline

This project is a data processing pipeline built for the Credem Hackathon 2025. It leverages Google Cloud AI services, including Document AI and Gemini, to extract information from documents and process it through an ETL pipeline.
---
## 🚦 What is this?
- **Core Engine:** Python 3.11
- **AI/OCR:** Google Document AI + Google Gemini via GCP API
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
docker run credem-hack-2025
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

---

## 📄 License
This project is created for hackathon purposes. See LICENSE for details.

---

**Happy Hacking! 🚀**
