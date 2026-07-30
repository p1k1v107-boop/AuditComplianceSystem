"""Service untuk generate laporan audit dalam format TXT dan CSV."""

import csv
import os
from datetime import datetime
from src.services.temuan_service import TemuanService
from src.services.tindak_lanjut_service import TindakLanjutService
from src.services.audit_service import AuditService
from src.exceptions.custom import GagalSimpanError

LAPORAN_DIR = "data/laporan"


def _pastikan_dir():
    os.makedirs(LAPORAN_DIR, exist_ok=True)


class LaporanService:
    """Generate dan simpan laporan audit ke file TXT dan CSV."""

    def __init__(self):
        self._svc_temuan = TemuanService()
        self._svc_tl = TindakLanjutService()
        self._svc_audit = AuditService()

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def laporan_temuan_terbuka(self) -> str:
        """Generate laporan temuan terbuka ke file TXT."""
        _pastikan_dir()
        temuan_list = self._svc_temuan.temuan_terbuka()
        nama_file = f"{LAPORAN_DIR}/temuan_terbuka_{self._timestamp()}.txt"
        try:
            with open(nama_file, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("LAPORAN TEMUAN AUDIT TERBUKA\n")
                f.write(f"Dibuat: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write("=" * 60 + "\n\n")
                if not temuan_list:
                    f.write("Tidak ada temuan terbuka.\n")
                for i, t in enumerate(temuan_list, 1):
                    f.write(f"{i}. [{t.JENIS}] {t.judul}\n")
                    f.write(f"   Status  : {t.status_tindak_lanjut}\n")
                    f.write(f"   Dampak  : {t.dampak} | Kemungkinan: {t.kemungkinan}\n")
                    f.write(f"   Skor Risiko: {t.hitung_skor_risiko()} ({t.label_risiko()})\n")
                    f.write(f"   Batas TL: {t.batas_tindak_lanjut or '-'}\n")
                    f.write("\n")
                f.write(f"Total: {len(temuan_list)} temuan terbuka\n")
        except OSError as e:
            raise GagalSimpanError(nama_file, str(e))
        return nama_file

    def laporan_keterlambatan(self) -> str:
        """Generate laporan tindak lanjut terlambat ke file TXT."""
        _pastikan_dir()
        terlambat = self._svc_tl.cek_keterlambatan()
        nama_file = f"{LAPORAN_DIR}/keterlambatan_{self._timestamp()}.txt"
        try:
            with open(nama_file, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("LAPORAN KETERLAMBATAN TINDAK LANJUT\n")
                f.write(f"Dibuat: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                f.write("=" * 60 + "\n\n")
                if not terlambat:
                    f.write("Tidak ada tindak lanjut yang terlambat.\n")
                for i, tl in enumerate(terlambat, 1):
                    f.write(f"{i}. ID: {tl.id[:8]}...\n")
                    f.write(f"   Tindakan     : {tl.tipe_tindakan}\n")
                    f.write(f"   PJ           : {tl.penanggung_jawab}\n")
                    f.write(f"   Batas Waktu  : {tl.batas_waktu}\n")
                    f.write(f"   Status       : {tl.status}\n\n")
                f.write(f"Total: {len(terlambat)} tindak lanjut terlambat\n")
        except OSError as e:
            raise GagalSimpanError(nama_file, str(e))
        return nama_file

    def laporan_unit_berisiko(self) -> str:
        """Generate laporan unit kerja berdasarkan akumulasi skor risiko ke CSV."""
        _pastikan_dir()
        temuan_list = self._svc_temuan.daftar_temuan()
        unit_list = self._svc_audit.daftar_unit()

        skor_per_unit: dict = {}
        for t in temuan_list:
            skor_per_unit.setdefault(t.unit_kerja_id, 0)
            skor_per_unit[t.unit_kerja_id] += t.hitung_skor_risiko()

        unit_map = {u.id: u.nama for u in unit_list}
        ranking = sorted(skor_per_unit.items(), key=lambda x: x[1], reverse=True)

        nama_file = f"{LAPORAN_DIR}/unit_berisiko_{self._timestamp()}.csv"
        try:
            with open(nama_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Ranking", "Unit Kerja", "Total Skor Risiko", "Jumlah Temuan"])
                for rank, (uid, skor) in enumerate(ranking, 1):
                    jumlah = len([t for t in temuan_list if t.unit_kerja_id == uid])
                    writer.writerow([rank, unit_map.get(uid, uid), round(skor, 2), jumlah])
        except OSError as e:
            raise GagalSimpanError(nama_file, str(e))
        return nama_file

    def laporan_efektivitas(self) -> str:
        """Generate laporan efektivitas tindak lanjut per unit kerja ke CSV."""
        _pastikan_dir()
        tl_list = self._svc_tl.daftar_tindak_lanjut()
        unit_list = self._svc_audit.daftar_unit()
        unit_map = {u.id: u.nama for u in unit_list}

        data_per_unit: dict = {}
        for tl in tl_list:
            uid = tl.unit_kerja_id
            if uid not in data_per_unit:
                data_per_unit[uid] = {"total": 0, "selesai": 0, "terlambat": 0}
            data_per_unit[uid]["total"] += 1
            if tl.status == "Selesai":
                data_per_unit[uid]["selesai"] += 1
            if tl.status == "Terlambat":
                data_per_unit[uid]["terlambat"] += 1

        nama_file = f"{LAPORAN_DIR}/efektivitas_{self._timestamp()}.csv"
        try:
            with open(nama_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Unit Kerja", "Total TL", "Selesai", "Terlambat", "Efektivitas (%)"
                ])
                for uid, stat in data_per_unit.items():
                    total = stat["total"]
                    efektivitas = round((stat["selesai"] / total * 100) if total > 0 else 0, 1)
                    writer.writerow([
                        unit_map.get(uid, uid),
                        total,
                        stat["selesai"],
                        stat["terlambat"],
                        efektivitas,
                    ])
        except OSError as e:
            raise GagalSimpanError(nama_file, str(e))
        return nama_file

    def daftar_file_laporan(self) -> list[dict]:
        """Kembalikan daftar file laporan yang sudah dihasilkan."""
        _pastikan_dir()
        hasil = []
        for fname in sorted(os.listdir(LAPORAN_DIR), reverse=True):
            path = os.path.join(LAPORAN_DIR, fname)
            if os.path.isfile(path):
                hasil.append({
                    "nama": fname,
                    "ukuran": os.path.getsize(path),
                    "dibuat": datetime.fromtimestamp(os.path.getctime(path)).strftime("%d/%m/%Y %H:%M"),
                })
        return hasil
