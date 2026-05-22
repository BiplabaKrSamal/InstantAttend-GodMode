"""
Gunicorn production configuration for InstantAttend-GodMode.
Usage: gunicorn -c gunicorn.conf.py app:app
"""
import os
import multiprocessing

# ── Server socket ─────────────────────────────────────────────
bind    = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
backlog = 2048

# ── Workers ───────────────────────────────────────────────────
# Must stay at 1 for WebSocket / SocketIO (eventlet)
workers    = 1
worker_class = 'eventlet'
worker_connections = 1000
timeout    = 120
keepalive  = 5

# ── Logging ───────────────────────────────────────────────────
accesslog  = '-'         # stdout
errorlog   = '-'         # stderr
loglevel   = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s %(f)s %(a)s'

# ── Process naming ────────────────────────────────────────────
proc_name  = 'instantattend-godmode'

# ── Server mechanics ─────────────────────────────────────────
preload_app     = True
daemon          = False
pidfile         = None
user            = None
group           = None
umask           = 0
tmp_upload_dir  = None
