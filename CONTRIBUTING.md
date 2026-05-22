# Contributing to InstantAttend God Mode

Thank you for taking the time to contribute! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/BiplabaKrSamal/InstantAttend-GodMode.git
cd InstantAttend-GodMode
pip install -r requirements.txt
python app.py
```

## Running Tests

```bash
make test
# or: pytest tests/ -v
```

## Coding Standards

- Python: PEP 8, max line length 120 — run `make lint` before committing
- Commits: use conventional prefixes — `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- All new features need at least one test in `tests/test_app.py`

## Pull Request Flow

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make changes + add tests
4. Run `make lint && make test` — both must pass
5. Push and open a PR against `main`

## Reporting Bugs

Use the GitHub Issues tab and fill in the bug report template.

## Feature Requests

Open an issue with the feature request template and describe the use case.
