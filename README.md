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

## 🏁 How do I start?

### 1. **Clone and Setup**
```bash
git clone <your-repo-url>
cd Credem_Hack_2025
cp env.example .env
```

### 2. **Run Locally with Docker**
```bash
docker compose up -d
```
- Backend: http://localhost:8000
- Frontend: http://localhost:8501

### 3. **(Optional) Local Python Dev**
```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
uv run streamlit run frontend/Home.py --server.port 8501 --server.address 0.0.0.0
```

---

## 🗂️ Project Structure
```
├── app/           # FastAPI backend
├── frontend/      # Streamlit UI
├── .devcontainer/ # VS Code dev container
├── Dockerfile     # Backend Dockerfile
├── docker-compose.yaml
├── env.example    # Example .env file
├── documents/     # Extra guides (deployment, troubleshooting)
└── ...
```

---

## ⚡ Quick Links
- [Deployment to Google Cloud](documents/DEPLOYMENT_GCLOUD.md)
- [Troubleshooting Guide](documents/TROUBLESHOOTING.md)

---

## 🛠️ Development Workflow
- Edit `.env` for your settings
- Use `pre-commit` for code quality: `uv add pre-commit && pre-commit install`
- Run tests and linting with `pre-commit run --all-files`
- Rebuild Docker if needed: `docker compose up -d --build`
- Check logs: `docker compose logs -f`

---

## 🔐 Environment Variables
- All config is managed via `.env` (see `env.example`)
- Never commit secrets! Use Google Secret Manager in production

---

## 🤝 Contributing
- Fork, branch, and PR as usual
- See [CONTRIBUTING.md](documents/CONTRIBUTING.md) (if present)

---

## 📄 License
This project is created for hackathon purposes. See LICENSE for details.

---

**Happy Hacking! 🚀**
