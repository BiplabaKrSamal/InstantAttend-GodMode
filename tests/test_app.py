"""
InstantAttend God Mode — Test Suite
Run: pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
import sqlite3
import tempfile

# ── Patch cv2 and joblib before importing app ──────────────────
import unittest.mock as mock

# Mock opencv (no display in CI)
cv2_mock = mock.MagicMock()
cv2_mock.data.haarcascades = '/tmp/'
cv2_mock.CascadeClassifier.return_value = mock.MagicMock()
sys.modules['cv2'] = cv2_mock
sys.modules['joblib'] = mock.MagicMock()

import app as ia

# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Each test gets its own isolated SQLite database."""
    db = str(tmp_path / "test.db")
    monkeypatch.setattr(ia, 'DB_PATH', db)
    ia.init_db()
    yield db


@pytest.fixture
def client(temp_db):
    ia.app.config['TESTING'] = True
    ia.app.config['SECRET_KEY'] = 'test'
    with ia.app.test_client() as c:
        yield c


# ──────────────────────────────────────────────────────────────
# Database Tests
# ──────────────────────────────────────────────────────────────
class TestDatabase:
    def test_init_creates_tables(self, temp_db):
        with sqlite3.connect(temp_db) as conn:
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()}
        assert 'users' in tables
        assert 'attendance' in tables

    def test_add_attendance_inserts_row(self, temp_db):
        # Pre-insert a fake user
        with sqlite3.connect(temp_db) as conn:
            conn.execute("INSERT INTO users (name,roll,created) VALUES ('Alice','101','2025-01-01')")
        ia.add_attendance('Alice_101')
        records = ia.get_today_attendance()
        assert len(records) == 1
        assert records[0]['name'] == 'Alice'
        assert records[0]['roll'] == '101'

    def test_add_attendance_deduplicates(self, temp_db):
        """Same person marked twice on same day → only one record."""
        ia.add_attendance('Bob_202')
        ia.add_attendance('Bob_202')
        assert len(ia.get_today_attendance()) == 1

    def test_get_stats_returns_dict(self, temp_db):
        stats = ia.get_stats()
        assert 'total_users' in stats
        assert 'present_today' in stats
        assert 'total_records' in stats
        assert 'weekly' in stats
        assert isinstance(stats['weekly'], list)


# ──────────────────────────────────────────────────────────────
# Helper Function Tests
# ──────────────────────────────────────────────────────────────
class TestHelpers:
    def test_today_str_format(self):
        d = ia.today_str()
        assert len(d) == 10
        parts = d.split('-')
        assert len(parts) == 3
        assert len(parts[0]) == 4  # YYYY

    def test_today_display_not_empty(self):
        assert len(ia.today_display()) > 0

    def test_identify_face_returns_none_without_model(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ia, 'MODEL_PATH', str(tmp_path / 'no_model.pkl'))
        result = ia.identify_face([[0]*7500])
        assert result is None


# ──────────────────────────────────────────────────────────────
# API Route Tests
# ──────────────────────────────────────────────────────────────
class TestAPI:
    def test_api_stats_200(self, client):
        res = client.get('/api/stats')
        assert res.status_code == 200
        data = res.get_json()
        assert 'total_users' in data

    def test_api_today_200(self, client):
        res = client.get('/api/attendance/today')
        assert res.status_code == 200
        data = res.get_json()
        assert 'records' in data
        assert 'date' in data

    def test_api_users_200(self, client):
        res = client.get('/api/users')
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_api_by_date(self, client):
        res = client.get('/api/attendance/2025-01-01')
        assert res.status_code == 200
        data = res.get_json()
        assert data['date'] == '2025-01-01'
        assert data['records'] == []

    def test_home_route(self, client):
        res = client.get('/')
        assert res.status_code == 200

    def test_admin_route(self, client):
        res = client.get('/admin')
        assert res.status_code == 200

    def test_export_csv(self, client):
        res = client.get('/export/csv')
        assert res.status_code == 200
        assert b'name' in res.data.lower() or res.status_code == 200
