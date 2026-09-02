import face_recognition
import cv2
import numpy as np
import base64
from config import Config

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def encode_face_from_image(image_path):
    """Extract face encoding from image file"""
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

def process_frame_data(image_data_base64, known_faces):
    """
    Decode base64 camera frame image and perform face recognition.
    known_faces is a list of dicts: [{'name': ..., 'student_id': ..., 'encoding': np.array}]
    Returns list of recognized face results.
    """
    if ',' in image_data_base64:
        image_data_base64 = image_data_base64.split(',')[1]
        
    image_bytes = base64.b64decode(image_data_base64)
    nparr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    
    known_encodings = [item['encoding'] for item in known_faces]
    known_names = [item['name'] for item in known_faces]
    known_student_ids = [item['student_id'] for item in known_faces]
    
    results = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
        name = "Unknown"
        student_id = None
        
        if True in matches:
            match_index = matches.index(True)
            name = known_names[match_index]
            student_id = known_student_ids[match_index]
            
        results.append({
            'name': name,
            'student_id': student_id
        })
        
    return results
