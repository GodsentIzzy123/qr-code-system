from flask import Flask, request, jsonify, send_file
from datetime import datetime, timedelta, date
from io import BytesIO
import qrcode
import secrets
import csv
import os
import threading

app = Flask(__name__)

# In-memory store for active tokens: {token: expiry_datetime}
tokens = {}
tokens_lock = threading.Lock()

# CSV file to store attendance
ATTENDANCE_FILE = "attendance.csv"

# Ensure CSV with headers exists
def ensure_csv():
    file_exists = os.path.exists(ATTENDANCE_FILE)
    if not file_exists or os.path.getsize(ATTENDANCE_FILE) == 0:
        with open(ATTENDANCE_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["First Name", "Last Name", "Student ID", "Timestamp", "QR Token"])

def save_attendance(first_name, last_name, student_id, token):
    with open(ATTENDANCE_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            first_name,
            last_name,
            student_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            token
        ])

def has_today_attendance(student_id):
    today_str = date.today().strftime("%Y-%m-%d")
    if not os.path.exists(ATTENDANCE_FILE):
        return False
    with open(ATTENDANCE_FILE, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get("Student ID") == student_id:
                ts = row.get("Timestamp", "")
                if ts.startswith(today_str):
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
def admin_page():
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

    save_attendance(first_name, last_name, student_id, token)
    return jsonify({"status": "success", "message": f"Attendance marked for {first_name} {last_name}"}), 200

@app.route('/attendance.csv', methods=['GET'])
def download_attendance():
    ensure_csv()
    return send_file(ATTENDANCE_FILE, mimetype='text/csv', as_attachment=True, download_name='attendance.csv')

if __name__ == '__main__':
    ensure_csv()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)