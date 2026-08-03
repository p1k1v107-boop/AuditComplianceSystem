"""Router untuk halaman dashboard utama."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.services.audit_service import AuditService
from src.services.temuan_service import TemuanService
from src.services.tindak_lanjut_service import TindakLanjutService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

audit_svc = AuditService()
temuan_svc = TemuanService()
tl_svc = TindakLanjutService()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    stat_audit = audit_svc.statistik()
    stat_temuan = temuan_svc.statistik()
    stat_tl = tl_svc.statistik()

    temuan_terbuka = temuan_svc.temuan_terbuka()[:5]
    terlambat = tl_svc.cek_keterlambatan()[:5]

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stat_audit": stat_audit,
        "stat_temuan": stat_temuan,
        "stat_tl": stat_tl,
        "temuan_terbuka": temuan_terbuka,
        "terlambat": terlambat,
        "judul_halaman": "Dashboard",
    })
