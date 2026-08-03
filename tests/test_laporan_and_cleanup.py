"""Test untuk laporan dan cleanup data relasional."""

from pathlib import Path

import src.services.audit_service as audit_service_module
import src.services.temuan_service as temuan_service_module
import src.services.tindak_lanjut_service as tindak_lanjut_service_module
import src.services.laporan_service as laporan_service_module

from src.services.audit_service import AuditService
from src.services.temuan_service import TemuanService
from src.services.tindak_lanjut_service import TindakLanjutService
from src.services.laporan_service import LaporanService


def _setup_services(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_service_module, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(temuan_service_module, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(temuan_service_module, "UPLOADS_DIR", tmp_path / "uploads")
    monkeypatch.setattr(tindak_lanjut_service_module, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(laporan_service_module, "LAPORAN_DIR", tmp_path / "laporan")


def _seed_minimal_data():
    audit_svc = AuditService()
    unit = audit_svc.tambah_unit({"nama": "Unit Tes", "kode": "UT-01", "kepala_unit": "Kepala"})
    auditor = audit_svc.tambah_auditor({"nama": "Auditor Tes", "jabatan": "Senior", "sertifikasi": "CIA"})
    audit = audit_svc.tambah_audit({
        "nama": "Audit Tes",
        "periode_mulai": "2026-01-01",
        "periode_selesai": "2026-01-31",
        "unit_kerja_id": unit.id,
        "auditor_id": auditor.id,
        "tujuan": "Testing",
        "status": "Pelaksanaan",
    })
    return audit_svc, unit, auditor, audit


def test_laporan_service_menghasilkan_file(tmp_path, monkeypatch):
    _setup_services(tmp_path, monkeypatch)
    audit_svc, unit, auditor, audit = _seed_minimal_data()
    temuan_svc = TemuanService()
    tl_svc = TindakLanjutService()

    temuan = temuan_svc.tambah_temuan({
        "program_audit_id": audit.id,
        "unit_kerja_id": unit.id,
        "jenis": "Mayor",
        "judul": "Temuan Tes",
        "deskripsi": "Deskripsi",
        "dampak": 4,
        "kemungkinan": 3,
        "tingkat_kepatuhan": 60,
        "rekomendasi": "Rekomendasi",
        "batas_tindak_lanjut": "2026-12-31",
    })
    temuan_svc.tambah_bukti({
        "temuan_id": temuan.id,
        "judul": "Bukti 1",
        "tipe": "Dokumen",
        "deskripsi": "Dokumen",
    })
    tl_svc.tambah_tindak_lanjut({
        "temuan_id": temuan.id,
        "unit_kerja_id": unit.id,
        "tipe_tindakan": "Koreksi",
        "deskripsi": "Tindak lanjut tes",
        "penanggung_jawab": "PIC",
        "batas_waktu": "2026-12-31",
        "catatan": "Catatan",
    })

    layanan_laporan = LaporanService()
    path_terbuka = layanan_laporan.laporan_temuan_terbuka()
    path_keterlambatan = layanan_laporan.laporan_keterlambatan()
    path_unit = layanan_laporan.laporan_unit_berisiko()
    path_efektivitas = layanan_laporan.laporan_efektivitas()

    assert Path(path_terbuka).exists()
    assert Path(path_keterlambatan).exists()
    assert Path(path_unit).exists()
    assert Path(path_efektivitas).exists()
    assert len(layanan_laporan.daftar_file_laporan()) == 4


def test_hapus_temuan_menghapus_turunan(tmp_path, monkeypatch):
    _setup_services(tmp_path, monkeypatch)
    audit_svc, unit, auditor, audit = _seed_minimal_data()
    temuan_svc = TemuanService()
    tl_svc = TindakLanjutService()

    temuan = temuan_svc.tambah_temuan({
        "program_audit_id": audit.id,
        "unit_kerja_id": unit.id,
        "jenis": "Mayor",
        "judul": "Temuan Hapus",
        "deskripsi": "Deskripsi",
        "dampak": 4,
        "kemungkinan": 3,
        "tingkat_kepatuhan": 60,
        "rekomendasi": "Rekomendasi",
        "batas_tindak_lanjut": "2026-12-31",
    })

    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_upload = uploads_dir / "bukti-hapus.txt"
    file_upload.write_text("hapus saya", encoding="utf-8")

    bukti = temuan_svc.tambah_bukti({
        "temuan_id": temuan.id,
        "judul": "Bukti Hapus",
        "tipe": "Dokumen",
        "deskripsi": "Dokumen",
        "lokasi_file": "/uploads/bukti-hapus.txt",
    })

    tl_svc.tambah_tindak_lanjut({
        "temuan_id": temuan.id,
        "unit_kerja_id": unit.id,
        "tipe_tindakan": "Koreksi",
        "deskripsi": "Tindak lanjut hapus",
        "penanggung_jawab": "PIC",
        "batas_waktu": "2026-12-31",
        "catatan": "Catatan",
    })

    assert temuan_svc.hapus_temuan(temuan.id) is True
    assert temuan_svc.detail_temuan(temuan.id) is None
    assert temuan_svc.daftar_bukti(temuan.id) == []
    assert tl_svc.tindak_lanjut_per_temuan(temuan.id) == []
    assert not file_upload.exists()
