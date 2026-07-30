"""Test fungsionalitas logika bisnis pada layer service."""

import os
from src.services.audit_service import AuditService
from src.services.temuan_service import TemuanService


def test_tambah_program_audit():
    """Menguji penambahan dan pembaruan program audit via service."""
    # Gunakan direktori test lokal untuk file
    # Mock global DATA_DIR
    import src.services.audit_service
    src.services.audit_service.DATA_DIR = "data_test"
    
    # Pastikan bersih
    if os.path.exists("data_test/audit.json"):
        os.remove("data_test/audit.json")
        
    svc = AuditService()
    audit = svc.tambah_audit({
        "nama": "Audit Keuangan",
        "periode_mulai": "2025-01-01",
        "periode_selesai": "2025-01-31",
        "unit_kerja_id": "u1",
        "auditor_id": "a1",
        "tujuan": "Testing",
        "status": "Perencanaan"
    })
    
    assert audit.nama == "Audit Keuangan"
    assert audit.status == "Perencanaan"
    
    # Verifikasi data tersimpan
    semua = svc.daftar_audit()
    assert len(semua) == 1
    
    # Perbarui data
    svc.perbarui_audit(audit.id, {"status": "Pelaksanaan"})
    audit_baru = svc.detail_audit(audit.id)
    assert audit_baru.status == "Pelaksanaan"


def test_statistik_temuan():
    """Menguji kalkulasi agregasi statistik temuan."""
    import src.services.temuan_service
    src.services.temuan_service.DATA_DIR = "data_test"
    
    if os.path.exists("data_test/temuan.json"):
        os.remove("data_test/temuan.json")
        
    svc = TemuanService()
    
    # Tambah 2 temuan minor terbuka, 1 mayor ditutup
    svc.tambah_temuan({
        "program_audit_id": "p1", "unit_kerja_id": "u1", "jenis": "Minor",
        "judul": "T1", "deskripsi": "D", "dampak": 2, "kemungkinan": 2, "tingkat_kepatuhan": 50
    })
    t2 = svc.tambah_temuan({
        "program_audit_id": "p1", "unit_kerja_id": "u1", "jenis": "Mayor",
        "judul": "T2", "deskripsi": "D", "dampak": 4, "kemungkinan": 4, "tingkat_kepatuhan": 50
    })
    
    # Set status bypass service (pakai private access) untuk testing
    repo = svc._repo_temuan
    data_t2 = repo.cari_id(t2.id)
    data_t2["status_tindak_lanjut"] = "Ditutup"
    repo.perbarui(t2.id, data_t2)
    
    stat = svc.statistik()
    assert stat["total_temuan"] == 2
    assert stat["terbuka"] == 1
    assert stat["ditutup"] == 1
    assert stat["minor"] == 1
    assert stat["mayor"] == 1
