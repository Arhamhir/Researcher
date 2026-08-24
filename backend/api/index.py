"""Vercel serverless entrypoint.

Vercel's Python runtime looks for an ASGI `app` object in files under
`api/`. This just re-exports the real FastAPI app from app/main.py so the
whole project (routes, CORS, etc.) runs unchanged behind Vercel.
"""
import sys
from pathlib import Path

# Make the backend/ root (parent of this api/ folder) importable so
# `from app.main import app` resolves the same way it does locally.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402
