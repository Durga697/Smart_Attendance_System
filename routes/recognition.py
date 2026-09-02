from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from services.attendance_service import get_known_student_faces, mark_attendance
from services.face_service import process_frame_data

recognition_bp = Blueprint('recognition', __name__)

@recognition_bp.route('/recognize')
def recognize():
    if 'admin_logged_in' not in session:
        return redirect(url_for('auth.login'))
    return render_template('recognize.html')

@recognition_bp.route('/process_frame', methods=['POST'])
def process_frame():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        image_data = request.json['image']
        known_faces = get_known_student_faces()
        detected_faces = process_frame_data(image_data, known_faces)
        
        results = []
        for face in detected_faces:
            name = face['name']
            student_id = face['student_id']
            
            if student_id:
                mark_result = mark_attendance(student_id, name)
                results.append({
                    'name': name,
                    'student_id': student_id,
                    'attendance_marked': mark_result['success'],
                    'message': mark_result['message']
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
