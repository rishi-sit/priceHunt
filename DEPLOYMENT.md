# PriceHunt API Deployment Guide

## Quick Deploy to Render (Free)

### Step 1: Push to GitHub

```bash
cd /Users/r0k02i7/price-comparator
git init
git add .
git commit -m "Initial commit - PriceHunt API"
git branch -M main
# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/pricehunt-api.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to https://render.com and sign up/login with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `pricehunt-api`
4. Configure:
   - **Name:** `pricehunt-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r api_requirements.txt && playwright install chromium && playwright install-deps`
   - **Start Command:** `python api_server.py`
   - **Instance Type:** `Free`

5. Click **"Create Web Service"**
6. Wait 5-10 minutes for deployment
7. Your API URL will be: `https://pricehunt-api.onrender.com`

### Step 3: Update Android App

Update the `BASE_URL` in:
`app/src/main/java/com/pricehunt/di/NetworkModule.kt`

```kotlin
private const val BASE_URL = "https://pricehunt-api.onrender.com/"
```

Then rebuild and install the app!

---

## Alternative: Deploy to Railway (Even Easier!)

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `pricehunt-api` repo
5. Railway auto-detects Python and deploys
6. Get your URL: `https://pricehunt-api.up.railway.app`

---

## Alternative: Deploy to Fly.io (Fast & Free)

```bash
# Install flyctl
brew install flyctl

# Login
flyctl auth login

# Deploy
cd /Users/r0k02i7/price-comparator
flyctl launch --name pricehunt-api
flyctl deploy
```

Your API will be at: `https://pricehunt-api.fly.dev`

---

## Test Your Deployed API

```bash
curl "https://YOUR_API_URL/api/search?q=milk&pincode=560001"
```

Should return JSON with products from multiple platforms!
