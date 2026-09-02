import os
from flask import Flask
from config import Config
from database import init_database

# Import Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.student import student_bp
from routes.recognition import recognition_bp
from routes.records import records_bp

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database tables
    init_database()
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(recognition_bp)
    app.register_blueprint(records_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    port = Config.PORT
    app.run(debug=True, host='0.0.0.0', port=port)