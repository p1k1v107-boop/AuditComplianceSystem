"""Model untuk ProgramAudit, Auditor, dan UnitKerja."""

from src.models.base import BaseEntity
from src.exceptions.custom import DataTidakValidError

STATUS_AUDIT = ["Perencanaan", "Pelaksanaan", "Pelaporan", "Selesai", "Dibatalkan"]


class Auditor(BaseEntity):
    """Representasi auditor yang melaksanakan audit."""

    def __init__(self, nama: str, jabatan: str, sertifikasi: str, id: str = None):
        super().__init__(id)
        self.nama = nama
        self.jabatan = jabatan
        self.sertifikasi = sertifikasi

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "nama": self.nama,
            "jabatan": self.jabatan,
            "sertifikasi": self.sertifikasi,
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        obj = super().from_dict(data)
        obj.nama = data.get("nama", "")
        obj.jabatan = data.get("jabatan", "")
        obj.sertifikasi = data.get("sertifikasi", "")
        return obj


class UnitKerja(BaseEntity):
    """Unit kerja yang menjadi objek audit."""

    def __init__(self, nama: str, kode: str, kepala_unit: str, id: str = None):
        super().__init__(id)
        self.nama = nama
        self.kode = kode
        self.kepala_unit = kepala_unit

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "nama": self.nama,
            "kode": self.kode,
            "kepala_unit": self.kepala_unit,
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        obj = super().from_dict(data)
        obj.nama = data.get("nama", "")
        obj.kode = data.get("kode", "")
        obj.kepala_unit = data.get("kepala_unit", "")
        return obj


class ProgramAudit(BaseEntity):
    """Program audit dengan informasi periode, status, dan penugasan."""

    def __init__(
        self,
        nama: str,
        periode_mulai: str,
        periode_selesai: str,
        unit_kerja_id: str,
        auditor_id: str,
        tujuan: str = "",
        status: str = "Perencanaan",
        id: str = None,
    ):
        super().__init__(id)
        if status not in STATUS_AUDIT:
            raise DataTidakValidError("status", status, f"Harus salah satu dari {STATUS_AUDIT}")
        self.nama = nama
        self.periode_mulai = periode_mulai
        self.periode_selesai = periode_selesai
        self.unit_kerja_id = unit_kerja_id
        self.auditor_id = auditor_id
        self.tujuan = tujuan
        self._status = status

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, nilai: str):
        if nilai not in STATUS_AUDIT:
            raise DataTidakValidError("status", nilai, f"Harus salah satu dari {STATUS_AUDIT}")
        self._status = nilai
        self._touch()

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "nama": self.nama,
            "periode_mulai": self.periode_mulai,
            "periode_selesai": self.periode_selesai,
            "unit_kerja_id": self.unit_kerja_id,
            "auditor_id": self.auditor_id,
            "tujuan": self.tujuan,
            "status": self._status,
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        obj = super().from_dict(data)
        obj.nama = data.get("nama", "")
        obj.periode_mulai = data.get("periode_mulai", "")
        obj.periode_selesai = data.get("periode_selesai", "")
        obj.unit_kerja_id = data.get("unit_kerja_id", "")
        obj.auditor_id = data.get("auditor_id", "")
        obj.tujuan = data.get("tujuan", "")
        obj._status = data.get("status", "Perencanaan")
        return obj
