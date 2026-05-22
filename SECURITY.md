# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x (God Mode) | ✅ Active |
| 1.x (Original) | ❌ No longer maintained |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not open a public GitHub issue**.

Instead, report it privately:

1. Go to the [Security tab](../../security/advisories/new) on this repo
2. Click **"Report a vulnerability"**
3. Fill in the details — include steps to reproduce, impact, and any suggested fix

You will receive an acknowledgement within **48 hours** and a resolution or update within **7 days**.

## Scope

In scope:
- SQL injection or database exposure
- Authentication/authorisation bypass
- Remote code execution
- Path traversal / file inclusion
- Sensitive data exposure (face data, attendance records)

Out of scope:
- Denial of service via webcam overload
- Social engineering attacks
- Issues requiring physical access to the machine running the server

## Security Notes for Deployment

- **Change `SECRET_KEY`** — set the `SECRET_KEY` environment variable in production, never use the default
- **Restrict network access** — do not expose port 5000 publicly without a reverse proxy + TLS
- **Face data is local** — all face images and the KNN model are stored on disk; ensure the `static/faces/` directory is not publicly accessible
- **SQLite is local** — `attendance.db` should not be in a web-accessible directory
- **Use Docker volumes** — mount `static/faces/` and `attendance.db` outside the container for persistence and backup
