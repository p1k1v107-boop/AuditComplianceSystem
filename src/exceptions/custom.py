"""Custom exceptions untuk domain audit kepatuhan."""


class AuditBaseError(Exception):
    """Base exception untuk semua custom error domain."""
    def __init__(self, message: str, kode: str = None):
        super().__init__(message)
        self.message = message
        self.kode = kode or "AUDIT_ERROR"

    def __str__(self):
        return f"[{self.kode}] {self.message}"


class BuktiAuditTidakCukupError(AuditBaseError):
    """Dipicu saat menutup temuan tapi bukti pendukung tidak memenuhi syarat."""
    def __init__(self, temuan_id: str, jumlah_bukti: int, minimum: int):
        pesan = (
            f"Temuan '{temuan_id}' tidak dapat ditutup: "
            f"bukti {jumlah_bukti}/{minimum} (minimum {minimum} bukti diperlukan)"
        )
        super().__init__(pesan, "BUKTI_TIDAK_CUKUP")
        self.temuan_id = temuan_id
        self.jumlah_bukti = jumlah_bukti
        self.minimum = minimum


class TindakLanjutTerlambatError(AuditBaseError):
    """Dipicu saat batas waktu tindak lanjut sudah terlewati."""
    def __init__(self, tindak_lanjut_id: str, batas_waktu: str, tanggal_sekarang: str):
        pesan = (
            f"Tindak lanjut '{tindak_lanjut_id}' terlambat: "
            f"batas waktu {batas_waktu}, sekarang {tanggal_sekarang}"
        )
        super().__init__(pesan, "TINDAK_LANJUT_TERLAMBAT")
        self.tindak_lanjut_id = tindak_lanjut_id
        self.batas_waktu = batas_waktu
        self.tanggal_sekarang = tanggal_sekarang


class DataTidakValidError(AuditBaseError):
    """Dipicu saat input data gagal validasi."""
    def __init__(self, field: str, nilai, alasan: str):
        pesan = f"Data tidak valid pada field '{field}' (nilai: {nilai!r}): {alasan}"
        super().__init__(pesan, "DATA_TIDAK_VALID")
        self.field = field
        self.nilai = nilai
        self.alasan = alasan


class FileTidakDitemukanError(AuditBaseError):
    """Dipicu saat file data tidak ditemukan."""
    def __init__(self, path: str):
        super().__init__(f"File tidak ditemukan: {path}", "FILE_TIDAK_DITEMUKAN")
        self.path = path


class GagalSimpanError(AuditBaseError):
    """Dipicu saat operasi simpan ke file gagal."""
    def __init__(self, path: str, detail: str):
        super().__init__(f"Gagal menyimpan ke '{path}': {detail}", "GAGAL_SIMPAN")
        self.path = path
        self.detail = detail


class StatusTransisiTidakValidError(AuditBaseError):
    """Dipicu saat transisi status tidak diizinkan."""
    def __init__(self, status_lama: str, status_baru: str):
        pesan = f"Transisi status '{status_lama}' -> '{status_baru}' tidak diizinkan"
        super().__init__(pesan, "STATUS_TIDAK_VALID")
        self.status_lama = status_lama
        self.status_baru = status_baru
