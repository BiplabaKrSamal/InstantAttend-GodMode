"""
pytest root configuration for InstantAttend God Mode.
Ensures the project root is on sys.path for all test modules.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
