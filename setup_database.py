#!/usr/bin/env python3
"""
Database setup script for Smart Attendance System
Run this script to create the SQLite database and tables
"""

import sqlite3

DATABASE_NAME = 'attendance.db'

def create_database():
    """Create database and tables"""
    connection = None
    try:
        # Connect to SQLite database file
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()
        
        print(f"Connected to SQLite database: {DATABASE_NAME}")
        
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
        print("Students table created successfully")
        
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
        print("Attendance table created successfully")
        
        # Create admin table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
        print("Admin table created successfully")
        
        # Insert default admin
        cursor.execute("SELECT COUNT(*) FROM admin WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO admin (username, password) VALUES ('admin', 'admin123')")
            print("Default admin user created (username: admin, password: admin123)")
        
        connection.commit()
        print("\nDatabase setup completed successfully!")
        print("You can now run the Flask application with: python app.py")
        
    except sqlite3.Error as e:
        print(f"Error: {e}")
    
    finally:
        if connection:
            connection.close()
            print("SQLite connection closed")

if __name__ == "__main__":
    print("Setting up Smart Attendance System Database...")
    print("=" * 50)
    create_database()