import sqlite3
from config import Config

def get_db_connection():
    """Get database connection"""
    try:
        connection = sqlite3.connect(Config.DB_PATH)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite: {e}")
        return None

def init_database():
    """Initialize database and tables"""
    connection = None
    try:
        connection = sqlite3.connect(Config.DB_PATH)
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
