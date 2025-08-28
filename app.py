from flask import Flask, request, jsonify, send_file
from datetime import datetime, timedelta, date
from io import BytesIO, StringIO
import qrcode
import secrets
import csv
import os
import threading

app = Flask(__name__)

# In-memory store for active tokens: {token: expiry_datetime}
tokens = {}
tokens_lock = threading.Lock()

# In-memory storage for attendance records
attendance_records = []
attendance_lock = threading.Lock()

def save_attendance(first_name, last_name, student_id):
    """Save attendance to in-memory storage"""
    with attendance_lock:
        attendance_records.append({
            'first_name': first_name,
            'last_name': last_name,
            'student_id': student_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"✅ Attendance saved: {first_name} {last_name} ({student_id})")
        return True

def has_today_attendance(student_id):
    """Check if student already has attendance for today"""
    today_str = date.today().strftime("%Y-%m-%d")
    
    with attendance_lock:
        for record in attendance_records:
            if record['student_id'] == student_id:
                if record['timestamp'].startswith(today_str):
                    return True
    return False

def cleanup_expired_tokens():
    now = datetime.now()
    expired = []
    with tokens_lock:
        for t, exp in list(tokens.items()):
            if now > exp:
                expired.append(t)
        for t in expired:
            tokens.pop(t, None)

@app.route('/')
def index():
    return send_file('qr_page.html', mimetype='text/html')

@app.route('/test')
def test():
    return send_file('test.html', mimetype='text/html')

@app.route('/submit/<token>')
def submit_page(token):
    return send_file('submit.html', mimetype='text/html')

@app.route('/admin')
def admin_panel():
    return send_file('admin.html', mimetype='text/html')

@app.route('/generate_qr', methods=['GET'])
def generate_qr():
    cleanup_expired_tokens()

    token = secrets.token_hex(4)  # 8 hex chars
    expiry = datetime.now() + timedelta(minutes=2)
    with tokens_lock:
        tokens[token] = expiry

    # Create a direct submission URL that students can access from their phones
    # This will open a mobile-friendly form
    submission_url = f"{request.host_url.rstrip('/')}/submit/{token}"
    
    # Encode the submission URL into QR, return image as bytes
    img = qrcode.make(submission_url)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype='image/png')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    cleanup_expired_tokens()

    data = request.get_json(silent=True) or {}
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    student_id = (data.get("student_id") or "").strip()
    token = (data.get("token") or "").strip()

    # Validate inputs
    if not all([first_name, last_name, student_id, token]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    # Validate token
    with tokens_lock:
        token_expiry = tokens.get(token)
        if not token_expiry or datetime.now() > token_expiry:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 400
        # One-time use: consume the token immediately
        tokens.pop(token, None)

    # Prevent duplicate attendance for the same day
    if has_today_attendance(student_id):
        return jsonify({"status": "error", "message": "Attendance already recorded today"}), 409

    try:
        save_attendance(first_name, last_name, student_id)
        return jsonify({"status": "success", "message": f"Attendance marked for {first_name} {last_name}"}), 200
    except Exception as e:
        print(f"Error saving attendance: {e}")
        return jsonify({"status": "error", "message": f"Error saving attendance: {str(e)}"}), 500

@app.route('/attendance.csv', methods=['GET'])
def download_attendance():
    """Download attendance data as CSV from in-memory storage"""
    try:
        with attendance_lock:
            if not attendance_records:
                # Return empty CSV with headers if no data
                csv_content = "First Name,Last Name,Student ID,Timestamp\n"
            else:
                # Convert to CSV format
                csv_content = "First Name,Last Name,Student ID,Timestamp\n"
                for record in attendance_records:
                    csv_content += f"{record['first_name']},{record['last_name']},{record['student_id']},{record['timestamp']}\n"
        
        # Create CSV response
        buffer = StringIO(csv_content)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'attendance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to download attendance: {str(e)}"}), 500

@app.route('/clear-attendance', methods=['POST'])
def clear_attendance():
    """Clear all attendance records (useful after each class)"""
    try:
        with attendance_lock:
            global attendance_records
            attendance_records = []
        return jsonify({"status": "success", "message": "Attendance records cleared"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to clear attendance: {str(e)}"}), 500

@app.route('/attendance-count', methods=['GET'])
def attendance_count():
    """Get current attendance count"""
    try:
        with attendance_lock:
            count = len(attendance_records)
        return jsonify({"status": "success", "count": count, "message": f"Total attendance records: {count}"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to get count: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)