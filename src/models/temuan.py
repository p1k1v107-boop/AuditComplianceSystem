"""Hierarki kelas TemuanAudit: superclass dan tiga subclass dengan polymorphism."""

from src.models.base import BaseEntity
from src.exceptions.custom import DataTidakValidError, StatusTransisiTidakValidError

STATUS_TEMUAN = ["Terbuka", "Dalam Proses", "Selesai", "Ditutup", "Dibatalkan"]

# Transisi status yang diizinkan
TRANSISI_VALID = {
    "Terbuka": ["Dalam Proses", "Dibatalkan"],
    "Dalam Proses": ["Selesai", "Terbuka", "Dibatalkan"],
    "Selesai": ["Ditutup", "Dalam Proses"],
    "Ditutup": [],
    "Dibatalkan": [],
}

MINIMUM_BUKTI = {"Minor": 1, "Mayor": 2, "Kritis": 3}


class TemuanAudit(BaseEntity):
    """Superclass untuk semua jenis temuan audit.
    Subclass wajib override hitung_skor_risiko().
    """

    JENIS = "Umum"
    BOBOT_RISIKO = 1.0

    def __init__(
        self,
        program_audit_id: str,
        unit_kerja_id: str,
        judul: str,
        deskripsi: str,
        dampak: int,
        kemungkinan: int,
        tingkat_kepatuhan: float,
        rekomendasi: str = "",
        batas_tindak_lanjut: str = "",
        status: str = "Terbuka",
        id: str = None,
    ):
        super().__init__(id)
        self._validasi_skala(dampak, "dampak", 1, 5)
        self._validasi_skala(kemungkinan, "kemungkinan", 1, 5)
        self._validasi_skala(tingkat_kepatuhan, "tingkat_kepatuhan", 0, 100)

        self.program_audit_id = program_audit_id
        self.unit_kerja_id = unit_kerja_id
        self.judul = judul
        self.deskripsi = deskripsi
        self.dampak = dampak
        self.kemungkinan = kemungkinan
        self.tingkat_kepatuhan = tingkat_kepatuhan
        self.rekomendasi = rekomendasi
        self.batas_tindak_lanjut = batas_tindak_lanjut

        # atribut privat: status tindak lanjut dengan enkapsulasi penuh
        self.__status_tindak_lanjut = status

    def _validasi_skala(self, nilai, field: str, minimum, maksimum):
        """Validasi nilai numerik dalam rentang yang ditentukan."""
        try:
            nilai = float(nilai)
        except (TypeError, ValueError):
            raise DataTidakValidError(field, nilai, "Harus berupa angka")
        if not (minimum <= nilai <= maksimum):
            raise DataTidakValidError(
                field, nilai, f"Harus antara {minimum} dan {maksimum}"
            )

    @property
    def status_tindak_lanjut(self) -> str:
        """Akses status tindak lanjut (read via property)."""
        return self.__status_tindak_lanjut

    @status_tindak_lanjut.setter
    def status_tindak_lanjut(self, nilai: str):
        """Set status dengan validasi transisi."""
        if nilai not in STATUS_TEMUAN:
            raise DataTidakValidError("status", nilai, f"Harus salah satu dari {STATUS_TEMUAN}")
        status_sekarang = self.__status_tindak_lanjut
        if nilai not in TRANSISI_VALID.get(status_sekarang, []):
            raise StatusTransisiTidakValidError(status_sekarang, nilai)
        self.__status_tindak_lanjut = nilai
        self._touch()

    def minimum_bukti(self) -> int:
        """Jumlah minimum bukti yang dibutuhkan untuk menutup temuan."""
        return MINIMUM_BUKTI.get(self.JENIS, 1)

    def hitung_skor_risiko(self) -> float:
        """Hitung skor risiko dasar. Subclass harus override method ini."""
        kepatuhan_faktor = (100 - self.tingkat_kepatuhan) / 100
        return round(self.dampak * self.kemungkinan * kepatuhan_faktor * self.BOBOT_RISIKO, 2)

    def label_risiko(self) -> str:
        """Label risiko berdasarkan skor."""
        skor = self.hitung_skor_risiko()
        if skor >= 15:
            return "Sangat Tinggi"
        elif skor >= 10:
            return "Tinggi"
        elif skor >= 5:
            return "Sedang"
        else:
            return "Rendah"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "jenis": self.JENIS,
            "program_audit_id": self.program_audit_id,
            "unit_kerja_id": self.unit_kerja_id,
            "judul": self.judul,
            "deskripsi": self.deskripsi,
            "dampak": self.dampak,
            "kemungkinan": self.kemungkinan,
            "tingkat_kepatuhan": self.tingkat_kepatuhan,
            "rekomendasi": self.rekomendasi,
            "batas_tindak_lanjut": self.batas_tindak_lanjut,
            "status_tindak_lanjut": self.__status_tindak_lanjut,
            "skor_risiko": self.hitung_skor_risiko(),
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        obj = super().from_dict(data)
        obj.program_audit_id = data.get("program_audit_id", "")
        obj.unit_kerja_id = data.get("unit_kerja_id", "")
        obj.judul = data.get("judul", "")
        obj.deskripsi = data.get("deskripsi", "")
        obj.dampak = data.get("dampak", 1)
        obj.kemungkinan = data.get("kemungkinan", 1)
        obj.tingkat_kepatuhan = data.get("tingkat_kepatuhan", 100)
        obj.rekomendasi = data.get("rekomendasi", "")
        obj.batas_tindak_lanjut = data.get("batas_tindak_lanjut", "")
        # restore private attr via name mangling
        obj._TemuanAudit__status_tindak_lanjut = data.get("status_tindak_lanjut", "Terbuka")
        return obj


class TemuanMinor(TemuanAudit):
    """Temuan dengan dampak rendah. Bobot risiko 0.5."""

    JENIS = "Minor"
    BOBOT_RISIKO = 0.5

    def hitung_skor_risiko(self) -> float:
        """Override: skor risiko minor dengan bobot 0.5 dan penalty kepatuhan ringan."""
        kepatuhan_faktor = (100 - self.tingkat_kepatuhan) / 100
        skor = self.dampak * self.kemungkinan * kepatuhan_faktor * self.BOBOT_RISIKO
        return round(max(skor, 0.1), 2)


class TemuanMayor(TemuanAudit):
    """Temuan dengan dampak menengah. Bobot risiko 1.0."""

    JENIS = "Mayor"
    BOBOT_RISIKO = 1.0

    def hitung_skor_risiko(self) -> float:
        """Override: skor risiko mayor dengan penambahan faktor dampak kuadratik."""
        kepatuhan_faktor = (100 - self.tingkat_kepatuhan) / 100
        skor = (self.dampak ** 1.2) * self.kemungkinan * kepatuhan_faktor * self.BOBOT_RISIKO
        return round(max(skor, 0.5), 2)


class TemuanKritis(TemuanAudit):
    """Temuan dengan dampak tinggi dan penalti kepatuhan maksimum. Bobot risiko 2.0."""

    JENIS = "Kritis"
    BOBOT_RISIKO = 2.0

    def hitung_skor_risiko(self) -> float:
        """Override: skor risiko kritis dengan bobot 2x dan penalti kepatuhan kuadratik."""
        kepatuhan_faktor = ((100 - self.tingkat_kepatuhan) / 100) ** 0.8
        skor = self.dampak * self.kemungkinan * kepatuhan_faktor * self.BOBOT_RISIKO
        return round(max(skor, 1.0), 2)


# Factory untuk membuat temuan berdasarkan jenis
PETA_KELAS_TEMUAN = {
    "Minor": TemuanMinor,
    "Mayor": TemuanMayor,
    "Kritis": TemuanKritis,
}


def buat_temuan(jenis: str, **kwargs) -> TemuanAudit:
    """Factory function: buat instance temuan sesuai jenis."""
    kelas = PETA_KELAS_TEMUAN.get(jenis)
    if not kelas:
        raise DataTidakValidError("jenis", jenis, f"Harus salah satu dari {list(PETA_KELAS_TEMUAN)}")
    return kelas(**kwargs)


def temuan_from_dict(data: dict) -> TemuanAudit:
    """Buat instance temuan dari dict berdasarkan field 'jenis'."""
    jenis = data.get("jenis", "Minor")
    kelas = PETA_KELAS_TEMUAN.get(jenis, TemuanMinor)
    return kelas.from_dict(data)
