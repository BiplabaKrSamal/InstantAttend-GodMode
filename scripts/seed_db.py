#!/usr/bin/env python3
"""
InstantAttend-GodMode — Demo Data Seeder
Seeds realistic attendance records for showcasing the dashboard.

Usage:
    python scripts/seed_db.py              # seeds 5 users, 14 days
    python scripts/seed_db.py --users 20  # custom user count
    python scripts/seed_db.py --reset     # wipe and re-seed
"""
import sys, os, sqlite3, random, argparse
from datetime import date, timedelta, datetime

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = os.environ.get('DB_PATH', 'attendance.db')

DEMO_USERS = [
    ("Biplaba_Samal",  "2101"),
    ("Ananya_Roy",     "2102"),
    ("Rahul_Das",      "2103"),
    ("Priya_Sharma",   "2104"),
    ("Arjun_Singh",    "2105"),
    ("Sneha_Patel",    "2106"),
    ("Karan_Mehta",    "2107"),
    ("Divya_Nair",     "2108"),
    ("Rohan_Gupta",    "2109"),
    ("Pooja_Verma",    "2110"),
    ("Amit_Kumar",     "2111"),
    ("Neha_Joshi",     "2112"),
    ("Siddharth_Rao",  "2113"),
    ("Kritika_Mishra", "2114"),
    ("Vishal_Tiwari",  "2115"),
]


def init_db(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        roll TEXT NOT NULL UNIQUE, created TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT, roll TEXT NOT NULL,
        name TEXT NOT NULL, date TEXT NOT NULL, time TEXT NOT NULL,
        status TEXT DEFAULT 'Present', UNIQUE(roll, date))""")
    conn.commit()


def seed(users_n=5, days=14, attendance_rate=0.80):
    users = DEMO_USERS[:users_n]
    today = date.today()

    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)

        # Insert users
        for name, roll in users:
            conn.execute(
                "INSERT OR IGNORE INTO users (name,roll,created) VALUES (?,?,?)",
                (name, roll, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

        # Insert attendance records
        seeded = 0
        for offset in range(days, -1, -1):
            day = today - timedelta(days=offset)
            day_str = day.strftime("%Y-%m-%d")
            # Skip weekends
            if day.weekday() >= 5:
                continue
            for name, roll in users:
                if random.random() < attendance_rate:
                    hour   = random.randint(8, 10)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
                    try:
                        conn.execute(
                            "INSERT OR IGNORE INTO attendance (roll,name,date,time) VALUES (?,?,?,?)",
                            (roll, name, day_str, time_str)
                        )
                        seeded += 1
                    except Exception:
                        pass

        conn.commit()
        print(f"✓ Seeded {users_n} users · {seeded} attendance records · {days} days")
        print(f"  Database: {os.path.abspath(DB_PATH)}")
        print(f"  Run 'python app.py' and open http://127.0.0.1:5000")


def reset():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM attendance")
        conn.execute("DELETE FROM users")
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('users','attendance')")
        conn.commit()
    print("✓ Database cleared")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seed demo data into InstantAttend-GodMode')
    parser.add_argument('--users',       type=int,  default=5,    help='Number of demo users (max 15)')
    parser.add_argument('--days',        type=int,  default=14,   help='Number of days to seed')
    parser.add_argument('--rate',        type=float,default=0.80, help='Attendance rate 0.0–1.0')
    parser.add_argument('--reset',       action='store_true',      help='Wipe existing data first')
    args = parser.parse_args()

    if args.reset:
        reset()

    seed(
        users_n=min(args.users, len(DEMO_USERS)),
        days=args.days,
        attendance_rate=args.rate
    )
