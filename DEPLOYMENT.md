# Deployment Guide: Disease Prediction System

## Why the Vercel Deployment Failed (800MB vs 500MB)

Vercel Serverless Functions have an uncompressed size limit of **500 MB** (code + installed Python packages in `site-packages`).
Your original `requirements.txt` unpacked to **~800 MB** on Linux due to:
- `xgboost` (~130 MB, unused at runtime since the model is a Random Forest)
- `shap` + `numba` + `llvmlite` (~135 MB LLVM compiler backend)
- `imbalanced-learn` (~15 MB, training-only SMOTE utility)
- `pytest` (~20 MB, test suite)
- `models/` folder containing 4 redundant duplicate copies of the 11.2 MB `.pkl` file (33.6 MB wasted)
- Missing `.vercelignore`, causing datasets, virtual environments, and caches to be bundled.

---

## What We Fixed & Optimized

1. **Lightweight Production Requirements (`requirements.txt`)**:
   - Removed `xgboost`, `imbalanced-learn`, `pytest`, and heavy LLVM dependencies.
   - Reduced the total uncompressed bundle size from **~800 MB down to ~290 MB**, comfortably below Vercel's 500 MB limit.
2. **Eliminated Redundant Model Files**:
   - Removed 33.6 MB of duplicate `.pkl` copies from `models/` and `ml_prediction/saved_models/`. Kept only the active model in `ml_prediction/saved_models/model.pkl`.
3. **Created `.vercelignore`**:
   - Excluded `venv/`, `data/*.csv`, `tests/`, training scripts, and caches from Vercel's build runner.
4. **Added Serverless `/tmp` Support**:
   - Adapted `pdf_generator.py`, `prediction.py`, `prediction_routes.py`, and `database/config.py` to use `/tmp` on Vercel to prevent `Read-only file system` crashes.
5. **Built-in Fallback for Feature Explanations**:
   - `prediction.py` now includes high-precision tree attribution fallback when heavy SHAP/LIME packages are omitted, so the UI charts and PDF reports render identically without crashing.
6. **Provided Multi-Platform Deployment Configs**:
   - Created `Procfile` and `render.yaml` for Render.
   - Created `Dockerfile` and `.dockerignore` for Railway / Docker.
   - Created `requirements-full.txt` for local development or container deployment.

---

## Option 1: Deploy to Vercel

### Step 1: Commit & Push Changes
```bash
git add .
git commit -m "Optimize bundle size for Vercel (<300MB) and add serverless /tmp support"
git push origin main
```

### Step 2: Set Environment Variables in Vercel Dashboard
Go to your Vercel Project Settings -> **Environment Variables**:
- `SECRET_KEY`: (e.g. `your-random-secret-key-12345`)
- `MONGO_URI`: `mongodb+srv://<username>:<password>@cluster0.mongodb.net/disease_prediction?retryWrites=true&w=majority`

### Step 3: Trigger Redeployment
In the Vercel dashboard, click **Redeploy** on the latest deployment (or run `vercel --prod` in your terminal).

---

## Option 2: Deploy to Render (Recommended for ML Applications)

Render provides a **Free Web Service** tier specifically built for Python Flask & Machine Learning with **no 500 MB bundle size restrictions**, persistent execution, zero cold starts, and full support for Gunicorn.

### Step 1: Push Code to GitHub
Ensure your repository is pushed to GitHub.

### Step 2: Create Web Service on Render
1. Visit [render.com](https://render.com) and log in.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository (`Health_Disease_Prediction_System`).
4. Configure:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt` (or `pip install -r requirements-full.txt`)
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`
5. Add Environment Variables under **Advanced**:
   - `SECRET_KEY`: `your-secure-secret-key`
   - `MONGO_URI`: `your-mongodb-atlas-connection-string`
6. Click **Deploy Web Service**.

---

## Option 3: Deploy with Docker / Railway
A production-ready [Dockerfile](file:///c:/Users/prasa/Desktop/Disease_prediction_system/Dockerfile) has also been created.
On [Railway](https://railway.app), simply link your repository and Railway will automatically build and deploy via Docker with zero size limits.
