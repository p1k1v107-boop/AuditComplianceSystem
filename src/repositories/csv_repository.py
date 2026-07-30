"""Repository generik untuk operasi baca-tulis file CSV."""

import csv
import os
from src.exceptions.custom import FileTidakDitemukanError, GagalSimpanError, DataTidakValidError


class CsvRepository:
    """Menangani semua operasi CRUD berbasis file CSV."""

    def __init__(self, path: str, fieldnames: list):
        self.path = path
        self.fieldnames = fieldnames
        self._pastikan_file_ada()

    def _pastikan_file_ada(self):
        """Buat file CSV dengan header jika belum ada."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            self._tulis_header()

    def _tulis_header(self):
        """Tulis header CSV ke file baru."""
        try:
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
        except OSError as e:
            raise GagalSimpanError(self.path, str(e))

    def _baca_raw(self) -> list:
        """Baca semua baris dari file CSV."""
        try:
            with open(self.path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return [dict(row) for row in reader]
        except FileNotFoundError:
            raise FileTidakDitemukanError(self.path)
        except csv.Error as e:
            raise DataTidakValidError("csv", self.path, f"Format CSV rusak: {e}")

    def _tulis_semua(self, data: list):
        """Tulis ulang seluruh isi file CSV."""
        try:
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(data)
        except OSError as e:
            raise GagalSimpanError(self.path, str(e))

    def baca_semua(self) -> list:
        """Kembalikan semua record dari file."""
        return self._baca_raw()

    def cari_id(self, id: str) -> dict | None:
        """Cari record berdasarkan id."""
        for record in self._baca_raw():
            if record.get("id") == id:
                return record
        return None

    def simpan(self, record: dict):
        """Tambah record baru ke file CSV."""
        try:
            with open(self.path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames, extrasaction="ignore")
                writer.writerow(record)
        except OSError as e:
            raise GagalSimpanError(self.path, str(e))

    def perbarui(self, id: str, record_baru: dict) -> bool:
        """Perbarui record yang cocok dengan id, tulis ulang seluruh file."""
        data = self._baca_raw()
        ditemukan = False
        for i, item in enumerate(data):
            if item.get("id") == id:
                data[i] = record_baru
                ditemukan = True
                break
        if ditemukan:
            self._tulis_semua(data)
        return ditemukan

    def hapus(self, id: str) -> bool:
        """Hapus record berdasarkan id."""
        data = self._baca_raw()
        data_baru = [item for item in data if item.get("id") != id]
        if len(data_baru) == len(data):
            return False
        self._tulis_semua(data_baru)
        return True

    def filter_by(self, field: str, nilai: str) -> list:
        """Filter record berdasarkan nilai field tertentu."""
        return [r for r in self._baca_raw() if r.get(field) == nilai]

    def jumlah(self) -> int:
        """Hitung jumlah total record."""
        return len(self._baca_raw())
