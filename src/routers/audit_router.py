"""Router untuk program audit, auditor, dan unit kerja."""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.services.audit_service import AuditService
from src.exceptions.custom import DataTidakValidError

router = APIRouter(prefix="/audit")
templates = Jinja2Templates(directory="templates")
svc = AuditService()


# --- Program Audit ---

@router.get("", response_class=HTMLResponse)
async def daftar_audit(request: Request):
    audit_list = svc.daftar_audit()
    unit_map = {u.id: u.nama for u in svc.daftar_unit()}
    auditor_map = {a.id: a.nama for a in svc.daftar_auditor()}
    return templates.TemplateResponse("audit/list.html", {
        "request": request,
        "audit_list": audit_list,
        "unit_map": unit_map,
        "auditor_map": auditor_map,
        "judul_halaman": "Program Audit",
    })


@router.get("/tambah", response_class=HTMLResponse)
async def form_tambah_audit(request: Request):
    return templates.TemplateResponse("audit/form.html", {
        "request": request,
        "unit_list": svc.daftar_unit(),
        "auditor_list": svc.daftar_auditor(),
        "audit": None,
        "judul_halaman": "Tambah Program Audit",
        "pesan_error": None,
    })


@router.post("/tambah")
async def simpan_tambah_audit(
    request: Request,
    nama: str = Form(...),
    periode_mulai: str = Form(...),
    periode_selesai: str = Form(...),
    unit_kerja_id: str = Form(...),
    auditor_id: str = Form(...),
    tujuan: str = Form(""),
    status: str = Form("Perencanaan"),
):
    try:
        svc.tambah_audit({
            "nama": nama,
            "periode_mulai": periode_mulai,
            "periode_selesai": periode_selesai,
            "unit_kerja_id": unit_kerja_id,
            "auditor_id": auditor_id,
            "tujuan": tujuan,
            "status": status,
        })
        return RedirectResponse("/audit", status_code=303)
    except DataTidakValidError as e:
        return templates.TemplateResponse("audit/form.html", {
            "request": request,
            "unit_list": svc.daftar_unit(),
            "auditor_list": svc.daftar_auditor(),
            "audit": None,
            "judul_halaman": "Tambah Program Audit",
            "pesan_error": str(e),
        })


@router.get("/{id}", response_class=HTMLResponse)
async def detail_audit(request: Request, id: str):
    audit = svc.detail_audit(id)
    if not audit:
        return RedirectResponse("/audit", status_code=303)
    unit = svc.detail_unit(audit.unit_kerja_id)
    auditor = svc.detail_auditor(audit.auditor_id)
    return templates.TemplateResponse("audit/detail.html", {
        "request": request,
        "audit": audit,
        "unit": unit,
        "auditor": auditor,
        "judul_halaman": "Detail Audit",
    })


@router.get("/{id}/edit", response_class=HTMLResponse)
async def form_edit_audit(request: Request, id: str):
    audit = svc.detail_audit(id)
    if not audit:
        return RedirectResponse("/audit", status_code=303)
    return templates.TemplateResponse("audit/form.html", {
        "request": request,
        "unit_list": svc.daftar_unit(),
        "auditor_list": svc.daftar_auditor(),
        "audit": audit,
        "judul_halaman": "Edit Program Audit",
        "pesan_error": None,
    })


@router.post("/{id}/edit")
async def simpan_edit_audit(
    request: Request,
    id: str,
    nama: str = Form(...),
    periode_mulai: str = Form(...),
    periode_selesai: str = Form(...),
    unit_kerja_id: str = Form(...),
    auditor_id: str = Form(...),
    tujuan: str = Form(""),
    status: str = Form("Perencanaan"),
):
    try:
        svc.perbarui_audit(id, {
            "nama": nama,
            "periode_mulai": periode_mulai,
            "periode_selesai": periode_selesai,
            "unit_kerja_id": unit_kerja_id,
            "auditor_id": auditor_id,
            "tujuan": tujuan,
            "status": status,
        })
        return RedirectResponse(f"/audit/{id}", status_code=303)
    except DataTidakValidError as e:
        audit = svc.detail_audit(id)
        return templates.TemplateResponse("audit/form.html", {
            "request": request,
            "unit_list": svc.daftar_unit(),
            "auditor_list": svc.daftar_auditor(),
            "audit": audit,
            "judul_halaman": "Edit Program Audit",
            "pesan_error": str(e),
        })


@router.post("/{id}/hapus")
async def hapus_audit(id: str):
    svc.hapus_audit(id)
    return RedirectResponse("/audit", status_code=303)


# --- Auditor ---

@router.get("/auditor/daftar", response_class=HTMLResponse)
async def daftar_auditor(request: Request):
    return templates.TemplateResponse("audit/auditor_list.html", {
        "request": request,
        "auditor_list": svc.daftar_auditor(),
        "judul_halaman": "Daftar Auditor",
    })


@router.get("/auditor/tambah", response_class=HTMLResponse)
async def form_tambah_auditor(request: Request):
    return templates.TemplateResponse("audit/auditor_form.html", {
        "request": request,
        "auditor": None,
        "judul_halaman": "Tambah Auditor",
        "pesan_error": None,
    })


@router.post("/auditor/tambah")
async def simpan_auditor(
    nama: str = Form(...),
    jabatan: str = Form(...),
    sertifikasi: str = Form(""),
):
    svc.tambah_auditor({"nama": nama, "jabatan": jabatan, "sertifikasi": sertifikasi})
    return RedirectResponse("/audit/auditor/daftar", status_code=303)


@router.post("/auditor/{id}/hapus")
async def hapus_auditor(id: str):
    svc.hapus_auditor(id)
    return RedirectResponse("/audit/auditor/daftar", status_code=303)


# --- Unit Kerja ---

@router.get("/unit/daftar", response_class=HTMLResponse)
async def daftar_unit(request: Request):
    return templates.TemplateResponse("audit/unit_list.html", {
        "request": request,
        "unit_list": svc.daftar_unit(),
        "judul_halaman": "Daftar Unit Kerja",
    })


@router.get("/unit/tambah", response_class=HTMLResponse)
async def form_tambah_unit(request: Request):
    return templates.TemplateResponse("audit/unit_form.html", {
        "request": request,
        "unit": None,
        "judul_halaman": "Tambah Unit Kerja",
        "pesan_error": None,
    })


@router.post("/unit/tambah")
async def simpan_unit(
    nama: str = Form(...),
    kode: str = Form(...),
    kepala_unit: str = Form(""),
):
    svc.tambah_unit({"nama": nama, "kode": kode, "kepala_unit": kepala_unit})
    return RedirectResponse("/audit/unit/daftar", status_code=303)


@router.post("/unit/{id}/hapus")
async def hapus_unit(id: str):
    svc.hapus_unit(id)
    return RedirectResponse("/audit/unit/daftar", status_code=303)
