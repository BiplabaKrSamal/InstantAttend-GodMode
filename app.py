"""
InstantAttend — God Mode Edition
Real-time Face Recognition Attendance System
Author: BiplabaKrSamal
"""

import cv2
import os
import sqlite3
import joblib
import numpy as np
import pandas as pd
from datetime import date, datetime
from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for
from flask_socketio import SocketIO, emit
from sklearn.neighbors import KNeighborsClassifier
from io import BytesIO
import json

# ──────────────────────────────────────────────────────────────
#  App Setup
# ──────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = 'instantattend-godmode-2025'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ──────────────────────────────────────────────────────────────
#  Constants & Paths
# ──────────────────────────────────────────────────────────────
DB_PATH       = 'attendance.db'
FACES_DIR     = 'static/faces'
MODEL_PATH    = 'static/face_recognition_model.pkl'
HAAR_CASCADE  = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_detector = cv2.CascadeClassifier(HAAR_CASCADE)

os.makedirs(FACES_DIR, exist_ok=True)
os.makedirs('Attendance', exist_ok=True)

# ──────────────────────────────────────────────────────────────
#  Database Setup (SQLite)
# ──────────────────────────────────────────────────────────────
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                roll    TEXT NOT NULL UNIQUE,
                created TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                roll      TEXT NOT NULL,
                name      TEXT NOT NULL,
                date      TEXT NOT NULL,
                time      TEXT NOT NULL,
                status    TEXT DEFAULT 'Present',
                UNIQUE(roll, date)
            )
        """)
        conn.commit()

init_db()

# ──────────────────────────────────────────────────────────────
#  Helper Functions
# ──────────────────────────────────────────────────────────────
def today_str():
    return date.today().strftime("%Y-%m-%d")

def today_display():
    return date.today().strftime("%d %B %Y")

def extract_faces(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return face_detector.detectMultiScale(gray, 1.3, 5)

def identify_face(face_array):
    if not os.path.exists(MODEL_PATH):
        return None
    model = joblib.load(MODEL_PATH)
    return model.predict(face_array)[0]

def train_model():
    faces, labels = [], []
    for user in os.listdir(FACES_DIR):
        for img_name in os.listdir(f'{FACES_DIR}/{user}'):
            img = cv2.imread(f'{FACES_DIR}/{user}/{img_name}')
            if img is None:
                continue
            faces.append(cv2.resize(img, (50, 50)).ravel())
            labels.append(user)
    if faces:
        knn = KNeighborsClassifier(n_neighbors=5)
        knn.fit(np.array(faces), labels)
        joblib.dump(knn, MODEL_PATH)
        return True
    return False

def add_attendance(label):
    parts  = label.rsplit('_', 1)
    name   = parts[0]
    roll   = parts[1] if len(parts) > 1 else '000'
    now    = datetime.now()
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO attendance (roll, name, date, time) VALUES (?,?,?,?)",
                (roll, name, today_str(), now.strftime("%H:%M:%S"))
            )
            conn.commit()
            # Broadcast real-time update
            socketio.emit('attendance_update', {
                'name': name, 'roll': roll,
                'time': now.strftime("%H:%M:%S"), 'date': today_str()
            })
            return True
        except Exception:
            return False

def get_today_attendance():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT name, roll, time, status FROM attendance WHERE date=? ORDER BY time",
            (today_str(),)
        ).fetchall()
    return [{'name': r[0], 'roll': r[1], 'time': r[2], 'status': r[3]} for r in rows]

def get_stats():
    with sqlite3.connect(DB_PATH) as conn:
        total_users  = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_today  = conn.execute("SELECT COUNT(*) FROM attendance WHERE date=?", (today_str(),)).fetchone()[0]
        total_all    = conn.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]
        weekly       = conn.execute("""
            SELECT date, COUNT(*) as cnt FROM attendance
            WHERE date >= date('now','-6 days')
            GROUP BY date ORDER BY date
        """).fetchall()
    return {
        'total_users':  total_users,
        'present_today': total_today,
        'total_records': total_all,
        'weekly': [{'date': r[0], 'count': r[1]} for r in weekly]
    }

# ──────────────────────────────────────────────────────────────
#  Web Routes
# ──────────────────────────────────────────────────────────────
@app.route('/')
def home():
    records = get_today_attendance()
    stats   = get_stats()
    model_ready = os.path.exists(MODEL_PATH)
    return render_template('home.html',
        records=records, stats=stats,
        model_ready=model_ready,
        datetoday2=today_display()
    )

@app.route('/start', methods=['GET'])
def start():
    if not os.path.exists(MODEL_PATH):
        return redirect(url_for('home'))

    cap = cv2.VideoCapture(0)
    marked = set()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        faces = extract_faces(frame)
        for (x, y, w, h) in faces:
            face   = cv2.resize(frame[y:y+h, x:x+w], (50, 50))
            label  = identify_face(face.reshape(1, -1))
            if label:
                add_attendance(label)
                marked.add(label)
                display_name = label.rsplit('_', 1)[0]
                color = (0, 200, 0) if label in marked else (255, 0, 20)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, f'✓ {display_name}', (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f'Marked: {len(marked)} | ESC to exit',
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow('InstantAttend — Taking Attendance', frame)
        if cv2.waitKey(1) == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
    return redirect(url_for('home'))

@app.route('/add', methods=['POST'])
def add():
    name   = request.form.get('newusername', '').strip().replace(' ', '_')
    roll   = request.form.get('newuserid', '').strip()
    if not name or not roll:
        return redirect(url_for('home'))

    folder = f'{FACES_DIR}/{name}_{roll}'
    os.makedirs(folder, exist_ok=True)

    # Register in DB
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (name, roll, created) VALUES (?,?,?)",
            (name, roll, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()

    cap = cv2.VideoCapture(0)
    count, frame_num = 0, 0
    while count < 50:
        ret, frame = cap.read()
        if not ret:
            break
        faces = extract_faces(frame)
        for (x, y, w, h) in faces:
            if frame_num % 10 == 0 and count < 50:
                cv2.imwrite(f'{folder}/{name}_{count}.jpg', frame[y:y+h, x:x+w])
                count += 1
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 200, 0), 2)
        prog = int((count / 50) * 100)
        cv2.putText(frame, f'Capturing: {count}/50  [{prog}%]',
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 0), 2)
        cv2.imshow(f'Registering: {name}', frame)
        frame_num += 1
        if cv2.waitKey(1) == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
    train_model()
    return redirect(url_for('home'))

@app.route('/retrain', methods=['POST'])
def retrain():
    success = train_model()
    return jsonify({'success': success, 'message': 'Model retrained!' if success else 'No faces found.'})

@app.route('/delete_user/<roll>', methods=['POST'])
def delete_user(roll):
    with sqlite3.connect(DB_PATH) as conn:
        user = conn.execute("SELECT name FROM users WHERE roll=?", (roll,)).fetchone()
        if user:
            import shutil
            folder = f"{FACES_DIR}/{user[0]}_{roll}"
            if os.path.exists(folder):
                shutil.rmtree(folder)
            conn.execute("DELETE FROM users WHERE roll=?", (roll,))
            conn.execute("DELETE FROM attendance WHERE roll=?", (roll,))
            conn.commit()
    train_model()
    return redirect(url_for('admin'))

@app.route('/admin')
def admin():
    with sqlite3.connect(DB_PATH) as conn:
        users = conn.execute("SELECT name, roll, created FROM users ORDER BY created DESC").fetchall()
        history = conn.execute("""
            SELECT a.name, a.roll, a.date, a.time, a.status
            FROM attendance a ORDER BY a.date DESC, a.time DESC LIMIT 100
        """).fetchall()
    return render_template('admin.html',
        users=[{'name': u[0], 'roll': u[1], 'created': u[2]} for u in users],
        history=[{'name': h[0], 'roll': h[1], 'date': h[2], 'time': h[3], 'status': h[4]} for h in history],
        stats=get_stats(), datetoday2=today_display()
    )

# ──────────────────────────────────────────────────────────────
#  REST API Endpoints
# ──────────────────────────────────────────────────────────────
@app.route('/api/attendance/today', methods=['GET'])
def api_today():
    return jsonify({'date': today_str(), 'records': get_today_attendance()})

@app.route('/api/attendance/<date_str>', methods=['GET'])
def api_by_date(date_str):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT name, roll, time, status FROM attendance WHERE date=? ORDER BY time",
            (date_str,)
        ).fetchall()
    return jsonify({'date': date_str, 'records': [
        {'name': r[0], 'roll': r[1], 'time': r[2], 'status': r[3]} for r in rows
    ]})

@app.route('/api/stats', methods=['GET'])
def api_stats():
    return jsonify(get_stats())

@app.route('/api/users', methods=['GET'])
def api_users():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT name, roll, created FROM users").fetchall()
    return jsonify([{'name': r[0], 'roll': r[1], 'registered': r[2]} for r in rows])

@app.route('/export/excel')
def export_excel():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT name, roll, date, time, status FROM attendance ORDER BY date DESC, time DESC", conn)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    buf.seek(0)
    return send_file(buf, download_name='InstantAttend_Export.xlsx',
                     as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/export/csv')
def export_csv():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql("SELECT name, roll, date, time, status FROM attendance ORDER BY date DESC", conn)
    buf = BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return send_file(buf, download_name=f'Attendance_{today_str()}.csv',
                     as_attachment=True, mimetype='text/csv')

# ──────────────────────────────────────────────────────────────
#  WebSocket Events
# ──────────────────────────────────────────────────────────────
@socketio.on('connect')
def handle_connect():
    emit('connected', {'status': 'InstantAttend live stream active'})

# ──────────────────────────────────────────────────────────────
#  Run
# ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
