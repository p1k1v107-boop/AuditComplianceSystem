"""Path absolut yang dipakai konsisten di seluruh aplikasi."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = DATA_DIR / "uploads"
LAPORAN_DIR = DATA_DIR / "laporan"
