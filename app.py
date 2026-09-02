from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import cv2
import face_recognition
import numpy as np
import sqlite3
import os
import base64
from datetime import datetime, date
import csv
import io
from werkzeug.utils import secure_filename
from PIL import Image
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'smart-attendance-secret-key-2026')


# Database configuration
DB_PATH = 'attendance.db'

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    """Get database connection"""
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite: {e}")
        return None

def init_database():
    """Initialize database and tables"""
    connection = None
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        
        # Create students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                student_id VARCHAR(50) UNIQUE NOT NULL,
                image_path VARCHAR(255),
                face_encoding TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id VARCHAR(50),
                name VARCHAR(255),
                date DATE,
                time TIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE (student_id, date)
            )
        """)
        
        # Create admin table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        
        # Insert default admin if not exists
        cursor.execute("SELECT COUNT(*) FROM admin WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO admin (username, password) VALUES ('admin', 'admin123')")
        
        connection.commit()
        print("Database initialized successfully")
        
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if connection:
            connection.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_face_from_image(image_path):
    """Extract face encoding from image"""
    try:
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) > 0:
            return face_encodings[0].tolist()
        else:
            return None
    except Exception as e:
        print(f"Error encoding face: {e}")
        return None

@app.route('/')
def login():
    if 'admin_logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = ? AND password = ?", (username, password))
        admin = cursor.fetchone()
        
        if admin:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    stats = {'total_students': 0, 'today_attendance': 0, 'total_attendance': 0}
    
    if connection:
        cursor = connection.cursor()
        
        # Get total students
        cursor.execute("SELECT COUNT(*) FROM students")
        stats['total_students'] = cursor.fetchone()[0]
        
        # Get today's attendance
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (date.today().isoformat(),))
        stats['today_attendance'] = cursor.fetchone()[0]
        
        # Get total attendance records
        cursor.execute("SELECT COUNT(*) FROM attendance")
        stats['total_attendance'] = cursor.fetchone()[0]
        
        connection.close()
    
    return render_template('dashboard.html', stats=stats)

@app.route('/register')
def register():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    name = request.form['name']
    student_id = request.form['student_id']
    
    # Handle image upload
    if 'image' not in request.files:
        flash('No image uploaded!', 'error')
        return redirect(url_for('register'))
    
    file = request.files['image']
    if file.filename == '':
        flash('No image selected!', 'error')
        return redirect(url_for('register'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{student_id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract face encoding
        face_encoding = encode_face_from_image(filepath)
        if face_encoding is None:
            flash('No face detected in the image! Please upload a clear face image.', 'error')
            os.remove(filepath)  # Remove the uploaded file
            return redirect(url_for('register'))
        
        # Save to database
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                cursor.execute("""
                    INSERT INTO students (name, student_id, image_path, face_encoding)
                    VALUES (?, ?, ?, ?)
                """, (name, student_id, filepath, json.dumps(face_encoding)))
                connection.commit()
                flash('Student registered successfully!', 'success')
            except sqlite3.IntegrityError:
                flash('Student ID already exists!', 'error')
                os.remove(filepath)  # Remove the uploaded file
            except Exception as e:
                flash(f'Error registering student: {str(e)}', 'error')
                os.remove(filepath)  # Remove the uploaded file
            finally:
                connection.close()
    else:
        flash('Invalid file type! Please upload PNG, JPG, or JPEG files.', 'error')
    
    return redirect(url_for('register'))

@app.route('/recognize')
def recognize():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('recognize.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Get image data from request
        image_data = request.json['image']
        
        # Decode base64 image
        image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64,
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Get known faces from database
        connection = get_db_connection()
        known_faces = []
        known_names = []
        known_student_ids = []
        
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT name, student_id, face_encoding FROM students")
            students = cursor.fetchall()
            
            for student in students:
                name, student_id, encoding_json = student
                if encoding_json:
                    encoding = np.array(json.loads(encoding_json))
                    known_faces.append(encoding)
                    known_names.append(name)
                    known_student_ids.append(student_id)
            
            connection.close()
        
        # Process each face in the frame
        results = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.6)
            name = "Unknown"
            student_id = None
            
            if True in matches:
                match_index = matches.index(True)
                name = known_names[match_index]
                student_id = known_student_ids[match_index]
                
                # Mark attendance
                if student_id:
                    mark_attendance_result = mark_attendance(student_id, name)
                    results.append({
                        'name': name,
                        'student_id': student_id,
                        'attendance_marked': mark_attendance_result['success'],
                        'message': mark_attendance_result['message']
                    })
            else:
                results.append({
                    'name': name,
                    'student_id': None,
                    'attendance_marked': False,
                    'message': 'Face not recognized'
                })
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def mark_attendance(student_id, name):
    """Mark attendance for a student"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # Check if attendance already marked today
            cursor.execute("""
                SELECT * FROM attendance 
                WHERE student_id = ? AND date = ?
            """, (student_id, date.today().isoformat()))
            
            existing_record = cursor.fetchone()
            
            if existing_record:
                return {'success': False, 'message': 'Attendance already marked today'}
            
            # Mark new attendance
            current_time = datetime.now().time()
            current_time_str = current_time.strftime('%H:%M:%S')
            cursor.execute("""
                INSERT INTO attendance (student_id, name, date, time)
                VALUES (?, ?, ?, ?)
            """, (student_id, name, date.today().isoformat(), current_time_str))
            
            connection.commit()
            connection.close()
            
            return {'success': True, 'message': 'Attendance marked successfully'}
    
    except Exception as e:
        return {'success': False, 'message': f'Error marking attendance: {str(e)}'}

@app.route('/records')
def records():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    # Get filter parameters
    filter_date = request.args.get('date', '')
    filter_student = request.args.get('student', '')
    
    connection = get_db_connection()
    attendance_records = []
    
    if connection:
        cursor = connection.cursor()
        
        # Build query based on filters
        query = "SELECT student_id, name, date, time FROM attendance WHERE 1=1"
        params = []
        
        if filter_date:
            query += " AND date = ?"
            params.append(filter_date)
        
        if filter_student:
            query += " AND (student_id LIKE ? OR name LIKE ?)"
            params.extend([f"%{filter_student}%", f"%{filter_student}%"])
        
        query += " ORDER BY date DESC, time DESC"
        
        cursor.execute(query, params)
        attendance_records = cursor.fetchall()
        connection.close()
    
    return render_template('records.html', records=attendance_records, 
                         filter_date=filter_date, filter_student=filter_student)

@app.route('/export_csv')
def export_csv():
    if 'admin_logged_in' not in session:
        return redirect(url_for('login'))
    
    # Get filter parameters
    filter_date = request.args.get('date', '')
    filter_student = request.args.get('student', '')
    
    connection = get_db_connection()
    if not connection:
        flash('Database connection error!', 'error')
        return redirect(url_for('records'))
    
    cursor = connection.cursor()
    
    # Build query based on filters
    query = "SELECT student_id, name, date, time FROM attendance WHERE 1=1"
    params = []
    
    if filter_date:
        query += " AND date = ?"
        params.append(filter_date)
    
    if filter_student:
        query += " AND (student_id LIKE ? OR name LIKE ?)"
        params.extend([f"%{filter_student}%", f"%{filter_student}%"])
    
    query += " ORDER BY date DESC, time DESC"
    
    cursor.execute(query, params)
    records = cursor.fetchall()
    connection.close()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Student ID', 'Name', 'Date', 'Time'])
    
    # Write data
    for record in records:
        writer.writerow(record)
    
    # Create response
    output.seek(0)
    
    # Create a BytesIO object for the file download
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    
    filename = f"attendance_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        mem,
        as_attachment=True,
        download_name=filename,
        mimetype='text/csv'
    )

if __name__ == '__main__':
    init_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)