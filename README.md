# Smart Attendance System

A comprehensive web-based attendance system using face recognition technology built with Flask, OpenCV, SQLite, and WebRTC.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

## Features

✅ **Real-time Face Detection & Recognition**
- Uses OpenCV and face_recognition library
- WebRTC browser webcam integration for live face detection
- High accuracy face matching with tolerance settings

✅ **Student Management**
- Register new students with photos
- Store face encodings in SQLite database
- Unique student ID system

✅ **Attendance Tracking**
- Automatic attendance marking upon face recognition
- Prevents duplicate entries (once per day per student)
- Timestamp recording with date and time

✅ **Admin Dashboard & Security**
- Comprehensive statistics overview
- Hashed admin password authentication (`werkzeug.security`)
- Environment variable configuration (`SECRET_KEY`, `ADMIN_PASSWORD`)

✅ **Records Management & Export**
- View attendance records with date & student filtering
- Export attendance data to CSV format

✅ **Render & Docker Ready**
- Pre-built `Dockerfile` with required C++ and OpenCV build libraries
- `render.yaml` for one-click Render Blueprint deployment
- Health check API (`GET /health`)

---

## Tech Stack

- **Backend**: Flask (Python)
- **WSGI Server**: Gunicorn
- **Face Recognition**: OpenCV (`opencv-python-headless`), `face_recognition` (dlib)
- **Database**: SQLite (`attendance.db`)
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Camera Access**: WebRTC (`navigator.mediaDevices.getUserMedia`)
- **Containerization**: Docker & Render Blueprint

---

## ☁️ Deployment on Render

For complete step-by-step Render deployment instructions, see [`DEPLOYMENT.md`](file:///c:/Users/Admin/SAM/Smart_Attendance_System/project/DEPLOYMENT.md).

### Quick Render Setup:
1. Push this repository to GitHub/GitLab.
2. In [Render Dashboard](https://dashboard.render.com/), click **New +** -> **Blueprint**.
3. Select this repository. Render automatically uses `render.yaml` and `Dockerfile`.
4. Render handles HTTPS (required for webcam permissions), Gunicorn server, and persistent disk mounting.

---

## 💻 Local Installation & Setup

### Prerequisites
- **Python 3.10+**
- **Webcam/Camera**

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
python app.py
```

The application will automatically initialize the SQLite database and be available at `http://localhost:5000`.

---

## Usage

### 1. Admin Login
- Default credentials: `admin` / `admin123` (configurable via `ADMIN_USERNAME` and `ADMIN_PASSWORD` env vars)
- Access the system at `http://localhost:5000`

### 2. Register Students
- Navigate to "Register Student"
- Enter student name and unique ID
- Upload a clear photo showing the student's face
- System will extract and store face encodings

### 3. Mark Attendance
- Go to "Mark Attendance"
- Click "Start Camera" to activate webcam
- Position face in camera view
- Click "Capture & Recognize" to mark attendance

### 4. View & Export Records
- Access "View Records" to see attendance data
- Filter by date or student name/ID
- Export filtered data to CSV format

---

## API Endpoints

- `GET /` - Login page
- `POST /login` - Admin authentication
- `GET /dashboard` - Admin dashboard
- `GET /register` - Student registration form
- `POST /register` - Process student registration
- `GET /recognize` - Face recognition interface
- `POST /process_frame` - Process camera frame for recognition
- `GET /records` - View attendance records
- `GET /export_csv` - Export records to CSV
- `GET /health` - Service health check endpoint
- `GET /logout` - Admin logout

---

## Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | `your-secret-key-change-this` | Flask session secret key |
| `ADMIN_USERNAME` | `admin` | Default admin username |
| `ADMIN_PASSWORD` | `admin123` | Default admin password |
| `DATA_DIR` | `.` (project root) | Directory path for `attendance.db` and static uploads (set to `/var/data` on Render persistent disk) |
| `PORT` | `5000` | HTTP Port for server |

---

## License

This project is open source and available under the [MIT License](LICENSE).