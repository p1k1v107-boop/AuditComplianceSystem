"""Test fungsionalitas logika bisnis pada layer service."""

from src.services.audit_service import AuditService
from src.services.temuan_service import TemuanService


def _siapkan_data_referensi_audit():
    svc = AuditService()
    unit = svc.tambah_unit({"nama": "Unit Tes", "kode": "UT-01", "kepala_unit": "Kepala"})
    auditor = svc.tambah_auditor({"nama": "Auditor Tes", "jabatan": "Senior", "sertifikasi": "CIA"})
    return svc, unit, auditor


def test_tambah_program_audit(tmp_path, monkeypatch):
    """Menguji penambahan dan pembaruan program audit via service."""
    import src.services.audit_service as audit_service_module

    monkeypatch.setattr(audit_service_module, "DATA_DIR", str(tmp_path))
    svc, unit, auditor = _siapkan_data_referensi_audit()
    audit = svc.tambah_audit({
        "nama": "Audit Keuangan",
        "periode_mulai": "2025-01-01",
        "periode_selesai": "2025-01-31",
        "unit_kerja_id": unit.id,
        "auditor_id": auditor.id,
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


def test_statistik_temuan(tmp_path, monkeypatch):
    """Menguji kalkulasi agregasi statistik temuan."""
    import src.services.temuan_service as temuan_service_module
    import src.services.audit_service as audit_service_module

    monkeypatch.setattr(audit_service_module, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(temuan_service_module, "DATA_DIR", str(tmp_path))
    audit_svc, unit, auditor = _siapkan_data_referensi_audit()
    audit = audit_svc.tambah_audit({
        "nama": "Audit Tes",
        "periode_mulai": "2025-01-01",
        "periode_selesai": "2025-01-31",
        "unit_kerja_id": unit.id,
        "auditor_id": auditor.id,
        "tujuan": "Testing",
        "status": "Perencanaan",
    })
    svc = TemuanService()
    
    # Tambah 2 temuan minor terbuka, 1 mayor ditutup
    svc.tambah_temuan({
        "program_audit_id": audit.id, "unit_kerja_id": unit.id, "jenis": "Minor",
        "judul": "T1", "deskripsi": "D", "dampak": 2, "kemungkinan": 2, "tingkat_kepatuhan": 50
    })
    t2 = svc.tambah_temuan({
        "program_audit_id": audit.id, "unit_kerja_id": unit.id, "jenis": "Mayor",
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
