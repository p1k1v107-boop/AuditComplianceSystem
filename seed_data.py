"""Script untuk mengisi data contoh ke semua file data."""

import sys
from datetime import date, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.services.audit_service import AuditService
from src.services.temuan_service import TemuanService
from src.services.tindak_lanjut_service import TindakLanjutService

DATA_FILES = [
    BASE_DIR / "data" / "audit.json",
    BASE_DIR / "data" / "auditor.json",
    BASE_DIR / "data" / "unit_kerja.json",
    BASE_DIR / "data" / "temuan.json",
    BASE_DIR / "data" / "bukti.json",
    BASE_DIR / "data" / "rekomendasi.json",
    BASE_DIR / "data" / "tindak_lanjut.csv",
]


def _reset_seed_data():
    """Hapus data lama agar seed bisa dijalankan berulang tanpa duplikasi."""
    for file_path in DATA_FILES:
        if file_path.exists():
            file_path.unlink()


def _build_services():
    audit_svc = AuditService()
    temuan_svc = TemuanService()
    tl_svc = TindakLanjutService()
    return audit_svc, temuan_svc, tl_svc


def _iso(days_from_today: int) -> str:
    return (date.today() + timedelta(days=days_from_today)).isoformat()


def seed():
    print("Mengisi data contoh...")
    _reset_seed_data()
    audit_svc, temuan_svc, tl_svc = _build_services()

    # Unit Kerja
    unit1 = audit_svc.tambah_unit({"nama": "Divisi Keuangan", "kode": "DIV-KEU", "kepala_unit": "Budi Santoso"})
    unit2 = audit_svc.tambah_unit({"nama": "Divisi SDM", "kode": "DIV-SDM", "kepala_unit": "Sari Dewi"})
    unit3 = audit_svc.tambah_unit({"nama": "Divisi IT", "kode": "DIV-IT", "kepala_unit": "Andi Wijaya"})
    print(f"  3 unit kerja ditambahkan")

    # Auditor
    adr1 = audit_svc.tambah_auditor({"nama": "Rudi Hartono", "jabatan": "Auditor Senior", "sertifikasi": "CIA, CISA"})
    adr2 = audit_svc.tambah_auditor({"nama": "Maya Sari", "jabatan": "Auditor Junior", "sertifikasi": "CIA"})
    adr3 = audit_svc.tambah_auditor({"nama": "Dodi Firmansyah", "jabatan": "Ketua Tim Audit", "sertifikasi": "CIA, CFE, CISA"})
    print(f"  3 auditor ditambahkan")

    # Program Audit
    pa1 = audit_svc.tambah_audit({
        "nama": "Audit Laporan Keuangan Q1 2025",
        "periode_mulai": _iso(-120),
        "periode_selesai": _iso(-60),
        "unit_kerja_id": unit1.id,
        "auditor_id": adr1.id,
        "tujuan": "Menilai kepatuhan laporan keuangan terhadap standar akuntansi",
        "status": "Pelaksanaan",
    })
    pa2 = audit_svc.tambah_audit({
        "nama": "Audit Proses Rekrutmen 2025",
        "periode_mulai": _iso(-90),
        "periode_selesai": _iso(-30),
        "unit_kerja_id": unit2.id,
        "auditor_id": adr2.id,
        "tujuan": "Menilai kepatuhan proses rekrutmen terhadap SOP",
        "status": "Pelaporan",
    })
    pa3 = audit_svc.tambah_audit({
        "nama": "Audit Keamanan Sistem IT",
        "periode_mulai": _iso(-60),
        "periode_selesai": _iso(30),
        "unit_kerja_id": unit3.id,
        "auditor_id": adr3.id,
        "tujuan": "Menilai penerapan kebijakan keamanan informasi",
        "status": "Pelaksanaan",
    })
    print(f"  3 program audit ditambahkan")

    # Temuan
    t1 = temuan_svc.tambah_temuan({
        "program_audit_id": pa1.id,
        "unit_kerja_id": unit1.id,
        "jenis": "Minor",
        "judul": "Keterlambatan penyusunan laporan bulanan",
        "deskripsi": "Laporan bulanan terlambat 5 hari dari batas waktu yang ditetapkan",
        "dampak": 2,
        "kemungkinan": 3,
        "tingkat_kepatuhan": 75,
        "rekomendasi": "Tetapkan reminder otomatis dan PIC yang jelas untuk setiap laporan",
        "batas_tindak_lanjut": _iso(14),
    })
    t2 = temuan_svc.tambah_temuan({
        "program_audit_id": pa1.id,
        "unit_kerja_id": unit1.id,
        "jenis": "Mayor",
        "judul": "Pengeluaran tidak didukung dokumen lengkap",
        "deskripsi": "Ditemukan 12 transaksi pengeluaran senilai Rp 150 juta tanpa dokumen pendukung yang sah",
        "dampak": 4,
        "kemungkinan": 3,
        "tingkat_kepatuhan": 55,
        "rekomendasi": "Lakukan verifikasi dokumen sebelum persetujuan pengeluaran",
        "batas_tindak_lanjut": _iso(21),
    })
    t3 = temuan_svc.tambah_temuan({
        "program_audit_id": pa2.id,
        "unit_kerja_id": unit2.id,
        "jenis": "Minor",
        "judul": "Data kandidat tidak tersimpan secara sistematis",
        "deskripsi": "Database kandidat rekrutmen tidak diperbarui secara berkala",
        "dampak": 2,
        "kemungkinan": 2,
        "tingkat_kepatuhan": 80,
        "rekomendasi": "Gunakan sistem ATS (Applicant Tracking System) yang terintegrasi",
        "batas_tindak_lanjut": _iso(10),
    })
    t4 = temuan_svc.tambah_temuan({
        "program_audit_id": pa3.id,
        "unit_kerja_id": unit3.id,
        "jenis": "Kritis",
        "judul": "Akses sistem tidak terotorisasi terdeteksi",
        "deskripsi": "Log sistem menunjukkan 3 percobaan akses tidak sah ke server database produksi",
        "dampak": 5,
        "kemungkinan": 4,
        "tingkat_kepatuhan": 30,
        "rekomendasi": "Segera rotasi semua kredensial, aktifkan MFA, dan audit hak akses seluruh user",
        "batas_tindak_lanjut": _iso(7),
    })
    t5 = temuan_svc.tambah_temuan({
        "program_audit_id": pa3.id,
        "unit_kerja_id": unit3.id,
        "jenis": "Mayor",
        "judul": "Backup data tidak dilakukan secara terjadwal",
        "deskripsi": "Backup database produksi terakhir dilakukan 45 hari yang lalu, melanggar SOP 7 hari",
        "dampak": 4,
        "kemungkinan": 4,
        "tingkat_kepatuhan": 40,
        "rekomendasi": "Konfigurasi backup otomatis harian dan validasi bulanan",
        "batas_tindak_lanjut": _iso(30),
    })
    print(f"  5 temuan ditambahkan")

    # Bukti untuk temuan kritis (perlu 3)
    temuan_svc.tambah_bukti({"temuan_id": t4.id, "judul": "Log Akses Server", "tipe": "Data Elektronik", "deskripsi": "Export log akses tanggal 1-15 Maret 2025"})
    temuan_svc.tambah_bukti({"temuan_id": t4.id, "judul": "Foto Alert Sistem", "tipe": "Foto", "deskripsi": "Screenshot notifikasi IDS"})
    temuan_svc.tambah_bukti({"temuan_id": t4.id, "judul": "Wawancara Admin IT", "tipe": "Wawancara", "deskripsi": "Notulen wawancara dengan admin sistem"})
    # Bukti untuk temuan mayor (perlu 2)
    temuan_svc.tambah_bukti({"temuan_id": t2.id, "judul": "Daftar Transaksi Bermasalah", "tipe": "Dokumen", "deskripsi": "Rekap 12 transaksi tanpa dokumen"})
    temuan_svc.tambah_bukti({"temuan_id": t2.id, "judul": "Bukti Transfer", "tipe": "Data Elektronik", "deskripsi": "Mutasi rekening terkait"})
    print(f"  5 bukti ditambahkan")

    # Tutup temuan yang sudah memiliki bukti cukup agar contoh data lebih realistis
    temuan_svc.tutup_temuan(t2.id)
    temuan_svc.tutup_temuan(t4.id)

    # Status awal tindak lanjut dibuat bervariasi sesuai skenario demo
    tl_list = tl_svc.daftar_tindak_lanjut()
    for tl in tl_list:
        if tl.temuan_id == t1.id:
            tl_svc.perbarui_status(tl.id, "Dalam Proses", "Sedang menyiapkan pengingat otomatis")
        elif tl.temuan_id == t2.id:
            tl_svc.perbarui_status(tl.id, "Selesai", "Dokumen pendukung telah dilengkapi")
        elif tl.temuan_id == t4.id:
            tl_svc.perbarui_status(tl.id, "Dalam Proses", "Rotasi kredensial dan MFA sedang diterapkan")
        elif tl.temuan_id == t5.id:
            tl_svc.perbarui_status(tl.id, "Belum Mulai", "Menunggu persetujuan jadwal implementasi")

    # Tindak Lanjut
    tl_svc.tambah_tindak_lanjut({
        "temuan_id": t1.id,
        "unit_kerja_id": unit1.id,
        "tipe_tindakan": "Koreksi",
        "deskripsi": "Membuat sistem pengingat otomatis untuk deadline laporan bulanan",
        "penanggung_jawab": "Budi Santoso",
        "batas_waktu": _iso(14),
        "catatan": "Akan menggunakan fitur reminder di sistem ERP",
    })
    tl_svc.tambah_tindak_lanjut({
        "temuan_id": t2.id,
        "unit_kerja_id": unit1.id,
        "tipe_tindakan": "Koreksi",
        "deskripsi": "Melengkapi dokumen pendukung untuk 12 transaksi yang bermasalah",
        "penanggung_jawab": "Budi Santoso",
        "batas_waktu": _iso(21),
        "catatan": "Koordinasi dengan vendor untuk mendapatkan invoice",
    })
    tl_svc.tambah_tindak_lanjut({
        "temuan_id": t4.id,
        "unit_kerja_id": unit3.id,
        "tipe_tindakan": "Pencegahan",
        "deskripsi": "Rotasi kredensial, aktifkan MFA, dan audit hak akses seluruh user sistem",
        "penanggung_jawab": "Andi Wijaya",
        "batas_waktu": _iso(7),
        "catatan": "Prioritas tertinggi - segera eksekusi",
    })
    tl_svc.tambah_tindak_lanjut({
        "temuan_id": t5.id,
        "unit_kerja_id": unit3.id,
        "tipe_tindakan": "Koreksi",
        "deskripsi": "Konfigurasi backup otomatis menggunakan cron job dan validasi setiap minggu",
        "penanggung_jawab": "Andi Wijaya",
        "batas_waktu": _iso(30),
        "catatan": "Backup akan disimpan ke cloud storage",
    })
    print(f"  4 tindak lanjut ditambahkan")

    # Status awal tindak lanjut dibuat bervariasi sesuai skenario demo
    tl_list = tl_svc.daftar_tindak_lanjut()
    for tl in tl_list:
        if tl.temuan_id == t1.id:
            tl_svc.perbarui_status(tl.id, "Dalam Proses", "Sedang menyiapkan pengingat otomatis")
        elif tl.temuan_id == t2.id:
            tl_svc.perbarui_status(tl.id, "Selesai", "Dokumen pendukung telah dilengkapi")
        elif tl.temuan_id == t4.id:
            tl_svc.perbarui_status(tl.id, "Dalam Proses", "Rotasi kredensial dan MFA sedang diterapkan")
        elif tl.temuan_id == t5.id:
            tl_svc.perbarui_status(tl.id, "Belum Mulai", "Menunggu persetujuan jadwal implementasi")
    print("Seed data selesai!")


if __name__ == "__main__":
    seed()
