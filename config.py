import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-attendance-secret-key-2026')
    DB_PATH = os.environ.get('DB_PATH', 'attendance.db')
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    PORT = int(os.environ.get('PORT', 5000))
