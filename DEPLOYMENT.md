# Render Deployment Guide - Smart Attendance System

This document provides a step-by-step guide to deploying the **Smart Attendance System** to [Render](https://render.com) with full production readiness, persistent database storage, and WebRTC HTTPS webcam support.

---

## 🛠️ Essential Render Settings

Render can deploy this application using **Native Python** or **Docker**.

### Option A: Native Python Web Service (Standard)

When deploying as a standard Python service on Render:

1. **Python Version**: `3.10.13` (Set via `PYTHON_VERSION=3.10.13` environment variable or `runtime.txt`). *Python 3.10 is required for pre-built dlib wheel compatibility.*
2. **Build Command**: `./build.sh`
3. **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 app:app`

> **Why `./build.sh`?**
> Building `dlib` on Linux requires installing `cmake` prior to running `pip install -r requirements.txt`. The included `./build.sh` automatically installs build tools and `cmake` first.

---

### Option B: One-Click Deploy via Render Blueprint

Render Blueprints use the included [`render.yaml`](file:///c:/Users/Admin/SAM/Smart_Attendance_System/project/render.yaml) file to automatically provision your web service and persistent disk.

1. Push your repository to GitHub.
2. Log into your [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** -> **Blueprint**.
4. Connect your GitHub repository (`Durga697/Smart_Attendance_System`).
5. Render detects `render.yaml` and configures:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 app:app`
   - Python Version: `3.10.13`
   - Persistent Disk: `/var/data` (1 GB)
6. Click **Apply**.

---

### Option C: Docker Web Service

If you set **Environment** to **Docker** in Render Dashboard:
- **Dockerfile Path**: `./Dockerfile`
- No build command or start command needed (handled by `Dockerfile`).

---

## 🔑 Environment Variables Reference

Add these in Render under **Environment**:

| Key | Recommended Value | Purpose |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.10.13` | Ensures compatible Python 3.10 binary wheels for dlib |
| `SECRET_KEY` | Generate random secret | Flask session encryption |
| `ADMIN_USERNAME` | `admin` | Admin dashboard login username |
| `ADMIN_PASSWORD` | `admin123` | Admin dashboard login password |
| `DATA_DIR` | `/var/data` | Path for SQLite DB & photo uploads on persistent disk |

---

## 💾 Persistent Disk Configuration

To preserve student records (`attendance.db`) and uploaded images:
1. In Render Web Service settings, click **Disks**.
2. Click **Add Disk**.
3. **Name**: `attendance-data`
4. **Mount Path**: `/var/data`
5. **Size**: `1 GB`
6. Set `DATA_DIR` environment variable to `/var/data`.

---

## 📷 Webcam / Camera Access Note

WebRTC (`navigator.mediaDevices.getUserMedia`) requires **HTTPS**. Render automatically provisions free SSL certificates (`https://your-app.onrender.com`). Users can open the URL in Chrome, Edge, or Safari and grant camera permissions.
