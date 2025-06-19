# AI HR System – Fullstack Hackathon Template

Welcome! This is a modern, production-ready template for building AI-powered HR systems with a FastAPI backend and Streamlit frontend. It's designed for rapid hackathon development, local Docker use, and easy Google Cloud deployment.

---

## 🚦 What is this?
- **Backend:** FastAPI (Python 3.11)
- **Frontend:** Streamlit
- **Dev Experience:** VS Code Dev Container, pre-commit hooks, uv for Python deps
- **Deployment:** Docker Compose (local), Google Cloud Run (prod)
- **CI/CD:** GitHub Actions ready

---

## 🏁 Systematic Setup & Development Guide

### 1. **Clone and Bootstrap**
```bash
git clone https://github.com/e-candeloro/Credem_Hack_2025.git
cd Credem_Hack_2025
cp env.example .env
```

### 2. **Install [uv](https://astral.sh/docs/uv/installation/)** (if not using the Dev Container)
- Recommended: [uv official install guide](https://astral.sh/docs/uv/installation/)
- Example (Linux/macOS):
  ```bash
  curl -Ls https://astral.sh/uv/install.sh | sh
  # or use pipx: pipx install uv
  ```
- Confirm:
  ```bash
  uv --version
  ```

### 3. **Sync Python Environment**
```bash
uv sync
```
- This installs all dependencies from `pyproject.toml` and locks them for reproducibility.

### 4. **Install and Set Up pre-commit**
```bash
uv pip install pre-commit
pre-commit install
```
- This ensures code quality and formatting are checked before every commit.
- To run all checks manually:
  ```bash
  pre-commit run --all-files
  ```

### 5. **Run Locally with Docker (Recommended)**
```bash
docker compose up -d --build
```
- Backend: http://localhost:8000
- Frontend: http://localhost:8501

### 6. **(Optional) Local Python Dev (without Docker)**
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
uv run streamlit run frontend/Home.py --server.port 8501 --server.address 0.0.0.0
```

---

## 🗂️ Project Structure
```
├── app/           # FastAPI backend
├── frontend/      # Streamlit UI
├── notebooks/     # Jupyter notebooks (prototyping, data science)
├── data/          # Data files (gitignored)
├── media/         # Images, videos, media assets
├── .devcontainer/ # VS Code dev container
├── Dockerfile     # Backend Dockerfile
├── docker-compose.yaml
├── env.example    # Example .env file
├── documents/     # Extra guides (deployment, troubleshooting)
└── ...
```

---

## ⚡ Quick Links
- [uv Installation Guide](https://astral.sh/docs/uv/installation/)
- [Deployment to Google Cloud](documents/DEPLOYMENT_GCLOUD.md)
- [Troubleshooting Guide](documents/TROUBLESHOOTING.md)

---

## 🛠️ Development & Collaboration Workflow
- **Edit `.env` for your settings** (never commit secrets)
- **Use `pre-commit` for code quality**: `pre-commit run --all-files`
- **Run tests and linting**: `pre-commit run --all-files`
- **Rebuild Docker if needed**: `docker compose up -d --build`
- **Check logs**: `docker compose logs -f`
- **Jupyter notebooks**: Place in `notebooks/` (not tracked by Docker)
- **Data files**: Place in `data/` (ignored by git and gcloud)
- **Media assets**: Place in `media/`
- **Reproducibility**: All dependencies are managed by `uv` and locked in `uv.lock`.
- **Dev Container**: Use `.devcontainer/` for a fully reproducible VS Code environment.

---

## 🔐 Environment Variables
- All config is managed via `.env` (see `env.example`)
- Never commit secrets! Use Google Secret Manager in production

---

## 🤝 Contributing
- Fork, branch, and PR as usual
- Use pre-commit and uv for all changes
- See [CONTRIBUTING.md](documents/CONTRIBUTING.md) (if present)

---

## 📄 License
This project is created for hackathon purposes. See LICENSE for details.

---

**Happy Hacking! 🚀**
