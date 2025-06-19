# 🛠️ Troubleshooting Guide

This guide covers common issues and solutions for the AI HR System project.

---

## Docker Issues

**Q: Docker containers won't start?**
- Make sure Docker is running: `docker info`
- Check for port conflicts: `lsof -i :8000` and `lsof -i :8501`
- Check logs: `docker compose logs`
- Remove all containers/volumes: `docker compose down -v`

**Q: Changes in code are not reflected?**
- If using Docker, rebuild: `docker compose up -d --build`
- If using uv locally, restart the process

---

## .env and Environment Variables

**Q: My app can't find environment variables?**
- Make sure you have a `.env` file in the project root
- Check `.env` is not named `.env.example`
- For Docker, ensure `env_file: .env` is set in `docker-compose.yaml`
- For GCP, set env vars in Cloud Run or use Secret Manager

---

## CORS Issues

**Q: Frontend can't reach backend (CORS error)?**
- Set `ALLOWED_ORIGINS` in `.env` to include your frontend URL
- For production, use the deployed frontend URL
- Restart backend after changing CORS settings

---

## Google Cloud Run

**Q: Backend/Frontend not reachable after deploy?**
- Check Cloud Run logs in the GCP console
- Make sure services are deployed in the same region
- Ensure `--allow-unauthenticated` is set if you want public access
- Check that environment variables and secrets are set correctly

**Q: Health checks fail?**
- Check `/api/v1/health` endpoint directly
- Make sure the container port matches the service port

---

## CI/CD Issues

**Q: GitHub Actions fails to deploy?**
- Check that GCP credentials are set up as GitHub secrets
- Make sure Docker images are built and pushed before deploy
- Review workflow logs for error details

---

## General Tips
- Always check logs first (Docker, Cloud Run, or Streamlit)
- Use `docker compose ps` to see running containers
- Use `pre-commit run --all-files` to check code quality before committing
- If stuck, try rebuilding everything and restarting Docker
