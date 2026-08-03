"""Test untuk memastikan inheritance, polymorphism, dan encapsulation berfungsi dengan baik."""

import pytest
from src.models.temuan import TemuanAudit, TemuanMinor, TemuanMayor, TemuanKritis, buat_temuan
from src.models.bukti import BuktiAudit
from src.exceptions.custom import DataTidakValidError, StatusTransisiTidakValidError


def test_temuan_inheritance():
    """Memastikan bahwa TemuanMinor, Mayor, Kritis mewarisi TemuanAudit (Inheritance)."""
    assert issubclass(TemuanMinor, TemuanAudit)
    assert issubclass(TemuanMayor, TemuanAudit)
    assert issubclass(TemuanKritis, TemuanAudit)


def test_hitung_skor_risiko_polymorphism():
    """Memastikan setiap jenis temuan menghitung skor dengan cara yang berbeda (Polymorphism)."""
    # Semua memiliki parameter yang sama
    params = {
        "program_audit_id": "1",
        "unit_kerja_id": "1",
        "judul": "Test",
        "deskripsi": "Test",
        "dampak": 3,
        "kemungkinan": 3,
        "tingkat_kepatuhan": 50
    }
    
    t_minor = buat_temuan("Minor", **params)
    t_mayor = buat_temuan("Mayor", **params)
    t_kritis = buat_temuan("Kritis", **params)
    
    # Nilai kepatuhan faktor = (100-50)/100 = 0.5
    # Skor minor = 3 * 3 * 0.5 * 0.5 = 2.25
    assert t_minor.hitung_skor_risiko() == 2.25
    
    # Skor mayor = (3^1.2) * 3 * 0.5 * 1.0 = 3.737 * 1.5 = ~5.61
    assert t_mayor.hitung_skor_risiko() == 5.61
    
    # Skor kritis: kepatuhan_faktor = (0.5)^0.8 = ~0.574
    # skor = 3 * 3 * 0.5743 * 2.0 = 10.34
    assert t_kritis.hitung_skor_risiko() == 10.34


def test_encapsulation_status():
    """Memastikan status_tindak_lanjut terenkapsulasi dan memvalidasi transisi state."""
    t = buat_temuan("Minor", program_audit_id="1", unit_kerja_id="1", judul="T", deskripsi="D",
                    dampak=3, kemungkinan=3, tingkat_kepatuhan=50)
    
    # Status awal default Terbuka
    assert t.status_tindak_lanjut == "Terbuka"
    
    # Bisa transisi ke Dalam Proses
    t.status_tindak_lanjut = "Dalam Proses"
    assert t.status_tindak_lanjut == "Dalam Proses"
    
    # Tidak bisa transisi langsung dari Dalam Proses ke Ditutup (harus lewat Selesai)
    with pytest.raises(StatusTransisiTidakValidError):
        t.status_tindak_lanjut = "Ditutup"
        
    # Validasi input tidak valid
    with pytest.raises(DataTidakValidError):
        t.status_tindak_lanjut = "StatusNgawur"


def test_encapsulation_bukti():
    """Memastikan daftar referensi bukti pada BuktiAudit terenkapsulasi."""
    b = BuktiAudit(temuan_id="1", judul="Bukti 1", tipe="Dokumen", deskripsi="Desc")
    
    # Mengembalikan list (copy dari property, bukan list asli)
    referensi = b.bukti_pendukung
    assert len(referensi) == 0
    
    # Mengubah list kembalian tidak mengubah data di dalam objek
    referensi.append("Hack")
    assert b.jumlah_referensi() == 0
    
    # Harus menggunakan method resmi untuk memanipulasi state
    b.tambah_referensi("Ref-001")
    assert b.jumlah_referensi() == 1
    assert "Ref-001" in b.bukti_pendukung
    
    # Validasi tambah kosong
    with pytest.raises(DataTidakValidError):
        b.tambah_referensi("")
