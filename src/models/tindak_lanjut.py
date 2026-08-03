"""Model TindakLanjut dan Rekomendasi."""

from src.models.base import BaseEntity
from src.exceptions.custom import DataTidakValidError

STATUS_TL = ["Belum Mulai", "Dalam Proses", "Selesai", "Terlambat", "Dibatalkan"]
TIPE_TINDAKAN = ["Koreksi", "Pencegahan", "Penutupan", "Pembatalan"]


class Rekomendasi(BaseEntity):
    """Rekomendasi yang diberikan untuk suatu temuan."""

    def __init__(
        self,
        temuan_id: str,
        isi_rekomendasi: str,
        prioritas: int = 1,
        id: str = None,
    ):
        super().__init__(id)
        if not (1 <= prioritas <= 3):
            raise DataTidakValidError("prioritas", prioritas, "Harus antara 1 (tinggi) dan 3 (rendah)")
        self.temuan_id = temuan_id
        self.isi_rekomendasi = isi_rekomendasi
        self.prioritas = prioritas

    def label_prioritas(self) -> str:
        return {1: "Tinggi", 2: "Sedang", 3: "Rendah"}.get(self.prioritas, "Sedang")

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "temuan_id": self.temuan_id,
            "isi_rekomendasi": self.isi_rekomendasi,
            "prioritas": self.prioritas,
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        obj = super().from_dict(data)
        obj.temuan_id = data.get("temuan_id", "")
        obj.isi_rekomendasi = data.get("isi_rekomendasi", "")
        obj.prioritas = data.get("prioritas", 1)
        return obj


class TindakLanjut(BaseEntity):
    """Tindak lanjut atas temuan audit dengan riwayat perubahan."""

    def __init__(
        self,
        temuan_id: str,
        unit_kerja_id: str,
        tipe_tindakan: str,
        deskripsi: str,
        penanggung_jawab: str,
        batas_waktu: str,
        tanggal_pelaksanaan: str = "",
        status: str = "Belum Mulai",
        catatan: str = "",
        id: str = None,
    ):
        super().__init__(id)
        if tipe_tindakan not in TIPE_TINDAKAN:
            raise DataTidakValidError("tipe_tindakan", tipe_tindakan, f"Harus salah satu dari {TIPE_TINDAKAN}")
        if status not in STATUS_TL:
            raise DataTidakValidError("status", status, f"Harus salah satu dari {STATUS_TL}")
        self.temuan_id = temuan_id
        self.unit_kerja_id = unit_kerja_id
        self.tipe_tindakan = tipe_tindakan
        self.deskripsi = deskripsi
        self.penanggung_jawab = penanggung_jawab
        self.batas_waktu = batas_waktu
        self.tanggal_pelaksanaan = tanggal_pelaksanaan
        self._status = status
        self.catatan = catatan
        self._riwayat: list = []

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, nilai: str):
        if nilai not in STATUS_TL:
            raise DataTidakValidError("status", nilai, f"Harus salah satu dari {STATUS_TL}")
        self._riwayat.append({
            "dari": self._status,
            "ke": nilai,
            "waktu": self._updated_at,
        })
        self._status = nilai
        self._touch()

    @property
    def riwayat(self) -> list:
        return list(self._riwayat)

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "temuan_id": self.temuan_id,
            "unit_kerja_id": self.unit_kerja_id,
            "tipe_tindakan": self.tipe_tindakan,
            "deskripsi": self.deskripsi,
            "penanggung_jawab": self.penanggung_jawab,
            "batas_waktu": self.batas_waktu,
            "tanggal_pelaksanaan": self.tanggal_pelaksanaan,
            "status": self._status,
            "catatan": self.catatan,
            "riwayat": self._riwayat,
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        obj = super().from_dict(data)
        obj.temuan_id = data.get("temuan_id", "")
        obj.unit_kerja_id = data.get("unit_kerja_id", "")
        obj.tipe_tindakan = data.get("tipe_tindakan", "Koreksi")
        obj.deskripsi = data.get("deskripsi", "")
        obj.penanggung_jawab = data.get("penanggung_jawab", "")
        obj.batas_waktu = data.get("batas_waktu", "")
        obj.tanggal_pelaksanaan = data.get("tanggal_pelaksanaan", "")
        obj._status = data.get("status", "Belum Mulai")
        obj.catatan = data.get("catatan", "")
        obj._riwayat = data.get("riwayat", [])
        return obj
