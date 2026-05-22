"""
InstantAttend-GodMode — Centralised Configuration
All tunables live here; override with environment variables in production.
"""
import os

class Config:
    # ── Security ─────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'instantattend-godmode-dev-key-change-in-prod')

    # ── Database ─────────────────────────────────────────────
    DB_PATH    = os.environ.get('DB_PATH', 'attendance.db')

    # ── Face recognition ─────────────────────────────────────
    FACES_DIR  = os.environ.get('FACES_DIR', 'static/faces')
    MODEL_PATH = os.environ.get('MODEL_PATH', 'static/face_recognition_model.pkl')
    FACE_SAMPLES        = int(os.environ.get('FACE_SAMPLES', 50))        # samples per user
    FACE_SAMPLE_EVERY   = int(os.environ.get('FACE_SAMPLE_EVERY', 10))   # capture every N frames
    KNN_NEIGHBORS       = int(os.environ.get('KNN_NEIGHBORS', 5))
    HAAR_SCALE_FACTOR   = float(os.environ.get('HAAR_SCALE_FACTOR', 1.3))
    HAAR_MIN_NEIGHBORS  = int(os.environ.get('HAAR_MIN_NEIGHBORS', 5))

    # ── Flask-SocketIO ────────────────────────────────────────
    SOCKETIO_ASYNC_MODE = os.environ.get('SOCKETIO_ASYNC_MODE', 'threading')
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '*')

    # ── Server ───────────────────────────────────────────────
    HOST  = os.environ.get('HOST', '0.0.0.0')
    PORT  = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_ENV', 'development') == 'development'


class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')   # must be set — no fallback


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DB_PATH  = ':memory:'


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     DevelopmentConfig,
}
