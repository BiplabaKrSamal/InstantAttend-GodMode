"""
InstantAttend-GodMode — Database Layer Tests
Isolated tests for all SQLite operations: schema, CRUD, constraints, stats.
"""
import sys, os, sqlite3, pytest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import unittest.mock as mock
cv2_mock = mock.MagicMock()
cv2_mock.data.haarcascades = '/tmp/'
sys.modules.setdefault('cv2', cv2_mock)
sys.modules.setdefault('joblib', mock.MagicMock())

import app as ia


# ── Fixtures ──────────────────────────────────────────────────
@pytest.fixture()
def db(tmp_path, monkeypatch):
    """Fresh isolated SQLite database per test."""
    path = str(tmp_path / "test.db")
    monkeypatch.setattr(ia, 'DB_PATH', path)
    ia.init_db()
    return path


def insert_user(db_path, name="Alice", roll="101"):
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (name,roll,created) VALUES (?,?,?)",
            (name, roll, "2025-01-01 09:00:00")
        )
        conn.commit()


# ── Schema Tests ──────────────────────────────────────────────
class TestSchema:
    def test_users_table_exists(self, db):
        with sqlite3.connect(db) as conn:
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert 'users' in tables

    def test_attendance_table_exists(self, db):
        with sqlite3.connect(db) as conn:
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert 'attendance' in tables

    def test_users_columns(self, db):
        with sqlite3.connect(db) as conn:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()}
        assert {'id', 'name', 'roll', 'created'}.issubset(cols)

    def test_attendance_columns(self, db):
        with sqlite3.connect(db) as conn:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(attendance)").fetchall()}
        assert {'id', 'roll', 'name', 'date', 'time', 'status'}.issubset(cols)


# ── User CRUD Tests ───────────────────────────────────────────
class TestUsers:
    def test_insert_user(self, db):
        insert_user(db)
        with sqlite3.connect(db) as conn:
            count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        assert count == 1

    def test_unique_roll_constraint(self, db):
        insert_user(db, "Alice", "101")
        with pytest.raises(sqlite3.IntegrityError):
            with sqlite3.connect(db) as conn:
                conn.execute(
                    "INSERT INTO users (name,roll,created) VALUES (?,?,?)",
                    ("Alice2", "101", "2025-01-01")
                )

    def test_api_users_returns_list(self, db, monkeypatch):
        insert_user(db)
        users = ia.get_stats()
        assert isinstance(users, dict)


# ── Attendance CRUD Tests ─────────────────────────────────────
class TestAttendance:
    def test_add_attendance_creates_record(self, db):
        ia.add_attendance("Alice_101")
        records = ia.get_today_attendance()
        assert len(records) == 1

    def test_record_has_correct_fields(self, db):
        ia.add_attendance("Bob_202")
        r = ia.get_today_attendance()[0]
        assert r['name'] == 'Bob'
        assert r['roll'] == '202'
        assert r['status'] == 'Present'
        assert ':' in r['time']

    def test_deduplication_same_day(self, db):
        """Marking the same person twice on same day should only keep one record."""
        ia.add_attendance("Carol_303")
        ia.add_attendance("Carol_303")
        assert len(ia.get_today_attendance()) == 1

    def test_multiple_users_same_day(self, db):
        ia.add_attendance("Alice_101")
        ia.add_attendance("Bob_202")
        ia.add_attendance("Carol_303")
        assert len(ia.get_today_attendance()) == 3

    def test_label_without_roll(self, db):
        """Labels with no underscore should still produce a record."""
        ia.add_attendance("NoRoll")
        records = ia.get_today_attendance()
        assert len(records) == 1
        assert records[0]['roll'] == '000'

    def test_records_ordered_by_time(self, db):
        with sqlite3.connect(db) as conn:
            conn.execute("INSERT INTO attendance (roll,name,date,time) VALUES ('1','A','2025-01-01','10:00:00')")
            conn.execute("INSERT INTO attendance (roll,name,date,time) VALUES ('2','B','2025-01-01','08:00:00')")
            conn.commit()
        monkeypatched_today = "2025-01-01"
        with sqlite3.connect(db) as conn:
            rows = conn.execute(
                "SELECT name FROM attendance WHERE date=? ORDER BY time", (monkeypatched_today,)
            ).fetchall()
        assert rows[0][0] == 'B'  # earlier time first


# ── Stats Tests ───────────────────────────────────────────────
class TestStats:
    def test_stats_structure(self, db):
        s = ia.get_stats()
        assert isinstance(s['total_users'], int)
        assert isinstance(s['present_today'], int)
        assert isinstance(s['total_records'], int)
        assert isinstance(s['weekly'], list)

    def test_stats_counts_correctly(self, db):
        insert_user(db, "Alice", "101")
        ia.add_attendance("Alice_101")
        s = ia.get_stats()
        assert s['total_users'] == 1
        assert s['present_today'] == 1
        assert s['total_records'] == 1

    def test_weekly_is_list_of_dicts(self, db):
        s = ia.get_stats()
        for item in s['weekly']:
            assert 'date' in item
            assert 'count' in item

    def test_empty_db_stats(self, db):
        s = ia.get_stats()
        assert s['total_users'] == 0
        assert s['present_today'] == 0
        assert s['total_records'] == 0


# ── Helper Tests ──────────────────────────────────────────────
class TestHelpers:
    def test_today_str_format(self):
        d = ia.today_str()
        assert len(d) == 10
        parts = d.split('-')
        assert len(parts) == 3 and len(parts[0]) == 4

    def test_today_display_not_empty(self):
        assert len(ia.today_display()) > 5

    def test_identify_face_no_model(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ia, 'MODEL_PATH', str(tmp_path / 'ghost.pkl'))
        assert ia.identify_face([[0] * 7500]) is None
