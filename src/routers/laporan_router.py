"""Router untuk generate dan download laporan."""

import os
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.services.laporan_service import LaporanService, LAPORAN_DIR
from src.exceptions.custom import GagalSimpanError

router = APIRouter(prefix="/laporan")
templates = Jinja2Templates(directory="templates")
svc = LaporanService()


@router.get("", response_class=HTMLResponse)
async def halaman_laporan(request: Request):
    file_list = svc.daftar_file_laporan()
    return templates.TemplateResponse("laporan/list.html", {
        "request": request,
        "file_list": file_list,
        "judul_halaman": "Laporan",
        "pesan_error": None,
        "pesan_sukses": None,
    })


@router.post("/temuan-terbuka")
async def generate_temuan_terbuka(request: Request):
    try:
        path = svc.laporan_temuan_terbuka()
        nama = os.path.basename(path)
        return RedirectResponse(f"/laporan?sukses=Laporan+{nama}+berhasil+dibuat", status_code=303)
    except GagalSimpanError as e:
        file_list = svc.daftar_file_laporan()
        return templates.TemplateResponse("laporan/list.html", {
            "request": request,
            "file_list": file_list,
            "judul_halaman": "Laporan",
            "pesan_error": str(e),
            "pesan_sukses": None,
        })


@router.post("/keterlambatan")
async def generate_keterlambatan(request: Request):
    try:
        path = svc.laporan_keterlambatan()
        nama = os.path.basename(path)
        return RedirectResponse(f"/laporan?sukses=Laporan+{nama}+berhasil+dibuat", status_code=303)
    except GagalSimpanError as e:
        file_list = svc.daftar_file_laporan()
        return templates.TemplateResponse("laporan/list.html", {
            "request": request,
            "file_list": file_list,
            "judul_halaman": "Laporan",
            "pesan_error": str(e),
            "pesan_sukses": None,
        })


@router.post("/unit-berisiko")
async def generate_unit_berisiko(request: Request):
    try:
        path = svc.laporan_unit_berisiko()
        nama = os.path.basename(path)
        return RedirectResponse(f"/laporan?sukses=Laporan+{nama}+berhasil+dibuat", status_code=303)
    except GagalSimpanError as e:
        file_list = svc.daftar_file_laporan()
        return templates.TemplateResponse("laporan/list.html", {
            "request": request,
            "file_list": file_list,
            "judul_halaman": "Laporan",
            "pesan_error": str(e),
            "pesan_sukses": None,
        })


@router.post("/efektivitas")
async def generate_efektivitas(request: Request):
    try:
        path = svc.laporan_efektivitas()
        nama = os.path.basename(path)
        return RedirectResponse(f"/laporan?sukses=Laporan+{nama}+berhasil+dibuat", status_code=303)
    except GagalSimpanError as e:
        file_list = svc.daftar_file_laporan()
        return templates.TemplateResponse("laporan/list.html", {
            "request": request,
            "file_list": file_list,
            "judul_halaman": "Laporan",
            "pesan_error": str(e),
            "pesan_sukses": None,
        })


@router.get("/download/{filename}")
async def download_laporan(filename: str):
    nama_file = Path(filename).name
    if nama_file != filename:
        return RedirectResponse("/laporan", status_code=303)

    base_dir = Path(LAPORAN_DIR).resolve()
    path = (base_dir / nama_file).resolve()
    if base_dir not in path.parents or not path.exists():
        return RedirectResponse("/laporan", status_code=303)
    return FileResponse(str(path), filename=nama_file)
