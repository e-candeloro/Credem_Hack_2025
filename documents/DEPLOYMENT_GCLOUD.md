# 🚀 Deploying to Google Cloud Run

This guide explains how to deploy the AI HR System (FastAPI backend + Streamlit frontend) to Google Cloud Run using Docker images.

---

## Prerequisites
- Google Cloud account and project
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [Docker](https://docs.docker.com/get-docker/)
- Billing enabled on your GCP project
- Enable Cloud Run, Artifact Registry, and Secret Manager APIs

---

## 1. Build and Push Docker Images

### Authenticate Docker with Google Cloud:
```bash
gcloud auth configure-docker
```

### Tag and push backend image:
```bash
docker build -t gcr.io/YOUR_PROJECT_ID/ai-hr-backend:latest .
docker push gcr.io/YOUR_PROJECT_ID/ai-hr-backend:latest
```

### Tag and push frontend image:
```bash
docker build -t gcr.io/YOUR_PROJECT_ID/ai-hr-frontend:latest ./frontend
docker push gcr.io/YOUR_PROJECT_ID/ai-hr-frontend:latest
```

---

## 2. Set Up Secrets (Recommended)

### Create a secret for your backend secret key:
```bash
gcloud secrets create ai-hr-secret-key --data-file=- <<< "your-production-secret-key"
```

### Grant access to Cloud Run service account:
```bash
gcloud secrets add-iam-policy-binding ai-hr-secret-key \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 3. Configure Environment Variables

- Edit `gcp/run.yaml` to set your environment variables and secret references.
- Set `API_BASE_URL` in the frontend to the deployed backend URL.
- Set `ALLOWED_ORIGINS` in the backend to your frontend URL.

---

## 4. Deploy to Cloud Run

### Deploy backend:
```bash
gcloud run deploy ai-hr-backend \
  --image gcr.io/YOUR_PROJECT_ID/ai-hr-backend:latest \
  --platform managed \
  --region YOUR_REGION \
  --allow-unauthenticated \
  --update-secrets SECRET_KEY=ai-hr-secret-key:latest \
  --set-env-vars ENVIRONMENT=production,DEBUG=false,ALLOWED_ORIGINS=https://your-frontend-url
```

### Deploy frontend:
```bash
gcloud run deploy ai-hr-frontend \
  --image gcr.io/YOUR_PROJECT_ID/ai-hr-frontend:latest \
  --platform managed \
  --region YOUR_REGION \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production,DEBUG=false,API_BASE_URL=https://ai-hr-backend-xxxxx-uc.a.run.app
```

---

## 5. Verify Deployment
- Visit the Cloud Run URLs for both services.
- Check `/api/v1/health` on the backend.
- Open the frontend and verify it can reach the backend.

---

## 6. (Optional) Automate with GitHub Actions
- See `.github/workflows/` for CI/CD examples.
- You can automate Docker builds and GCP deployments.

---

## Useful Links
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Secret Manager Docs](https://cloud.google.com/secret-manager/docs)
- [Artifact Registry Docs](https://cloud.google.com/artifact-registry/docs)
