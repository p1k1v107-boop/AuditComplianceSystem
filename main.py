"""Entry point aplikasi FastAPI Sistem Audit Kepatuhan."""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.routers import audit_router, dashboard, laporan_router, temuan_router, tindak_lanjut_router
from src.core.paths import STATIC_DIR, UPLOADS_DIR


def create_app() -> FastAPI:
    app = FastAPI(
        title="Sistem Audit Kepatuhan",
        description="Aplikasi web untuk audit kepatuhan dan tindak lanjut temuan",
        version="1.0.0",
    )

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

    app.include_router(dashboard.router)
    app.include_router(audit_router.router)
    app.include_router(temuan_router.router)
    app.include_router(tindak_lanjut_router.router)
    app.include_router(laporan_router.router)
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
