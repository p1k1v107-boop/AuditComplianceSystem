"""Router untuk tindak lanjut dan rekomendasi."""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.services.tindak_lanjut_service import TindakLanjutService
from src.services.audit_service import AuditService
from src.services.temuan_service import TemuanService
from src.exceptions.custom import TindakLanjutTerlambatError, DataTidakValidError

router = APIRouter(prefix="/tindak-lanjut")
templates = Jinja2Templates(directory="templates")
svc = TindakLanjutService()
audit_svc = AuditService()
temuan_svc = TemuanService()


@router.get("", response_class=HTMLResponse)
async def daftar_tindak_lanjut(request: Request, status: str = ""):
    semua = svc.daftar_tindak_lanjut()
    if status:
        semua = [tl for tl in semua if tl.status == status]
    temuan_map = {t.id: t.judul for t in temuan_svc.daftar_temuan()}
    unit_map = {u.id: u.nama for u in audit_svc.daftar_unit()}
    return templates.TemplateResponse("tindak_lanjut/list.html", {
        "request": request,
        "tl_list": semua,
        "temuan_map": temuan_map,
        "unit_map": unit_map,
        "filter_status": status,
        "judul_halaman": "Tindak Lanjut",
    })


@router.get("/tambah", response_class=HTMLResponse)
async def form_tambah(request: Request):
    return templates.TemplateResponse("tindak_lanjut/form.html", {
        "request": request,
        "temuan_list": temuan_svc.daftar_temuan(),
        "unit_list": audit_svc.daftar_unit(),
        "tl": None,
        "judul_halaman": "Tambah Tindak Lanjut",
        "pesan_error": None,
    })


@router.post("/tambah")
async def simpan_tambah(
    request: Request,
    temuan_id: str = Form(...),
    unit_kerja_id: str = Form(...),
    tipe_tindakan: str = Form(...),
    deskripsi: str = Form(...),
    penanggung_jawab: str = Form(...),
    batas_waktu: str = Form(...),
    tanggal_pelaksanaan: str = Form(""),
    catatan: str = Form(""),
):
    try:
        svc.tambah_tindak_lanjut({
            "temuan_id": temuan_id,
            "unit_kerja_id": unit_kerja_id,
            "tipe_tindakan": tipe_tindakan,
            "deskripsi": deskripsi,
            "penanggung_jawab": penanggung_jawab,
            "batas_waktu": batas_waktu,
            "tanggal_pelaksanaan": tanggal_pelaksanaan,
            "catatan": catatan,
        })
        return RedirectResponse("/tindak-lanjut", status_code=303)
    except DataTidakValidError as e:
        return templates.TemplateResponse("tindak_lanjut/form.html", {
            "request": request,
            "temuan_list": temuan_svc.daftar_temuan(),
            "unit_list": audit_svc.daftar_unit(),
            "tl": None,
            "judul_halaman": "Tambah Tindak Lanjut",
            "pesan_error": str(e),
        })


@router.get("/{id}", response_class=HTMLResponse)
async def detail_tindak_lanjut(request: Request, id: str):
    tl = svc.detail_tindak_lanjut(id)
    if not tl:
        return RedirectResponse("/tindak-lanjut", status_code=303)
    temuan = temuan_svc.detail_temuan(tl.temuan_id)
    unit = audit_svc.detail_unit(tl.unit_kerja_id)
    return templates.TemplateResponse("tindak_lanjut/detail.html", {
        "request": request,
        "tl": tl,
        "temuan": temuan,
        "unit": unit,
        "judul_halaman": "Detail Tindak Lanjut",
        "pesan_error": None,
        "pesan_sukses": None,
    })


@router.post("/{id}/status")
async def ubah_status(
    request: Request,
    id: str,
    status_baru: str = Form(...),
    catatan: str = Form(""),
):
    try:
        svc.perbarui_status(id, status_baru, catatan)
        return RedirectResponse(f"/tindak-lanjut/{id}", status_code=303)
    except TindakLanjutTerlambatError as e:
        tl = svc.detail_tindak_lanjut(id)
        temuan = temuan_svc.detail_temuan(tl.temuan_id) if tl else None
        unit = audit_svc.detail_unit(tl.unit_kerja_id) if tl else None
        return templates.TemplateResponse("tindak_lanjut/detail.html", {
            "request": request,
            "tl": tl,
            "temuan": temuan,
            "unit": unit,
            "judul_halaman": "Detail Tindak Lanjut",
            "pesan_error": str(e),
            "pesan_sukses": None,
        })


@router.post("/{id}/hapus")
async def hapus_tindak_lanjut(id: str):
    svc.hapus_tindak_lanjut(id)
    return RedirectResponse("/tindak-lanjut", status_code=303)
