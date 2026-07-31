"""Router untuk temuan dan bukti audit."""

from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import shutil
import uuid
from src.services.temuan_service import TemuanService
from src.services.audit_service import AuditService
from src.services.tindak_lanjut_service import TindakLanjutService
from src.exceptions.custom import BuktiAuditTidakCukupError, DataTidakValidError, StatusTransisiTidakValidError

router = APIRouter(prefix="/temuan")
templates = Jinja2Templates(directory="templates")
svc = TemuanService()
audit_svc = AuditService()
tl_svc = TindakLanjutService()


@router.get("", response_class=HTMLResponse)
async def daftar_temuan(request: Request, jenis: str = "", status: str = ""):
    semua = svc.daftar_temuan()
    if jenis:
        semua = [t for t in semua if t.JENIS == jenis]
    if status:
        semua = [t for t in semua if t.status_tindak_lanjut == status]
    unit_map = {u.id: u.nama for u in audit_svc.daftar_unit()}
    return templates.TemplateResponse("temuan/list.html", {
        "request": request,
        "temuan_list": semua,
        "unit_map": unit_map,
        "filter_jenis": jenis,
        "filter_status": status,
        "judul_halaman": "Daftar Temuan",
    })


@router.get("/tambah", response_class=HTMLResponse)
async def form_tambah_temuan(request: Request):
    return templates.TemplateResponse("temuan/form.html", {
        "request": request,
        "audit_list": audit_svc.daftar_audit(),
        "unit_list": audit_svc.daftar_unit(),
        "temuan": None,
        "judul_halaman": "Tambah Temuan",
        "pesan_error": None,
    })


@router.post("/tambah")
async def simpan_tambah_temuan(
    request: Request,
    program_audit_id: str = Form(...),
    unit_kerja_id: str = Form(...),
    jenis: str = Form(...),
    judul: str = Form(...),
    deskripsi: str = Form(...),
    dampak: int = Form(...),
    kemungkinan: int = Form(...),
    tingkat_kepatuhan: float = Form(...),
    rekomendasi: str = Form(""),
    batas_tindak_lanjut: str = Form(""),
):
    try:
        svc.tambah_temuan({
            "program_audit_id": program_audit_id,
            "unit_kerja_id": unit_kerja_id,
            "jenis": jenis,
            "judul": judul,
            "deskripsi": deskripsi,
            "dampak": dampak,
            "kemungkinan": kemungkinan,
            "tingkat_kepatuhan": tingkat_kepatuhan,
            "rekomendasi": rekomendasi,
            "batas_tindak_lanjut": batas_tindak_lanjut,
        })
        return RedirectResponse("/temuan", status_code=303)
    except DataTidakValidError as e:
        return templates.TemplateResponse("temuan/form.html", {
            "request": request,
            "audit_list": audit_svc.daftar_audit(),
            "unit_list": audit_svc.daftar_unit(),
            "temuan": None,
            "judul_halaman": "Tambah Temuan",
            "pesan_error": str(e),
        })


@router.get("/{id}", response_class=HTMLResponse)
async def detail_temuan(request: Request, id: str):
    temuan = svc.detail_temuan(id)
    if not temuan:
        return RedirectResponse("/temuan", status_code=303)
    bukti_list = svc.daftar_bukti(id)
    tl_list = tl_svc.tindak_lanjut_per_temuan(id)
    unit = audit_svc.detail_unit(temuan.unit_kerja_id)
    return templates.TemplateResponse("temuan/detail.html", {
        "request": request,
        "temuan": temuan,
        "bukti_list": bukti_list,
        "tl_list": tl_list,
        "unit": unit,
        "judul_halaman": "Detail Temuan",
        "pesan_error": None,
        "pesan_sukses": None,
    })


@router.post("/{id}/tutup")
async def tutup_temuan(request: Request, id: str):
    try:
        svc.tutup_temuan(id)
        temuan = svc.detail_temuan(id)
        bukti_list = svc.daftar_bukti(id)
        tl_list = tl_svc.tindak_lanjut_per_temuan(id)
        unit = audit_svc.detail_unit(temuan.unit_kerja_id)
        return templates.TemplateResponse("temuan/detail.html", {
            "request": request,
            "temuan": temuan,
            "bukti_list": bukti_list,
            "tl_list": tl_list,
            "unit": unit,
            "judul_halaman": "Detail Temuan",
            "pesan_error": None,
            "pesan_sukses": "Temuan berhasil ditutup.",
        })
    except (BuktiAuditTidakCukupError, DataTidakValidError, StatusTransisiTidakValidError) as e:
        temuan = svc.detail_temuan(id)
        bukti_list = svc.daftar_bukti(id)
        tl_list = tl_svc.tindak_lanjut_per_temuan(id)
        unit = audit_svc.detail_unit(temuan.unit_kerja_id) if temuan else None
        return templates.TemplateResponse("temuan/detail.html", {
            "request": request,
            "temuan": temuan,
            "bukti_list": bukti_list,
            "tl_list": tl_list,
            "unit": unit,
            "judul_halaman": "Detail Temuan",
            "pesan_error": str(e),
            "pesan_sukses": None,
        })


@router.post("/{id}/status")
async def ubah_status_temuan(id: str, status_baru: str = Form(...)):
    try:
        svc.ubah_status(id, status_baru)
    except (DataTidakValidError, StatusTransisiTidakValidError):
        pass
    return RedirectResponse(f"/temuan/{id}", status_code=303)


@router.get("/{id}/edit", response_class=HTMLResponse)
async def form_edit_temuan(request: Request, id: str):
    temuan = svc.detail_temuan(id)
    if not temuan:
        return RedirectResponse("/temuan", status_code=303)
    return templates.TemplateResponse("temuan/form.html", {
        "request": request,
        "audit_list": audit_svc.daftar_audit(),
        "unit_list": audit_svc.daftar_unit(),
        "temuan": temuan,
        "judul_halaman": "Edit Temuan",
        "pesan_error": None,
    })


@router.post("/{id}/edit")
async def simpan_edit_temuan(
    request: Request,
    id: str,
    judul: str = Form(...),
    deskripsi: str = Form(...),
    dampak: int = Form(...),
    kemungkinan: int = Form(...),
    tingkat_kepatuhan: float = Form(...),
    rekomendasi: str = Form(""),
    batas_tindak_lanjut: str = Form(""),
):
    try:
        svc.perbarui_temuan(id, {
            "judul": judul,
            "deskripsi": deskripsi,
            "dampak": dampak,
            "kemungkinan": kemungkinan,
            "tingkat_kepatuhan": tingkat_kepatuhan,
            "rekomendasi": rekomendasi,
            "batas_tindak_lanjut": batas_tindak_lanjut,
        })
        return RedirectResponse(f"/temuan/{id}", status_code=303)
    except DataTidakValidError as e:
        temuan = svc.detail_temuan(id)
        return templates.TemplateResponse("temuan/form.html", {
            "request": request,
            "audit_list": audit_svc.daftar_audit(),
            "unit_list": audit_svc.daftar_unit(),
            "temuan": temuan,
            "judul_halaman": "Edit Temuan",
            "pesan_error": str(e),
        })


@router.post("/{id}/hapus")
async def hapus_temuan(id: str):
    svc.hapus_temuan(id)
    return RedirectResponse("/temuan", status_code=303)


# --- Bukti ---

@router.post("/{temuan_id}/bukti/tambah")
async def tambah_bukti(
    temuan_id: str,
    judul: str = Form(...),
    tipe: str = Form(...),
    deskripsi: str = Form(""),
    file: UploadFile = File(None),
):
    lokasi_file = ""
    # Jika ada file yang di-upload, simpan secara fisik
    if file and file.filename:
        upload_dir = os.path.join("data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        # Buat nama file unik agar tidak bertabrakan
        ekstensi = os.path.splitext(file.filename)[1]
        nama_unik = f"{uuid.uuid4().hex}{ekstensi}"
        path_simpan = os.path.join(upload_dir, nama_unik)
        with open(path_simpan, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Simpan lokasi relatif yang bisa diakses dari browser
        lokasi_file = f"/uploads/{nama_unik}"
    try:
        svc.tambah_bukti({
            "temuan_id": temuan_id,
            "judul": judul,
            "tipe": tipe,
            "deskripsi": deskripsi,
            "lokasi_file": lokasi_file,
        })
    except DataTidakValidError:
        pass
    return RedirectResponse(f"/temuan/{temuan_id}", status_code=303)


@router.post("/{temuan_id}/bukti/{bukti_id}/hapus")
async def hapus_bukti(temuan_id: str, bukti_id: str):
    svc.hapus_bukti(bukti_id)
    return RedirectResponse(f"/temuan/{temuan_id}", status_code=303)
