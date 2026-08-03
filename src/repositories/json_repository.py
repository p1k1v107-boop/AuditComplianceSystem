"""Repository generik untuk operasi baca-tulis file JSON."""

import json
import os
from src.exceptions.custom import FileTidakDitemukanError, GagalSimpanError, DataTidakValidError


class JsonRepository:
    """Menangani semua operasi CRUD berbasis file JSON."""

    def __init__(self, path: str):
        self.path = path
        self._pastikan_file_ada()

    def _pastikan_file_ada(self):
        """Buat file JSON kosong jika belum ada."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            self._tulis([])

    def _baca_raw(self) -> list:
        """Baca isi file JSON dan kembalikan sebagai list."""
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    raise DataTidakValidError("format", self.path, "File JSON harus berisi array")
                return data
        except FileNotFoundError:
            raise FileTidakDitemukanError(self.path)
        except json.JSONDecodeError as e:
            raise DataTidakValidError("json", self.path, f"Format JSON rusak: {e}")

    def _tulis(self, data: list):
        """Tulis data list ke file JSON."""
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            raise GagalSimpanError(self.path, str(e))

    def baca_semua(self) -> list:
        """Kembalikan semua record dari file."""
        return self._baca_raw()

    def cari_id(self, id: str) -> dict | None:
        """Cari record berdasarkan id."""
        data = self._baca_raw()
        for record in data:
            if record.get("id") == id:
                return record
        return None

    def simpan(self, record: dict):
        """Tambah record baru ke file."""
        data = self._baca_raw()
        data.append(record)
        self._tulis(data)

    def perbarui(self, id: str, record_baru: dict) -> bool:
        """Perbarui record yang cocok dengan id."""
        data = self._baca_raw()
        for i, item in enumerate(data):
            if item.get("id") == id:
                data[i] = record_baru
                self._tulis(data)
                return True
        return False

    def hapus(self, id: str) -> bool:
        """Hapus record berdasarkan id."""
        data = self._baca_raw()
        data_baru = [item for item in data if item.get("id") != id]
        if len(data_baru) == len(data):
            return False
        self._tulis(data_baru)
        return True

    def hapus_filter_by(self, field: str, nilai) -> int:
        """Hapus semua record yang cocok dengan nilai field tertentu."""
        data = self._baca_raw()
        data_baru = [item for item in data if item.get(field) != nilai]
        jumlah_dihapus = len(data) - len(data_baru)
        if jumlah_dihapus:
            self._tulis(data_baru)
        return jumlah_dihapus

    def filter_by(self, field: str, nilai) -> list:
        """Filter record berdasarkan nilai field tertentu."""
        return [r for r in self._baca_raw() if r.get(field) == nilai]

    def jumlah(self) -> int:
        """Hitung jumlah total record."""
        return len(self._baca_raw())
