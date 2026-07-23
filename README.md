# Smart Attendance System

A web-based attendance system that uses face recognition to automatically mark student attendance. Built with Flask, OpenCV, and SQLite.

## Features

✅ **Real-time Face Detection & Recognition**
- Uses OpenCV and the `face_recognition` library
- Webcam integration for live face capture
- Configurable tolerance for face matching accuracy

✅ **Student Management**
- Register new students with a photo
- Automatically extracts and stores 128-dimensional face encodings
- Unique student ID enforcement

✅ **Attendance Tracking**
- Automatically marks attendance when a registered face is recognized
- Prevents duplicate entries (one record per student per day)
- Records both date and time of attendance

✅ **Admin Dashboard**
- At-a-glance stats: total students, today's attendance, total attendance records
- Simple navigation across all features

✅ **Records Management**
- View attendance records with filters
- Filter by date and/or student name or ID
- Export filtered records to CSV

✅ **Security**
- Admin login and session-based authentication
- Secure filename handling for uploaded images

## Tech Stack

- **Backend**: Flask (Python)
- **Face Recognition**: OpenCV, `face_recognition`
- **Database**: SQLite
- **Image Handling**: Pillow (PIL), NumPy
- **Camera Access**: Browser webcam via `getUserMedia` (WebRTC), processed server-side

## Project Structure

```
.
├── app.py                 # Main Flask application
├── setup_database.py      # Standalone script to initialize the SQLite database
├── attendance.db          # SQLite database file (created on setup/first run)
├── requirements.txt       # Python dependencies
├── static/
│   └── uploads/           # Uploaded student face images
└── templates/             # HTML templates (login, dashboard, register, recognize, records)
```

## Installation

### Prerequisites

1. Python 3.7+
2. A webcam (for the face recognition feature)
3. On Windows, `face_recognition` requires CMake and Visual C++ Build Tools (needed by its `dlib` dependency)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

> Note: `face_recognition` depends on `dlib`, which can take a while to build from source. If installation fails, install CMake first (`pip install cmake`) and ensure a C++ compiler is available.

### Step 2: Initialize the Database

The database is created automatically the first time you run `app.py`, but you can also set it up explicitly:

```bash
python setup_database.py
```

This creates `attendance.db` in the project root with the `students`, `attendance`, and `admin` tables, and seeds a default admin user.

### Step 3: Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`.

## Usage

### 1. Admin Login
- Default credentials: `admin` / `admin123`
- **Change these before any real/shared use** — see Security Notes below.

### 2. Register a Student
- Go to **Register Student**
- Enter the student's name and a unique student ID
- Upload a clear, front-facing photo (PNG/JPG/JPEG)
- The system extracts a face encoding from the photo; if no face is detected, the upload is rejected

### 3. Mark Attendance
- Go to **Recognize/Mark Attendance**
- Start the webcam and capture a frame
- The system matches the detected face against registered students and marks attendance automatically
- Attempting to mark attendance twice in the same day for the same student is blocked

### 4. View & Export Records
- Go to **Records** to browse attendance history
- Filter by date and/or student name/ID
- Use **Export CSV** to download the currently filtered records

## Database Schema

### `students`
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    image_path VARCHAR(255),
    face_encoding TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `attendance`
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(50),
    name VARCHAR(255),
    date DATE,
    time TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    UNIQUE (student_id, date)
);
```

### `admin`
```sql
CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
```

## API Endpoints

| Method | Endpoint         | Description                              | Auth Required |
|--------|------------------|-------------------------------------------|:--------------:|
| GET    | `/`              | Login page                                | No             |
| POST   | `/login`         | Authenticate admin                        | No             |
| GET    | `/logout`        | Log out and clear session                 | Yes            |
| GET    | `/dashboard`     | Admin dashboard with stats                | Yes            |
| GET    | `/register`      | Student registration form                 | Yes            |
| POST   | `/register`      | Process new student registration          | Yes            |
| GET    | `/recognize`     | Face recognition / attendance capture UI  | Yes            |
| POST   | `/process_frame` | Process a captured frame, mark attendance | Yes            |
| GET    | `/records`       | View attendance records (with filters)    | Yes            |
| GET    | `/export_csv`    | Export filtered records as CSV            | Yes            |

## Configuration

### Face Recognition
- **Tolerance**: `0.6` (lower = stricter matching), set in `process_frame()` in `app.py`
- **Accepted image formats**: PNG, JPG, JPEG
- **Face encoding size**: 128-dimensional vector, stored as JSON in the database

### Security Notes
This project is set up for local development/demo use. Before using it in any real or shared environment:
- Change `app.secret_key` in `app.py` to a strong, randomly generated value (ideally loaded from an environment variable)
- Replace the default `admin` / `admin123` credentials
- Hash admin passwords (e.g., with `werkzeug.security.generate_password_hash`) instead of storing them in plain text
- Move secrets/config out of source code and into a `.env` file (a `python-dotenv` dependency is already included for this)

## Troubleshooting

**Camera not working**
- Confirm the browser has camera permission for the site
- Make sure no other application is using the webcam
- Chrome is the most reliably tested browser for this project

**Face not recognized**
- Use good, even lighting when capturing
- Re-register with a clearer, front-facing photo if matches are unreliable
- Adjust the tolerance value in `process_frame()` if matches are consistently too strict/loose

**Database errors**
- Confirm `attendance.db` exists in the project root (run `setup_database.py` if not)
- Delete `attendance.db` and re-run setup if the schema seems out of sync

**Import / installation errors**
- Re-run `pip install -r requirements.txt`
- On Windows, install CMake and Visual C++ Build Tools before installing `face_recognition`/`dlib`

## Production Deployment Notes

If deploying beyond local use:
- Serve with a production WSGI server (e.g., Gunicorn, uWSGI) instead of Flask's built-in dev server
- Enable HTTPS
- Move from SQLite to a more concurrent-friendly database if usage scales up
- Set up regular backups of `attendance.db` and the `static/uploads/` folder
- Apply the security hardening steps listed above

## License

This project is open source and available under the MIT License.
