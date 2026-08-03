"""Service untuk operasi tindak lanjut dan rekomendasi."""

from datetime import date
from pathlib import Path
from src.models.tindak_lanjut import TindakLanjut, Rekomendasi
from src.repositories.csv_repository import CsvRepository
from src.repositories.json_repository import JsonRepository
from src.exceptions.custom import TindakLanjutTerlambatError, DataTidakValidError
from src.core.paths import DATA_DIR

TL_FIELDNAMES = [
    "id", "temuan_id", "unit_kerja_id", "tipe_tindakan", "deskripsi",
    "penanggung_jawab", "batas_waktu", "tanggal_pelaksanaan",
    "status", "catatan", "riwayat", "created_at", "updated_at",
]


class TindakLanjutService:
    """Logika bisnis untuk pengelolaan tindak lanjut dan rekomendasi."""

    def __init__(self):
        self._repo_tl = CsvRepository(str(Path(DATA_DIR) / "tindak_lanjut.csv"), TL_FIELDNAMES)
        self._repo_rek = JsonRepository(str(Path(DATA_DIR) / "rekomendasi.json"))

    def _pastikan_temuan_ada(self, temuan_id: str):
        from src.services.temuan_service import TemuanService

        if not TemuanService().detail_temuan(temuan_id):
            raise DataTidakValidError("temuan_id", temuan_id, "Temuan tidak ditemukan")

    def _pastikan_unit_ada(self, unit_kerja_id: str):
        from src.services.audit_service import AuditService

        if not AuditService().detail_unit(unit_kerja_id):
            raise DataTidakValidError("unit_kerja_id", unit_kerja_id, "Unit kerja tidak ditemukan")

    # --- Tindak Lanjut ---

    def _parse_tl(self, row: dict) -> TindakLanjut:
        """Konversi baris CSV ke objek TindakLanjut."""
        import ast
        row = dict(row)
        try:
            row["riwayat"] = ast.literal_eval(row.get("riwayat", "[]"))
        except Exception:
            row["riwayat"] = []
        return TindakLanjut.from_dict(row)

    def daftar_tindak_lanjut(self) -> list[TindakLanjut]:
        return [self._parse_tl(r) for r in self._repo_tl.baca_semua()]

    def detail_tindak_lanjut(self, id: str) -> TindakLanjut | None:
        row = self._repo_tl.cari_id(id)
        return self._parse_tl(row) if row else None

    def tambah_tindak_lanjut(self, data: dict) -> TindakLanjut:
        self._pastikan_temuan_ada(data["temuan_id"])
        self._pastikan_unit_ada(data["unit_kerja_id"])
        tl = TindakLanjut(
            temuan_id=data["temuan_id"],
            unit_kerja_id=data["unit_kerja_id"],
            tipe_tindakan=data["tipe_tindakan"],
            deskripsi=data["deskripsi"],
            penanggung_jawab=data["penanggung_jawab"],
            batas_waktu=data["batas_waktu"],
            tanggal_pelaksanaan=data.get("tanggal_pelaksanaan", ""),
            catatan=data.get("catatan", ""),
        )
        row = tl.to_dict()
        row["riwayat"] = str(row["riwayat"])
        self._repo_tl.simpan(row)
        return tl

    def perbarui_status(self, id: str, status_baru: str, catatan: str = "") -> TindakLanjut:
        """Ubah status tindak lanjut dengan pengecekan keterlambatan."""
        tl = self.detail_tindak_lanjut(id)
        if not tl:
            raise DataTidakValidError("id", id, "Tindak lanjut tidak ditemukan")

        hari_ini = date.today().isoformat()
        if tl.batas_waktu and hari_ini > tl.batas_waktu and status_baru != "Terlambat":
            raise TindakLanjutTerlambatError(id, tl.batas_waktu, hari_ini)

        tl.status = status_baru
        if catatan:
            tl.catatan = catatan
        row = tl.to_dict()
        row["riwayat"] = str(row["riwayat"])
        self._repo_tl.perbarui(id, row)
        return tl

    def hapus_tindak_lanjut(self, id: str) -> bool:
        return self._repo_tl.hapus(id)

    def hapus_berdasarkan_temuan(self, temuan_id: str) -> int:
        return self._repo_tl.hapus_filter_by("temuan_id", temuan_id)

    def cek_keterlambatan(self) -> list[TindakLanjut]:
        """Kembalikan daftar tindak lanjut yang telah melewati batas waktu."""
        hari_ini = date.today().isoformat()
        hasil = []
        for tl in self.daftar_tindak_lanjut():
            if (
                tl.batas_waktu
                and hari_ini > tl.batas_waktu
                and tl.status not in ["Selesai", "Dibatalkan", "Terlambat"]
            ):
                hasil.append(tl)
        return hasil

    def tindak_lanjut_per_temuan(self, temuan_id: str) -> list[TindakLanjut]:
        rows = self._repo_tl.filter_by("temuan_id", temuan_id)
        return [self._parse_tl(r) for r in rows]

    # --- Rekomendasi ---

    def daftar_rekomendasi(self, temuan_id: str = None) -> list[Rekomendasi]:
        if temuan_id:
            data = self._repo_rek.filter_by("temuan_id", temuan_id)
        else:
            data = self._repo_rek.baca_semua()
        return [Rekomendasi.from_dict(d) for d in data]

    def tambah_rekomendasi(self, data: dict) -> Rekomendasi:
        rek = Rekomendasi(
            temuan_id=data["temuan_id"],
            isi_rekomendasi=data["isi_rekomendasi"],
            prioritas=int(data.get("prioritas", 1)),
        )
        self._repo_rek.simpan(rek.to_dict())
        return rek

    def hapus_rekomendasi(self, id: str) -> bool:
        return self._repo_rek.hapus(id)

    def statistik(self) -> dict:
        semua = self.daftar_tindak_lanjut()
        terlambat = self.cek_keterlambatan()
        return {
            "total_tindak_lanjut": len(semua),
            "selesai": len([t for t in semua if t.status == "Selesai"]),
            "dalam_proses": len([t for t in semua if t.status == "Dalam Proses"]),
            "terlambat": len(terlambat),
        }
