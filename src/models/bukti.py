"""Model BuktiAudit dengan encapsulation pada __bukti_pendukung."""

from src.models.base import BaseEntity
from src.exceptions.custom import DataTidakValidError

TIPE_BUKTI = ["Dokumen", "Foto", "Wawancara", "Observasi", "Data Elektronik"]


class BuktiAudit(BaseEntity):
    """Bukti pendukung temuan audit dengan enkapsulasi pada daftar bukti."""

    def __init__(
        self,
        temuan_id: str,
        judul: str,
        tipe: str,
        deskripsi: str,
        lokasi_file: str = "",
        id: str = None,
    ):
        super().__init__(id)
        if tipe not in TIPE_BUKTI:
            raise DataTidakValidError("tipe", tipe, f"Harus salah satu dari {TIPE_BUKTI}")
        if not judul or not judul.strip():
            raise DataTidakValidError("judul", judul, "Judul bukti tidak boleh kosong")
        self.temuan_id = temuan_id
        self.judul = judul.strip()
        self.tipe = tipe
        self.deskripsi = deskripsi
        # atribut privat untuk daftar referensi bukti tambahan
        self.__bukti_pendukung: list = []
        self.lokasi_file = lokasi_file

    @property
    def bukti_pendukung(self) -> list:
        """Akses read-only ke daftar referensi bukti pendukung."""
        return list(self.__bukti_pendukung)

    def tambah_referensi(self, referensi: str):
        """Tambah referensi bukti pendukung dengan validasi."""
        if not referensi or not referensi.strip():
            raise DataTidakValidError("referensi", referensi, "Referensi tidak boleh kosong")
        self.__bukti_pendukung.append(referensi.strip())
        self._touch()

    def hapus_referensi(self, referensi: str):
        """Hapus referensi bukti pendukung."""
        if referensi in self.__bukti_pendukung:
            self.__bukti_pendukung.remove(referensi)
            self._touch()

    def jumlah_referensi(self) -> int:
        return len(self.__bukti_pendukung)

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "temuan_id": self.temuan_id,
            "judul": self.judul,
            "tipe": self.tipe,
            "deskripsi": self.deskripsi,
            "lokasi_file": self.lokasi_file,
            "bukti_pendukung": list(self.__bukti_pendukung),
        })
        return data

    @classmethod
    def from_dict(cls, data: dict):
        obj = super().from_dict(data)
        obj.temuan_id = data.get("temuan_id", "")
        obj.judul = data.get("judul", "")
        obj.tipe = data.get("tipe", "Dokumen")
        obj.deskripsi = data.get("deskripsi", "")
        obj.lokasi_file = data.get("lokasi_file", "")
        # restore private via name mangling
        obj._BuktiAudit__bukti_pendukung = data.get("bukti_pendukung", [])
        return obj
