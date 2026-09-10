# 🚀 Dhvani Rakshak - Render Deployment Guide

This guide walks you through deploying the **Dhvani Rakshak FastAPI Backend** to [Render](https://render.com) for production or live testing.

---

## 🛠️ Pre-Deployment Checklist

The workspace includes all required deployment configuration files:
- ✅ [`render.yaml`](file:///c:/Users/golag/New%20folder/Dhvani%20Rakshak/render.yaml) — Render Blueprint configuration.
- ✅ [`Procfile`](file:///c:/Users/golag/New%20folder/Dhvani%20Rakshak/Procfile) — Web process runner (`uvicorn backend.main:app`).
- ✅ [`requirements.txt`](file:///c:/Users/golag/New%20folder/Dhvani%20Rakshak/requirements.txt) — Production dependencies (`fastapi`, `uvicorn`, `websockets`, `numpy`, `scipy`, etc.).
- ✅ [`backend/Dockerfile`](file:///c:/Users/golag/New%20folder/Dhvani%20Rakshak/backend/Dockerfile) — Containerized deployment option.

---

## 🔹 Option 1: Automatic Deployment using Render Blueprint (Recommended)

1. Push your repository code to **GitHub** or **GitLab**.
2. Sign in to your [Render Dashboard](https://dashboard.render.com).
3. Click **New +** and select **Blueprint**.
4. Connect your GitHub repository (`Dhvani-Rakshak`).
5. Render will automatically detect [`render.yaml`](file:///c:/Users/golag/New%20folder/Dhvani%20Rakshak/render.yaml) and configure:
   - **Service Name**: `dhvani-rakshak-backend`
   - **Environment**: Python 3.11
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/api/v1/health`
6. Click **Apply**. Render will build and deploy the web service automatically!

---

## 🔹 Option 2: Manual Web Service Deployment on Render

If you prefer to configure manually via the Render UI:

1. Go to [Render Dashboard](https://dashboard.render.com) -> **New +** -> **Web Service**.
2. Connect your Git repository.
3. Configure the following fields:
   - **Name**: `dhvani-rakshak-backend`
   - **Region**: Singapore (or nearest to users)
   - **Branch**: `main`
   - **Root Directory**: (Leave blank)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or Starter for higher memory/traffic)
4. Add **Environment Variables** (under Advanced):
   - `PYTHON_VERSION`: `3.11.8`
   - `ENVIRONMENT`: `production`
5. Click **Create Web Service**.

---

## 🔹 Option 3: Docker Deployment on Render

Render also supports native Docker container deployment:

1. Click **New +** -> **Web Service**.
2. Select **Existing Image** or **Build from Dockerfile**.
3. Point Dockerfile path to: `backend/Dockerfile`.
4. Render will build the container image and expose port `$PORT`.

---

## 🌐 Post-Deployment URLs & Endpoints

Once deployed, Render will assign your service a public URL, for example: `https://dhvani-rakshak-backend.onrender.com`

* **Health Check**: `GET https://dhvani-rakshak-backend.onrender.com/api/v1/health`
* **Swagger API Docs**: `https://dhvani-rakshak-backend.onrender.com/docs`
* **WebSockets Live Audio Stream**: `wss://dhvani-rakshak-backend.onrender.com/ws/live-stream`
* **Analyze Endpoint**: `POST https://dhvani-rakshak-backend.onrender.com/api/v1/analyze`
* **Telecom Intercept Endpoint**: `POST https://dhvani-rakshak-backend.onrender.com/api/v1/telecom/simulate-call`

---

## 🔗 Connecting Frontend to Render Backend

Update your frontend API configuration (e.g. in `frontend/src/App.jsx` or `.env`):

```javascript
const API_BASE_URL = "https://dhvani-rakshak-backend.onrender.com";
const WS_BASE_URL = "wss://dhvani-rakshak-backend.onrender.com/ws/live-stream";
```
