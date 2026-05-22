#!/usr/bin/env python3
"""
InstantAttend-GodMode — CLI Report Exporter
Export attendance data without running the web server.

Usage:
    python scripts/export_report.py --format csv
    python scripts/export_report.py --format excel --from 2025-01-01 --to 2025-01-31
    python scripts/export_report.py --format summary
"""
import sys, os, sqlite3, argparse
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.environ.get('DB_PATH', 'attendance.db')


def get_records(from_date=None, to_date=None):
    if not os.path.exists(DB_PATH):
        print(f"No database found at {DB_PATH}. Run 'python scripts/seed_db.py' first.")
        sys.exit(1)
    with sqlite3.connect(DB_PATH) as conn:
        query = "SELECT name,roll,date,time,status FROM attendance"
        params = []
        if from_date and to_date:
            query += " WHERE date BETWEEN ? AND ?"
            params = [from_date, to_date]
        elif from_date:
            query += " WHERE date >= ?"
            params = [from_date]
        query += " ORDER BY date DESC, time ASC"
        rows = conn.execute(query, params).fetchall()
    return rows


def export_csv(rows, outfile=None):
    import csv, io
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['Name', 'Roll', 'Date', 'Time', 'Status'])
    writer.writerows(rows)
    out = outfile or f"Attendance_{date.today()}.csv"
    with open(out, 'w', newline='') as f:
        f.write(buf.getvalue())
    print(f"✓ CSV exported → {os.path.abspath(out)}  ({len(rows)} records)")


def export_excel(rows, outfile=None):
    try:
        import pandas as pd
    except ImportError:
        print("pandas not installed. Run: pip install pandas openpyxl")
        sys.exit(1)
    df = pd.DataFrame(rows, columns=['Name', 'Roll', 'Date', 'Time', 'Status'])
    out = outfile or f"Attendance_{date.today()}.xlsx"
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    print(f"✓ Excel exported → {os.path.abspath(out)}  ({len(rows)} records)")


def print_summary(from_date=None, to_date=None):
    if not os.path.exists(DB_PATH):
        print(f"No database at {DB_PATH}")
        sys.exit(1)
    with sqlite3.connect(DB_PATH) as conn:
        total_users   = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_records = conn.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]
        today_present = conn.execute(
            "SELECT COUNT(*) FROM attendance WHERE date=?", (str(date.today()),)).fetchone()[0]
        by_date = conn.execute(
            "SELECT date, COUNT(*) FROM attendance GROUP BY date ORDER BY date DESC LIMIT 10"
        ).fetchall()

    print("\n  📊 InstantAttend-GodMode — Attendance Summary")
    print("  " + "─" * 42)
    print(f"  Registered users  : {total_users}")
    print(f"  Total records     : {total_records}")
    print(f"  Present today     : {today_present}")
    if total_users:
        rate = int((today_present / total_users) * 100)
        print(f"  Today's rate      : {rate}%")
    print(f"\n  Last 10 days:")
    for d, cnt in by_date:
        bar = '█' * cnt + '░' * max(0, total_users - cnt)
        print(f"  {d}  {bar}  {cnt}/{total_users}")
    print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export InstantAttend-GodMode attendance reports')
    parser.add_argument('--format', choices=['csv', 'excel', 'summary'], default='summary')
    parser.add_argument('--from',   dest='from_date', default=None, help='Start date YYYY-MM-DD')
    parser.add_argument('--to',     dest='to_date',   default=None, help='End date YYYY-MM-DD')
    parser.add_argument('--out',    dest='outfile',    default=None, help='Output filename')
    args = parser.parse_args()

    if args.format == 'summary':
        print_summary(args.from_date, args.to_date)
    else:
        rows = get_records(args.from_date, args.to_date)
        if not rows:
            print("No records found for the given date range.")
            sys.exit(0)
        if args.format == 'csv':
            export_csv(rows, args.outfile)
        elif args.format == 'excel':
            export_excel(rows, args.outfile)
