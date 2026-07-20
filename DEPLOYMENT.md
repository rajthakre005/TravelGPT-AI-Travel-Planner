# Deployment Guide: Free Cloud Hosting for TravelGPT

This guide walks you through deploying **TravelGPT** to free cloud platforms without modifying any of the existing user interface (UI) code or styling.

---

## Option 1: Render (Free Tier Web Service)

Render provides a free hosting tier for Python web services that connects directly to a GitHub repository and redeploys automatically on git pushes.

### Steps to Deploy:
1. **Push your code to GitHub**:
   - Create a private or public repository on GitHub (e.g. `TravelGPT`).
   - Push the contents of the `travel-planner/` folder to the repository.
2. **Sign up for Render**:
   - Go to [render.com](https://render.com) and sign up for a free account.
3. **Create a new Web Service**:
   - In the Render Dashboard, click **New +** and select **Web Service**.
   - Connect your GitHub account and choose your `TravelGPT` repository.
4. **Configure the settings**:
   - **Name**: `travelgpt-planner` (or any unique name)
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Select **Free** (CPU, RAM, and bandwidth are free).
5. **Set Environment Variables (Optional)**:
   - If you want a global Gemini API key pre-configured for your deployment so users do not have to enter their own, add an environment variable:
     - Key: `GEMINI_API_KEY`
     - Value: `YOUR_API_KEY_HERE`
   - *Note: If left unset, users can still input their own keys directly in the UI Settings gear modal.*
6. **Deploy**:
   - Click **Create Web Service**. Render will build and deploy the app. Once completed, your custom link (e.g. `https://travelgpt-planner.onrender.com`) will be active.

---

## Option 2: Hugging Face Spaces (100% Free Docker Container Hosting)

Hugging Face Spaces offers a completely free hosting tier for Docker containers that runs indefinitely (without sleep/suspension states common to other free providers).

### Steps to Deploy:
1. **Create an account**:
   - Sign up for a free account at [huggingface.co](https://huggingface.co).
2. **Create a new Space**:
   - Click your profile image in the top-right and select **New Space**.
   - **Space Name**: `travelgpt`
   - **License**: `mit` (or choose any)
   - **SDK**: Select **Docker** (very important).
   - **Template**: Choose **Blank** (default).
   - **Space Hardware**: Choose **CPU basic • 2 vCPU • 16 GB • Free** (runs 24/7 for free).
   - **Visibility**: Public or Private.
   - Click **Create Space**.
3. **Upload/Push your files**:
   - Clone the Space repository locally using Git or upload the files directly through the Hugging Face web interface.
   - Add all of the files from the `travel-planner/` folder (including `Dockerfile` and `requirements.txt`).
4. **Build and Host**:
   - Once the files are uploaded, Hugging Face will read the `Dockerfile`, install the dependencies via pip, and launch Gunicorn.
   - In a few minutes, the status will turn to green **Running**, and the app will load in the space frame.
5. **Add API Keys (Optional)**:
   - Go to the **Settings** tab of your Space, scroll to **Variables and secrets**, and add a new Secret:
     - Name: `GEMINI_API_KEY`
     - Value: `YOUR_API_KEY_HERE`
