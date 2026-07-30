"""Service untuk operasi program audit, auditor, dan unit kerja."""

from src.models.audit import ProgramAudit, Auditor, UnitKerja
from src.repositories.json_repository import JsonRepository
from src.exceptions.custom import DataTidakValidError

DATA_DIR = "data"


class AuditService:
    """Logika bisnis untuk pengelolaan program audit, auditor, dan unit kerja."""

    def __init__(self):
        self._repo_audit = JsonRepository(f"{DATA_DIR}/audit.json")
        self._repo_auditor = JsonRepository(f"{DATA_DIR}/auditor.json")
        self._repo_unit = JsonRepository(f"{DATA_DIR}/unit_kerja.json")

    # --- Program Audit ---

    def daftar_audit(self) -> list[ProgramAudit]:
        return [ProgramAudit.from_dict(d) for d in self._repo_audit.baca_semua()]

    def detail_audit(self, id: str) -> ProgramAudit | None:
        data = self._repo_audit.cari_id(id)
        return ProgramAudit.from_dict(data) if data else None

    def tambah_audit(self, data: dict) -> ProgramAudit:
        audit = ProgramAudit(
            nama=data["nama"],
            periode_mulai=data["periode_mulai"],
            periode_selesai=data["periode_selesai"],
            unit_kerja_id=data["unit_kerja_id"],
            auditor_id=data["auditor_id"],
            tujuan=data.get("tujuan", ""),
            status=data.get("status", "Perencanaan"),
        )
        self._repo_audit.simpan(audit.to_dict())
        return audit

    def perbarui_audit(self, id: str, data: dict) -> ProgramAudit | None:
        audit = self.detail_audit(id)
        if not audit:
            return None
        audit.nama = data.get("nama", audit.nama)
        audit.periode_mulai = data.get("periode_mulai", audit.periode_mulai)
        audit.periode_selesai = data.get("periode_selesai", audit.periode_selesai)
        audit.unit_kerja_id = data.get("unit_kerja_id", audit.unit_kerja_id)
        audit.auditor_id = data.get("auditor_id", audit.auditor_id)
        audit.tujuan = data.get("tujuan", audit.tujuan)
        if "status" in data:
            audit.status = data["status"]
        self._repo_audit.perbarui(id, audit.to_dict())
        return audit

    def hapus_audit(self, id: str) -> bool:
        return self._repo_audit.hapus(id)

    # --- Auditor ---

    def daftar_auditor(self) -> list[Auditor]:
        return [Auditor.from_dict(d) for d in self._repo_auditor.baca_semua()]

    def detail_auditor(self, id: str) -> Auditor | None:
        data = self._repo_auditor.cari_id(id)
        return Auditor.from_dict(data) if data else None

    def tambah_auditor(self, data: dict) -> Auditor:
        auditor = Auditor(
            nama=data["nama"],
            jabatan=data["jabatan"],
            sertifikasi=data.get("sertifikasi", "-"),
        )
        self._repo_auditor.simpan(auditor.to_dict())
        return auditor

    def perbarui_auditor(self, id: str, data: dict) -> Auditor | None:
        auditor = self.detail_auditor(id)
        if not auditor:
            return None
        auditor.nama = data.get("nama", auditor.nama)
        auditor.jabatan = data.get("jabatan", auditor.jabatan)
        auditor.sertifikasi = data.get("sertifikasi", auditor.sertifikasi)
        self._repo_auditor.perbarui(id, auditor.to_dict())
        return auditor

    def hapus_auditor(self, id: str) -> bool:
        return self._repo_auditor.hapus(id)

    # --- Unit Kerja ---

    def daftar_unit(self) -> list[UnitKerja]:
        return [UnitKerja.from_dict(d) for d in self._repo_unit.baca_semua()]

    def detail_unit(self, id: str) -> UnitKerja | None:
        data = self._repo_unit.cari_id(id)
        return UnitKerja.from_dict(data) if data else None

    def tambah_unit(self, data: dict) -> UnitKerja:
        unit = UnitKerja(
            nama=data["nama"],
            kode=data["kode"],
            kepala_unit=data.get("kepala_unit", "-"),
        )
        self._repo_unit.simpan(unit.to_dict())
        return unit

    def perbarui_unit(self, id: str, data: dict) -> UnitKerja | None:
        unit = self.detail_unit(id)
        if not unit:
            return None
        unit.nama = data.get("nama", unit.nama)
        unit.kode = data.get("kode", unit.kode)
        unit.kepala_unit = data.get("kepala_unit", unit.kepala_unit)
        self._repo_unit.perbarui(id, unit.to_dict())
        return unit

    def hapus_unit(self, id: str) -> bool:
        return self._repo_unit.hapus(id)

    def statistik(self) -> dict:
        """Ringkasan statistik untuk dashboard."""
        return {
            "total_audit": self._repo_audit.jumlah(),
            "total_auditor": self._repo_auditor.jumlah(),
            "total_unit": self._repo_unit.jumlah(),
        }
