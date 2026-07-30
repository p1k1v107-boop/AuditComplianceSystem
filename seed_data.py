"""Script untuk mengisi data contoh ke semua file data."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.audit_service import AuditService
from src.services.temuan_service import TemuanService
from src.services.tindak_lanjut_service import TindakLanjutService

audit_svc = AuditService()
temuan_svc = TemuanService()
tl_svc = TindakLanjutService()


def seed():
    print("Mengisi data contoh...")

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
        "periode_mulai": "2025-01-01",
        "periode_selesai": "2025-03-31",
        "unit_kerja_id": unit1.id,
        "auditor_id": adr1.id,
        "tujuan": "Menilai kepatuhan laporan keuangan terhadap standar akuntansi",
        "status": "Pelaksanaan",
    })
    pa2 = audit_svc.tambah_audit({
        "nama": "Audit Proses Rekrutmen 2025",
        "periode_mulai": "2025-02-01",
        "periode_selesai": "2025-04-30",
        "unit_kerja_id": unit2.id,
        "auditor_id": adr2.id,
        "tujuan": "Menilai kepatuhan proses rekrutmen terhadap SOP",
        "status": "Pelaporan",
    })
    pa3 = audit_svc.tambah_audit({
        "nama": "Audit Keamanan Sistem IT",
        "periode_mulai": "2025-03-01",
        "periode_selesai": "2025-05-31",
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
        "deskripsi": "Laporan bulanan Januari dan Februari terlambat 5 hari dari batas waktu yang ditetapkan",
        "dampak": 2,
        "kemungkinan": 3,
        "tingkat_kepatuhan": 75,
        "rekomendasi": "Tetapkan reminder otomatis dan PIC yang jelas untuk setiap laporan",
        "batas_tindak_lanjut": "2025-04-30",
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
        "batas_tindak_lanjut": "2025-05-15",
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
        "batas_tindak_lanjut": "2025-06-01",
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
        "batas_tindak_lanjut": "2025-04-01",
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
        "batas_tindak_lanjut": "2025-04-15",
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

    # Tindak Lanjut
    tl_svc.tambah_tindak_lanjut({
        "temuan_id": t1.id,
        "unit_kerja_id": unit1.id,
        "tipe_tindakan": "Koreksi",
        "deskripsi": "Membuat sistem pengingat otomatis untuk deadline laporan bulanan",
        "penanggung_jawab": "Budi Santoso",
        "batas_waktu": "2025-04-15",
        "catatan": "Akan menggunakan fitur reminder di sistem ERP",
    })
    tl_svc.tambah_tindak_lanjut({
        "temuan_id": t2.id,
        "unit_kerja_id": unit1.id,
        "tipe_tindakan": "Koreksi",
        "deskripsi": "Melengkapi dokumen pendukung untuk 12 transaksi yang bermasalah",
        "penanggung_jawab": "Budi Santoso",
        "batas_waktu": "2025-05-10",
        "catatan": "Koordinasi dengan vendor untuk mendapatkan invoice",
    })
    tl_svc.tambah_tindak_lanjut({
        "temuan_id": t4.id,
        "unit_kerja_id": unit3.id,
        "tipe_tindakan": "Pencegahan",
        "deskripsi": "Rotasi kredensial, aktifkan MFA, dan audit hak akses seluruh user sistem",
        "penanggung_jawab": "Andi Wijaya",
        "batas_waktu": "2025-04-01",
        "catatan": "Prioritas tertinggi - segera eksekusi",
    })
    tl_svc.tambah_tindak_lanjut({
        "temuan_id": t5.id,
        "unit_kerja_id": unit3.id,
        "tipe_tindakan": "Koreksi",
        "deskripsi": "Konfigurasi backup otomatis menggunakan cron job dan validasi setiap minggu",
        "penanggung_jawab": "Andi Wijaya",
        "batas_waktu": "2025-04-10",
        "catatan": "Backup akan disimpan ke cloud storage",
    })
    print(f"  4 tindak lanjut ditambahkan")
    print("Seed data selesai!")


if __name__ == "__main__":
    seed()
