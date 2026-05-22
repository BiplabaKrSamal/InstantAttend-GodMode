.PHONY: run install test lint seed export docker-up docker-down clean help

help:
	@echo ""
	@echo "  InstantAttend-GodMode — Dev Commands"
	@echo "  ─────────────────────────────────────────"
	@echo "  make install     Install Python dependencies"
	@echo "  make run         Start Flask app (dev mode)"
	@echo "  make test        Run full pytest suite"
	@echo "  make lint        Run flake8 linter"
	@echo "  make seed        Seed demo data (5 users, 14 days)"
	@echo "  make export      Print attendance summary to terminal"
	@echo "  make docker-up   Start with Docker Compose"
	@echo "  make docker-down Stop Docker containers"
	@echo "  make clean       Remove cache files"
	@echo ""

install:
	pip install -r requirements.txt

run:
	python app.py

test:
	pytest tests/ -v --tb=short

lint:
	flake8 app.py --count --max-line-length=120 --statistics

seed:
	python scripts/seed_db.py --users 5 --days 14

seed-full:
	python scripts/seed_db.py --users 15 --days 30 --reset

export:
	python scripts/export_report.py --format summary

docker-up:
	docker compose up --build

docker-down:
	docker compose down

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
