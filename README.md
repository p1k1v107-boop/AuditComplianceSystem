# Sistem Audit Kepatuhan dan Tindak Lanjut Temuan

Aplikasi web berbasis FastAPI untuk merencanakan audit, menetapkan auditor, mencatat bukti, temuan, tingkat risiko, dan tindak lanjut unit kerja.

## Fitur Utama

- **Dashboard Statistik**: Ringkasan data program audit, distribusi temuan, dan status tindak lanjut.
- **Manajemen Program Audit**: Mengelola data program audit, unit kerja, dan auditor.
- **Manajemen Temuan & Bukti (Polymorphism & Encapsulation)**:
  - Pencatatan temuan dengan 3 tingkat (Minor, Mayor, Kritis) yang memiliki perhitungan skor risiko (polymorphism) berbeda-beda.
  - Penutupan temuan memerlukan minimum jumlah bukti audit yang memadai (Minor = 1, Mayor = 2, Kritis = 3).
  - Status tindak lanjut pada temuan dienkapsulasi dengan validasi transisi antar status.
- **Tindak Lanjut & Rekomendasi (Exception Handling)**:
  - Pembaruan status tindak lanjut memvalidasi tanggal batas waktu, memicu Exception jika batas waktu terlewati dan status tidak diatur menjadi Terlambat.
  - Mencatat riwayat perubahan status pada tindak lanjut.
- **Export Laporan (File Handling)**:
  - Generate Laporan Temuan Terbuka (TXT).
  - Generate Laporan Keterlambatan TL (TXT).
  - Generate Laporan Unit Berisiko (CSV).
  - Generate Laporan Efektivitas TL (CSV).
- **Data Tersimpan Otomatis**: Penyimpanan data ke file `JSON` dan `CSV` memastikan data tidak hilang.

## Struktur Proyek & Entry Point
Proyek ini mengadopsi arsitektur modular yang terorganisasi rapi dengan satu entry point yang jelas:
```text
.
├── main.py                  # Single Entry Point aplikasi FastAPI
├── requirements.txt         # Daftar dependency proyek
├── seed_data.py             # Script generator data contoh
├── data/                    # Berkas data persisten (JSON/CSV/TXT)
│   ├── laporan/             # File output txt/csv hasil generate program
│   └── ...                  # File database JSON/CSV
├── src/                     # Folder kode sumber utama (Python)
│   ├── exceptions/          # Custom Exception Handling
│   ├── models/              # Kelas Model (OOP: Inheritance, Polymorphism)
│   ├── repositories/        # File Handling (JSON & CSV Repository)
│   ├── routers/             # Routing FastAPI (Controller)
│   └── services/            # Logika Bisnis
├── static/                  # File statis (CSS/JS)
├── templates/               # UI berbasis HTML (Jinja2)
└── tests/                   # 8 Unit Tests (Pytest)
```

## Berkas Data (File Handling)
Program membaca, memodifikasi, dan menulis data secara persisten ke dalam folder `/data/`.
1. **Data JSON (CRUD)**: `audit.json`, `auditor.json`, `unit_kerja.json`, `temuan.json`, `bukti.json`.
2. **Data CSV (CRUD)**: `tindak_lanjut.csv` (menyimpan log tindak lanjut yang dapat bertambah).
3. **Data Laporan (Output Generate)**: 
   - `data/laporan/temuan_terbuka_....txt` (Laporan bentuk TXT)
   - `data/laporan/keterlambatan_tl_....txt` (Laporan bentuk TXT)
   - `data/laporan/unit_berisiko_....csv` (Laporan bentuk CSV)

## Kebutuhan Sistem
- Python 3.10+
- Dependencies sesuai `requirements.txt`

## Akun & Data Contoh
Aplikasi ini tidak memerlukan sistem login (Autentikasi) sesuai dengan spesifikasi. Namun, untuk mempermudah pengujian, Anda **wajib** menjalankan `seed_data.py` sebelum menjalankan server agar aplikasi langsung terisi dengan:
- 3 Program Audit, 3 Auditor, 3 Unit Kerja.
- 5 Temuan Audit dengan berbagai tingkat risiko (Minor, Mayor, Kritis).
- 4 Tindak Lanjut beserta status tenggat waktunya.

## Instalasi dan Menjalankan Program

1. Clone repositori ini atau masuk ke direktori proyek:
   ```bash
   cd /path/to/AuditComplianceSystem
   ```
2. (Opsional) Buat virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Generate Data Contoh (Seed Data):
   ```bash
   python seed_data.py
   ```
5. Jalankan aplikasi:
   ```bash
   python main.py
   ```
   Aplikasi akan berjalan di `http://localhost:8000`.

## Menjalankan Unit Tests (8 Unit Tests)
Terdapat 8 unit tests yang menguji Polymorphism, Encapsulation, Custom Exceptions, dan operasi file (JSON/CSV).
Untuk menjalankannya:
```bash
pytest tests/ -v
```

## Daftar Kelas (Minimal 8)
1. `BaseEntity` (Superclass)
2. `ProgramAudit` (Subclass BaseEntity)
3. `Auditor` (Subclass BaseEntity)
4. `UnitKerja` (Subclass BaseEntity)
5. `BuktiAudit` (Subclass BaseEntity dengan enkapsulasi `__bukti_pendukung`)
6. `TindakLanjut` (Subclass BaseEntity dengan riwayat status)
7. `Rekomendasi` (Subclass BaseEntity)
8. `TemuanAudit` (Superclass level 2, abstract-like dengan `hitung_skor_risiko()`)
   - `TemuanMinor` (Subclass TemuanAudit dengan override perhitungan risiko)
   - `TemuanMayor` (Subclass TemuanAudit dengan override perhitungan risiko)
   - `TemuanKritis` (Subclass TemuanAudit dengan override perhitungan risiko)

## Penanganan Exception (Custom Exceptions)
- `BuktiAuditTidakCukupError`: Terjadi saat temuan akan ditutup namun jumlah buktinya kurang dari yang disyaratkan.
- `TindakLanjutTerlambatError`: Terjadi jika batas waktu tindak lanjut sudah dilewati tanpa update status yang sesuai.
- `DataTidakValidError`, `FileTidakDitemukanError`, `GagalSimpanError`, `StatusTransisiTidakValidError`.
