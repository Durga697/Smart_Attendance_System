import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from services.face_service import allowed_file, encode_face_from_image
from services.attendance_service import save_student_record

student_bp = Blueprint('student', __name__)

@student_bp.route('/register')
def register():
    if 'admin_logged_in' not in session:
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@student_bp.route('/register', methods=['POST'])
def register_post():
    if 'admin_logged_in' not in session:
        return redirect(url_for('auth.login'))
    
    name = request.form['name']
    student_id = request.form['student_id']
    
    if 'image' not in request.files:
        flash('No image uploaded!', 'error')
        return redirect(url_for('student.register'))
    
    file = request.files['image']
    if file.filename == '':
        flash('No image selected!', 'error')
        return redirect(url_for('student.register'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{student_id}_{file.filename}")
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Extract face encoding
        face_encoding = encode_face_from_image(filepath)
        if face_encoding is None:
            flash('No face detected in the image! Please upload a clear face image.', 'error')
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(url_for('student.register'))
        
        # Save to database via attendance service
        result = save_student_record(name, student_id, filepath, face_encoding)
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
            if os.path.exists(filepath):
                os.remove(filepath)
    else:
        flash('Invalid file type! Please upload PNG, JPG, or JPEG files.', 'error')
    
    return redirect(url_for('student.register'))
