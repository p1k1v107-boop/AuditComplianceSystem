"""Test untuk memastikan custom exceptions dilemparkan dengan benar."""

import csv
import json
from datetime import date, timedelta

import pytest
from src.exceptions.custom import BuktiAuditTidakCukupError, TindakLanjutTerlambatError
from src.services.temuan_service import TemuanService
from src.services.tindak_lanjut_service import TindakLanjutService


def test_bukti_tidak_cukup_exception(tmp_path, monkeypatch):
    """Test saat menutup temuan tanpa bukti yang memadai -> BuktiAuditTidakCukupError."""
    import src.services.temuan_service as temuan_service_module

    monkeypatch.setattr(temuan_service_module, "DATA_DIR", str(tmp_path))

    with open(tmp_path / "temuan.json", "w", encoding="utf-8") as f:
        json.dump([
            {
                "id": "t1", "jenis": "Kritis", "program_audit_id": "p1", "unit_kerja_id": "u1",
                "judul": "Test", "deskripsi": "Test", "dampak": 5, "kemungkinan": 5,
                "tingkat_kepatuhan": 0, "status_tindak_lanjut": "Selesai"
            }
        ], f)
    with open(tmp_path / "bukti.json", "w", encoding="utf-8") as f:
        json.dump([
            {"id": "b1", "temuan_id": "t1", "judul": "B1", "tipe": "Dokumen", "deskripsi": "D"}
        ], f)
        
    svc = TemuanService()
    
    # Temuan Kritis butuh 3 bukti, tapi hanya ada 1
    with pytest.raises(BuktiAuditTidakCukupError) as exc_info:
        svc.tutup_temuan("t1")
        
    assert exc_info.value.temuan_id == "t1"
    assert exc_info.value.jumlah_bukti == 1
    assert exc_info.value.minimum == 3


def test_tindak_lanjut_terlambat_exception(tmp_path, monkeypatch):
    """Test saat mengubah status TL jika batas waktu terlewati -> TindakLanjutTerlambatError."""
    import src.services.tindak_lanjut_service as tindak_lanjut_service_module

    monkeypatch.setattr(tindak_lanjut_service_module, "DATA_DIR", str(tmp_path))
    
    # Setup data dummy (batas waktu kemarin)
    kemarin = (date.today() - timedelta(days=1)).isoformat()
    with open(tmp_path / "tindak_lanjut.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "temuan_id", "unit_kerja_id", "tipe_tindakan", "deskripsi",
            "penanggung_jawab", "batas_waktu", "tanggal_pelaksanaan",
            "status", "catatan", "riwayat", "created_at", "updated_at"
        ])
        writer.writeheader()
        writer.writerow({
            "id": "tl1", "temuan_id": "t1", "unit_kerja_id": "u1", 
            "tipe_tindakan": "Koreksi", "deskripsi": "Test TL",
            "penanggung_jawab": "A", "batas_waktu": kemarin, 
            "status": "Dalam Proses", "riwayat": "[]"
        })
        
    svc = TindakLanjutService()
    
    # Update ke status yang bukan "Terlambat" padahal sudah melewati batas waktu
    with pytest.raises(TindakLanjutTerlambatError) as exc_info:
        svc.perbarui_status("tl1", "Selesai")
        
    assert exc_info.value.tindak_lanjut_id == "tl1"
    assert exc_info.value.batas_waktu == kemarin
