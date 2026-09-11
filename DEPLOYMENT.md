# Render Deployment Guide - Smart Attendance System

This document provides a step-by-step guide to deploying the **Smart Attendance System** to [Render](https://render.com) with full production readiness, persistent database storage, and WebRTC HTTPS webcam support.

---

## 🚀 Option 1: One-Click Deploy via Render Blueprint (Recommended)

Render Blueprints use the included [`render.yaml`](file:///c:/Users/Admin/SAM/Smart_Attendance_System/project/render.yaml) file to automatically provision your Docker container web service and persistent disk.

1. **Push your repository to GitHub / GitLab**.
2. Log into your [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** in the top right corner and select **Blueprint**.
4. Connect your GitHub repository containing this project.
5. Render will detect `render.yaml` and configure:
   - Service Name: `smart-attendance-system`
   - Runtime: `Docker`
   - Persistent Disk: `/var/data` (1 GB)
   - Auto-generated `SECRET_KEY`
6. Click **Apply**.
7. Wait for Docker build to complete (usually 3–5 minutes). Your app is now live!

---

## 🛠️ Option 2: Manual Web Service Setup on Render

If you prefer setting up the web service manually through the Render Dashboard interface:

### Step 1: Create New Web Service
1. Go to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your repository.

### Step 2: Configure Service Settings
- **Name**: `smart-attendance-system`
- **Region**: Choose the closest location to your users.
- **Branch**: `main` (or `master`)
- **Root Directory**: `project` (if your project files are inside `project/`, otherwise leave blank)
- **Runtime**: **Docker** (Select Docker so cmake, dlib, and OpenCV system dependencies build automatically)
- **Dockerfile Path**: `./Dockerfile`
- **Instance Type**: `Free` (or `Starter` for higher speed)

### Step 3: Set Environment Variables
Under the **Environment** section, add the following environment variables:

| Key | Recommended Value / Description |
| :--- | :--- |
| `SECRET_KEY` | Click **Generate** or enter a strong secret key string |
| `ADMIN_USERNAME` | Your preferred admin username (default: `admin`) |
| `ADMIN_PASSWORD` | Your preferred admin password (default: `admin123`) |
| `DATA_DIR` | `/var/data` (if attaching a persistent disk) or leave default |
| `FLASK_DEBUG` | `False` |

### Step 4: Add Persistent Disk (Optional but Recommended)
To preserve the SQLite database (`attendance.db`) and uploaded student photos across app redeploys:
1. Under your service settings, navigate to **Disks**.
2. Click **Add Disk**.
3. Set **Name**: `attendance-data`
4. Set **Mount Path**: `/var/data`
5. Set **Size**: `1 GB`
6. Ensure environment variable `DATA_DIR` is set to `/var/data`.

---

## 📷 Webcam / Camera Permission Note for WebRTC

Modern web browsers (Chrome, Edge, Safari, Firefox) **only allow camera access over HTTPS or localhost**.

- When deployed on Render, your app receives a secure `https://smart-attendance-system.onrender.com` URL automatically.
- Users accessing the app over HTTPS can click **Start Camera** in the browser, grant camera access, and mark attendance seamlessly.

---

## 🔍 Health Check & Troubleshooting

### Health Check Endpoint
The app includes a built-in health check route at `/health`:
```
GET /health
Response: {"status": "healthy", "timestamp": "2026-09-11T..."}
```

### Common Issues & Solutions
1. **Camera Not Accessing**: Ensure you are using `https://` (Render provides SSL automatically).
2. **Database Resetting on Restart**: Attach a Render Persistent Disk mounted to `/var/data` and set `DATA_DIR=/var/data`.
3. **Build Timeout**: Ensure **Runtime** is set to `Docker` in Render service settings.
