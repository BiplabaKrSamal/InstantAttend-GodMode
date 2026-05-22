# Changelog

All notable changes to InstantAttend-GodMode are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.0.0] — 2025-10-14 — God Mode

### Added
- **SQLite database** replacing CSV files — structured storage, UNIQUE daily constraints, full history
- **REST API** — `/api/attendance/today`, `/api/attendance/<date>`, `/api/users`, `/api/stats`
- **WebSocket live updates** via Flask-SocketIO — dashboard refreshes in real-time on every mark
- **Admin panel** — full user management, delete users + face data, attendance history view
- **Weekly bar chart** — Chart.js 7-day attendance visualisation on dashboard
- **Export to Excel** — `.xlsx` download alongside existing CSV export
- **Docker + docker-compose** — one-command production deployment with volume persistence
- **GitHub Actions CI/CD** — lint → test → GitHub Pages deploy → Docker build check
- **GitHub Pages landing page** in `docs/index.html` — auto-deployed on push to main
- **pytest test suite** — covers DB schema, attendance logic, deduplication, all API routes
- **Dedicated DB tests** in `tests/test_db.py` — schema, CRUD, constraints, stats, helpers
- **Separated CSS/JS** — `static/css/style.css` + `static/js/main.js` (no more inline styles)
- **`config.py`** — centralised configuration with environment variable overrides
- **`gunicorn.conf.py`** — production server config (eventlet, logging, timeouts)
- **`scripts/seed_db.py`** — demo data seeder with 15 realistic users, configurable days/rate
- **`scripts/export_report.py`** — standalone CLI report exporter (CSV / Excel / summary)
- **Makefile** — `make run`, `make test`, `make lint`, `make docker-up`, `make clean`
- **`setup.cfg`** — project metadata, pytest config, flake8 config
- **`CONTRIBUTING.md`** — contribution guide
- **`SECURITY.md`** — security policy and responsible disclosure process
- **`CHANGELOG.md`** — this file
- **GitHub issue templates** — bug report + feature request
- **GitHub PR template** — standardised pull request checklist
- **`docs/.nojekyll`** — ensures GitHub Pages serves static assets correctly

### Changed
- Face registration now stores users in SQLite in addition to filesystem
- `identify_face()` returns `None` gracefully when no model exists (no crash)
- Toast notifications appear in real-time as attendance is marked via WebSocket
- Dashboard stat cards auto-update live without page refresh

### Removed
- Direct CSV writes during attendance (replaced by SQLite; CSV still available via `/export/csv`)

---

## [1.0.0] — 2024-01-01 — Original

### Added
- Basic face registration via OpenCV + Haar Cascade
- KNN model training with scikit-learn
- Real-time webcam attendance marking
- CSV file storage
- Simple Flask dashboard
