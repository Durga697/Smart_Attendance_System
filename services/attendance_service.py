import sqlite3
import json
import numpy as np
from datetime import datetime, date
from database import get_db_connection

def get_dashboard_stats():
    """Get dashboard stats overview"""
    stats = {'total_students': 0, 'today_attendance': 0, 'total_attendance': 0}
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        stats['total_students'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ?", (date.today().isoformat(),))
        stats['today_attendance'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM attendance")
        stats['total_attendance'] = cursor.fetchone()[0]
        
        connection.close()
    return stats

def get_known_student_faces():
    """Retrieve known student faces and encodings from database"""
    known_faces = []
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name, student_id, face_encoding FROM students")
        students = cursor.fetchall()
        
        for student in students:
            name, student_id, encoding_json = student
            if encoding_json:
                encoding = np.array(json.loads(encoding_json))
                known_faces.append({
                    'name': name,
                    'student_id': student_id,
                    'encoding': encoding
                })
        connection.close()
    return known_faces

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
                connection.close()
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
        return {'success': False, 'message': 'Database connection error'}
    except Exception as e:
        return {'success': False, 'message': f'Error marking attendance: {str(e)}'}

def save_student_record(name, student_id, filepath, face_encoding):
    """Save new student to database"""
    connection = get_db_connection()
    if not connection:
        return {'success': False, 'message': 'Database connection error'}
        
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO students (name, student_id, image_path, face_encoding)
            VALUES (?, ?, ?, ?)
        """, (name, student_id, filepath, json.dumps(face_encoding)))
        connection.commit()
        return {'success': True, 'message': 'Student registered successfully!'}
    except sqlite3.IntegrityError:
        return {'success': False, 'message': 'Student ID already exists!'}
    except Exception as e:
        return {'success': False, 'message': f'Error registering student: {str(e)}'}
    finally:
        connection.close()

def get_filtered_attendance_records(filter_date='', filter_student=''):
    """Fetch attendance records according to filter parameters"""
    connection = get_db_connection()
    records = []
    if connection:
        cursor = connection.cursor()
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
    return records
