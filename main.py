"""Entry point aplikasi FastAPI Sistem Audit Kepatuhan."""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.routers import dashboard, audit_router, temuan_router, tindak_lanjut_router, laporan_router

app = FastAPI(
    title="Sistem Audit Kepatuhan",
    description="Aplikasi web untuk audit kepatuhan dan tindak lanjut temuan",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(dashboard.router)
app.include_router(audit_router.router)
app.include_router(temuan_router.router)
app.include_router(tindak_lanjut_router.router)
app.include_router(laporan_router.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
