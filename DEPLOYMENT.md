# PhishGuard AI - Deployment Guide

This guide covers deploying **PhishGuard AI** to production using different hosting options.

---

## Architecture Overview

- **Frontend**: React 19 + Vite + TypeScript (Single Page Application).
- **Backend**: Python 3.11 + Flask + Gunicorn (serving BERT, Deep CNN, and Isolation Forest models).
- **Extension**: Chromium Manifest V3 browser extension.

---

## Option 1: Managed Cloud Deployment (Recommended)

### A. Deploy Backend to Render / Railway

#### Deploying on Render:
1. Create a free account at [render.com](https://render.com).
2. Click **New +** -> **Web Service** -> Connect your GitHub repository `phishing_detection`.
3. Configure the service:
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3` (or choose `Docker` if using `backend/Dockerfile`)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 wsgi:app`
   - **Instance Type**: 1GB+ RAM recommended (for BERT & CNN inference).
4. In **Environment Variables**, add:
   - `PORT` = `5000` (or leave default assigned by Render)
   - `CORS_ORIGINS` = `*` (or your frontend URL once deployed)
   - `FLASK_ENV` = `production`
5. Click **Create Web Service**. Note your backend URL (e.g., `https://phishguard-api.onrender.com`).

---

### B. Deploy Frontend to Vercel / Netlify

#### Deploying on Vercel:
1. Create a free account at [vercel.com](https://vercel.com).
2. Click **Add New Project** and import your `phishing_detection` repository.
3. Configure Project Settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
4. In **Environment Variables**, add:
   - `VITE_API_BASE_URL` = `https://<YOUR-BACKEND-RENDER-OR-RAILWAY-URL>/api` (e.g. `https://phishguard-api.onrender.com/api`)
5. Click **Deploy**.
   - Your frontend will be live on a secure HTTPS domain (e.g., `https://phishguard-ai.vercel.app`).

---

## Option 2: Single Server / VPS with Docker Compose

If you have a Linux VPS (AWS EC2, DigitalOcean Droplet, Hetzner, etc.):

1. Clone the repository with Git LFS:
   ```bash
   git clone https://github.com/Manishankar-614/phishing_detection.git
   cd phishing_detection
   git lfs pull
   ```

2. Launch both containers:
   ```bash
   docker compose up -d --build
   ```

3. Access your app:
   - **Frontend**: `http://<YOUR_SERVER_IP>`
   - **Backend API**: `http://<YOUR_SERVER_IP>:5000`
   - **Health Check**: `http://<YOUR_SERVER_IP>:5000/health`

---

## Option 3: Containerized Cloud (AWS App Runner / Google Cloud Run)

1. **Backend**:
   - Build and push the Docker image from `backend/Dockerfile` to Amazon ECR or Google Artifact Registry:
     ```bash
     cd backend
     docker build -t phishguard-backend .
     ```
   - Deploy as a container service with 1 CPU and 2GB RAM minimum.

2. **Frontend**:
   - Deploy the build output (`dist/`) directly to AWS S3 + CloudFront, Firebase Hosting, or Cloudflare Pages.

---

## Important Deployment Notes

> [!IMPORTANT]
> **Git LFS in Cloud Build Pipelines**:
> If deploying via GitHub on Render or Railway, ensure Git LFS is enabled or model weights are pulled during build, as the BERT `model.safetensors` file is stored with Git LFS.

> [!TIP]
> **CORS Security**:
> In production, set `CORS_ORIGINS` in your backend environment to your exact frontend domain (e.g., `https://phishguard-ai.vercel.app`) to restrict unauthorized API access.

---

## Environment Variables Reference

### Backend
| Variable | Default | Description |
| :--- | :--- | :--- |
| `PORT` | `5000` | Port for the HTTP / WSGI server |
| `HOST` | `0.0.0.0` | Bind IP address |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated or `*`) |
| `DEBUG` | `false` | Enable Flask debug mode (`true` / `false`) |
| `FLASK_ENV` | `production` | Environment name |

### Frontend
| Variable | Default | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `http://127.0.0.1:5000/api` | Backend API base endpoint |
