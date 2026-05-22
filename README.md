# 🎯 InstantAttend — God Mode Edition

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=for-the-badge&logo=opencv&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![SocketIO](https://img.shields.io/badge/WebSocket-Live-ff6b35?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![CI](https://img.shields.io/github/actions/workflow/status/BiplabaKrSamal/InstantAttend/ci.yml?style=for-the-badge&label=CI%2FCD)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Real-time face recognition attendance — zero roll calls, zero delays.**

[🌐 Live Demo](https://bipLabakrsamal.github.io/InstantAttend) · [📖 Docs](#-getting-started) · [🐛 Issues](https://github.com/BiplabaKrSamal/InstantAttend/issues) · [⭐ Star](https://github.com/BiplabaKrSamal/InstantAttend)

![Dashboard Preview](screenshot.png)

</div>

---

## ✨ What's New in God Mode (v2.0)

| Feature | v1.0 (Original) | v2.0 God Mode |
|---------|----------------|---------------|
| Storage | CSV files | **SQLite database** |
| Live updates | Manual refresh | **WebSocket (real-time)** |
| API | None | **Full REST API** |
| Export | CSV only | **CSV + Excel (.xlsx)** |
| Admin panel | None | **Full user management** |
| Tests | None | **pytest suite + CI/CD** |
| Deployment | Manual | **Docker + GitHub Actions** |
| Landing page | None | **GitHub Pages site** |
| Duplicate check | Roll number | **Roll + Date unique constraint** |
| Dashboard | Basic table | **Stats cards + weekly chart** |

---

## 🚀 Getting Started

### Option A — Direct (Python)

```bash
# 1. Clone
git clone https://github.com/BiplabaKrSamal/InstantAttend.git
cd InstantAttend

# 2. Install
pip install -r requirements.txt

# 3. Run
python app.py
# → Open http://127.0.0.1:5000
```

### Option B — Docker (Recommended)

```bash
# One command — fully isolated, no Python setup needed
docker compose up --build

# → Open http://127.0.0.1:5000
```

### Option C — Docker CLI

```bash
docker build -t instantattend .
docker run -p 5000:5000 -v $(pwd)/static/faces:/app/static/faces instantattend
```

---

## 📋 How It Works

### 1. Register a User
- Enter name + roll number → click **Capture & Register**
- Webcam captures **50 face samples** automatically (takes ~10 seconds)
- KNN model **retrains instantly** — user is immediately recognisable

### 2. Take Attendance
- Click **Launch Webcam** (or navigate to `/start`)
- System detects faces → matches against KNN model in real-time
- Attendance marked in **SQLite** with name, roll, timestamp
- Dashboard **updates live** via WebSocket — no page refresh

### 3. Export & Report
- **CSV**: `/export/csv` — instant download of all records
- **Excel**: `/export/excel` — formatted `.xlsx` with all history
- **REST API**: query attendance programmatically (see below)

---

## 🗂️ Project Structure

```
InstantAttend/
│
├── app.py                         # Flask app — routes, DB, face logic, SocketIO
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Production Docker image
├── docker-compose.yml             # One-command deployment
│
├── templates/
│   ├── home.html                  # Dashboard (live stats, WebSocket, chart)
│   └── admin.html                 # Admin panel (user management, history)
│
├── static/
│   └── faces/                     # Registered face images (auto-created)
│       └── Name_Roll/             # 50 images per user
│
├── tests/
│   └── test_app.py                # pytest suite (DB, helpers, API routes)
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions: test → pages → docker
│
├── docs/
│   └── index.html                 # GitHub Pages landing page
│
├── attendance.db                  # SQLite database (auto-created)
└── Attendance/                    # Legacy CSV exports
```

---

## 🌐 REST API Reference

All endpoints return JSON.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/attendance/today` | Today's attendance records |
| `GET` | `/api/attendance/YYYY-MM-DD` | Records for a specific date |
| `GET` | `/api/users` | All registered users |
| `GET` | `/api/stats` | Summary stats + 7-day chart data |
| `GET` | `/export/csv` | Download CSV of all records |
| `GET` | `/export/excel` | Download Excel of all records |
| `POST` | `/retrain` | Force model retrain |
| `POST` | `/delete_user/<roll>` | Delete a user + their data |

### Example

```bash
curl http://localhost:5000/api/attendance/today
```

```json
{
  "date": "2025-10-14",
  "records": [
    {"name": "Biplaba", "roll": "2101", "time": "09:03:12", "status": "Present"},
    {"name": "Ananya",  "roll": "2102", "time": "09:05:44", "status": "Present"}
  ]
}
```

---

## ⚡ WebSocket Events

The dashboard subscribes to live events via Socket.IO:

```javascript
const socket = io();
socket.on('attendance_update', data => {
  // { name, roll, time, date }
  console.log(`${data.name} marked present at ${data.time}`);
});
```

---

## 🏗️ System Architecture

```
Webcam Input
    │
    ▼
Face Detection (Haar Cascade @ 30fps)
    │
    ├── Preprocessing: Grayscale → 50×50 resize
    │
    ├── KNN Model Prediction (scikit-learn, k=5)
    │
    └── SQLite Write (UNIQUE roll+date constraint)
            │
            └── WebSocket Broadcast → Live Dashboard Update
```

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/ -v
```

Tests cover: DB schema, attendance deduplication, helper functions, all API routes, and edge cases.

---

## 📊 Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 2.x |
| Real-time | Flask-SocketIO (eventlet) |
| Face Detection | OpenCV — Haar Cascade |
| Face Recognition | scikit-learn — KNN (k=5) |
| Database | SQLite (via Python stdlib) |
| Frontend | Bootstrap 5, Chart.js, Socket.IO |
| Export | Pandas + openpyxl |
| Deployment | Docker, docker-compose |
| CI/CD | GitHub Actions |

---

## 🔮 Roadmap

- [ ] Anti-spoofing / liveness detection
- [ ] Multi-camera support
- [ ] Deep learning upgrade (FaceNet / DeepFace)
- [ ] Email daily report to admin
- [ ] Cloud DB integration (PostgreSQL / Firebase)
- [ ] Mobile app (React Native)

---

## 🤝 Contributing

```bash
# Fork → branch → commit → PR
git checkout -b feature/YourFeature
git commit -m "feat: add YourFeature"
git push origin feature/YourFeature
# Open a Pull Request on GitHub
```

PRs welcome! Please run `pytest tests/` before submitting.

---

<div align="center">

Made with ❤️ by [BiplabaKrSamal](https://github.com/BiplabaKrSamal)

**If this saved you time, please ⭐ star the repo!**

</div>
