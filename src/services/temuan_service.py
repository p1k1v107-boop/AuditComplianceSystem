"""Service untuk operasi temuan dan bukti audit."""

from pathlib import Path

from src.models.temuan import TemuanAudit, temuan_from_dict, buat_temuan
from src.models.bukti import BuktiAudit
from src.repositories.json_repository import JsonRepository
from src.exceptions.custom import BuktiAuditTidakCukupError, DataTidakValidError
from src.core.paths import DATA_DIR, UPLOADS_DIR


class TemuanService:
    """Logika bisnis untuk pengelolaan temuan dan bukti audit."""

    def __init__(self):
        self._repo_temuan = JsonRepository(str(Path(DATA_DIR) / "temuan.json"))
        self._repo_bukti = JsonRepository(str(Path(DATA_DIR) / "bukti.json"))

    def _pastikan_program_audit_ada(self, program_audit_id: str):
        from src.services.audit_service import AuditService

        if not AuditService().detail_audit(program_audit_id):
            raise DataTidakValidError("program_audit_id", program_audit_id, "Program audit tidak ditemukan")

    def _pastikan_unit_ada(self, unit_kerja_id: str):
        from src.services.audit_service import AuditService

        if not AuditService().detail_unit(unit_kerja_id):
            raise DataTidakValidError("unit_kerja_id", unit_kerja_id, "Unit kerja tidak ditemukan")

    def _hapus_file_bukti(self, lokasi_file: str):
        if not lokasi_file:
            return
        nama_file = Path(lokasi_file).name
        kandidat = (UPLOADS_DIR / nama_file).resolve()
        if UPLOADS_DIR.resolve() in kandidat.parents and kandidat.exists():
            kandidat.unlink()

    def _hapus_bukti_terkait(self, temuan_id: str):
        bukti_terkait = self._repo_bukti.filter_by("temuan_id", temuan_id)
        for bukti in bukti_terkait:
            self._hapus_file_bukti(bukti.get("lokasi_file", ""))
        self._repo_bukti.hapus_filter_by("temuan_id", temuan_id)

    # --- Temuan ---

    def daftar_temuan(self) -> list[TemuanAudit]:
        return [temuan_from_dict(d) for d in self._repo_temuan.baca_semua()]

    def detail_temuan(self, id: str) -> TemuanAudit | None:
        data = self._repo_temuan.cari_id(id)
        return temuan_from_dict(data) if data else None

    def tambah_temuan(self, data: dict) -> TemuanAudit:
        jenis = data.get("jenis", "Minor")
        self._pastikan_program_audit_ada(data["program_audit_id"])
        self._pastikan_unit_ada(data["unit_kerja_id"])
        temuan = buat_temuan(
            jenis=jenis,
            program_audit_id=data["program_audit_id"],
            unit_kerja_id=data["unit_kerja_id"],
            judul=data["judul"],
            deskripsi=data["deskripsi"],
            dampak=int(data["dampak"]),
            kemungkinan=int(data["kemungkinan"]),
            tingkat_kepatuhan=float(data["tingkat_kepatuhan"]),
            rekomendasi=data.get("rekomendasi", ""),
            batas_tindak_lanjut=data.get("batas_tindak_lanjut", ""),
        )
        self._repo_temuan.simpan(temuan.to_dict())
        return temuan

    def perbarui_temuan(self, id: str, data: dict) -> TemuanAudit | None:
        temuan = self.detail_temuan(id)
        if not temuan:
            return None
        temuan.judul = data.get("judul", temuan.judul)
        temuan.deskripsi = data.get("deskripsi", temuan.deskripsi)
        temuan.dampak = int(data.get("dampak", temuan.dampak))
        temuan.kemungkinan = int(data.get("kemungkinan", temuan.kemungkinan))
        temuan.tingkat_kepatuhan = float(data.get("tingkat_kepatuhan", temuan.tingkat_kepatuhan))
        temuan.rekomendasi = data.get("rekomendasi", temuan.rekomendasi)
        temuan.batas_tindak_lanjut = data.get("batas_tindak_lanjut", temuan.batas_tindak_lanjut)
        self._repo_temuan.perbarui(id, temuan.to_dict())
        return temuan

    def hapus_temuan(self, id: str) -> bool:
        if not self.detail_temuan(id):
            return False

        self._hapus_bukti_terkait(id)
        from src.services.tindak_lanjut_service import TindakLanjutService

        TindakLanjutService().hapus_berdasarkan_temuan(id)
        return self._repo_temuan.hapus(id)

    def tutup_temuan(self, id: str) -> TemuanAudit:
        """Tutup temuan dengan validasi jumlah bukti pendukung."""
        temuan = self.detail_temuan(id)
        if not temuan:
            raise DataTidakValidError("id", id, "Temuan tidak ditemukan")

        bukti_list = self._repo_bukti.filter_by("temuan_id", id)
        jumlah_bukti = len(bukti_list)
        minimum = temuan.minimum_bukti()

        if jumlah_bukti < minimum:
            raise BuktiAuditTidakCukupError(id, jumlah_bukti, minimum)

        if temuan.status_tindak_lanjut == "Terbuka":
            temuan.status_tindak_lanjut = "Dalam Proses"
        if temuan.status_tindak_lanjut == "Dalam Proses":
            temuan.status_tindak_lanjut = "Selesai"
        if temuan.status_tindak_lanjut != "Ditutup":
            temuan.status_tindak_lanjut = "Ditutup"
        self._repo_temuan.perbarui(id, temuan.to_dict())
        return temuan

    def ubah_status(self, id: str, status_baru: str) -> TemuanAudit:
        """Ubah status temuan dengan validasi transisi."""
        temuan = self.detail_temuan(id)
        if not temuan:
            raise DataTidakValidError("id", id, "Temuan tidak ditemukan")
        temuan.status_tindak_lanjut = status_baru
        self._repo_temuan.perbarui(id, temuan.to_dict())
        return temuan

    def temuan_per_audit(self, program_audit_id: str) -> list[TemuanAudit]:
        data = self._repo_temuan.filter_by("program_audit_id", program_audit_id)
        return [temuan_from_dict(d) for d in data]

    def temuan_terbuka(self) -> list[TemuanAudit]:
        data = self._repo_temuan.filter_by("status_tindak_lanjut", "Terbuka")
        return [temuan_from_dict(d) for d in data]

    # --- Bukti ---

    def daftar_bukti(self, temuan_id: str) -> list[BuktiAudit]:
        data = self._repo_bukti.filter_by("temuan_id", temuan_id)
        return [BuktiAudit.from_dict(d) for d in data]

    def tambah_bukti(self, data: dict) -> BuktiAudit:
        if not self.detail_temuan(data["temuan_id"]):
            raise DataTidakValidError("temuan_id", data["temuan_id"], "Temuan tidak ditemukan")
        bukti = BuktiAudit(
            temuan_id=data["temuan_id"],
            judul=data["judul"],
            tipe=data["tipe"],
            deskripsi=data.get("deskripsi", ""),
            lokasi_file=data.get("lokasi_file", ""),
        )
        self._repo_bukti.simpan(bukti.to_dict())
        return bukti

    def hapus_bukti(self, id: str) -> bool:
        data = self._repo_bukti.cari_id(id)
        if not data:
            return False
        self._hapus_file_bukti(data.get("lokasi_file", ""))
        return self._repo_bukti.hapus(id)

    def statistik(self) -> dict:
        semua = self.daftar_temuan()
        return {
            "total_temuan": len(semua),
            "terbuka": len([t for t in semua if t.status_tindak_lanjut == "Terbuka"]),
            "dalam_proses": len([t for t in semua if t.status_tindak_lanjut == "Dalam Proses"]),
            "ditutup": len([t for t in semua if t.status_tindak_lanjut == "Ditutup"]),
            "minor": len([t for t in semua if t.JENIS == "Minor"]),
            "mayor": len([t for t in semua if t.JENIS == "Mayor"]),
            "kritis": len([t for t in semua if t.JENIS == "Kritis"]),
        }
