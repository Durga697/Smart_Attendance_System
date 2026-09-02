import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, flash
from services.attendance_service import get_filtered_attendance_records

records_bp = Blueprint('records', __name__)

@records_bp.route('/records')
def records():
    if 'admin_logged_in' not in session:
        return redirect(url_for('auth.login'))
        
    filter_date = request.args.get('date', '')
    filter_student = request.args.get('student', '')
    
    attendance_records = get_filtered_attendance_records(filter_date, filter_student)
    
    return render_template(
        'records.html',
        records=attendance_records,
        filter_date=filter_date,
        filter_student=filter_student
    )

@records_bp.route('/export_csv')
def export_csv():
    if 'admin_logged_in' not in session:
        return redirect(url_for('auth.login'))
        
    filter_date = request.args.get('date', '')
    filter_student = request.args.get('student', '')
    
    records = get_filtered_attendance_records(filter_date, filter_student)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student ID', 'Name', 'Date', 'Time'])
    
    for record in records:
        writer.writerow(record)
        
    output.seek(0)
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
