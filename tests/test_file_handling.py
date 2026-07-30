"""Test untuk memastikan operasi read-write JSON dan CSV berjalan baik tanpa kehilangan data."""

import os
from src.repositories.json_repository import JsonRepository
from src.repositories.csv_repository import CsvRepository


def test_json_read_write(tmp_path):
    """Test Create, Read, Update, Delete ke file JSON."""
    file_path = tmp_path / "test_data.json"
    repo = JsonRepository(str(file_path))
    
    # Create
    repo.simpan({"id": "1", "nama": "A"})
    repo.simpan({"id": "2", "nama": "B"})
    
    assert repo.jumlah() == 2
    assert repo.cari_id("1")["nama"] == "A"
    
    # Update
    repo.perbarui("1", {"id": "1", "nama": "X"})
    assert repo.cari_id("1")["nama"] == "X"
    
    # Delete
    repo.hapus("2")
    assert repo.jumlah() == 1
    assert repo.cari_id("2") is None


def test_csv_read_write(tmp_path):
    """Test Create, Read, Update, Delete ke file CSV dan penanganan data hilang."""
    file_path = tmp_path / "test_data.csv"
    fields = ["id", "nama", "nilai"]
    repo = CsvRepository(str(file_path), fields)
    
    # Create
    repo.simpan({"id": "c1", "nama": "CSV 1", "nilai": "100"})
    repo.simpan({"id": "c2", "nama": "CSV 2", "nilai": "200"})
    
    data = repo.baca_semua()
    assert len(data) == 2
    assert data[0]["nama"] == "CSV 1"
    
    # Update (Tulis ulang tanpa kehilangan data lainnya)
    sukses = repo.perbarui("c1", {"id": "c1", "nama": "CSV X", "nilai": "100"})
    assert sukses is True
    
    data = repo.baca_semua()
    assert data[0]["nama"] == "CSV X"
    assert data[1]["nama"] == "CSV 2" # Data kedua tetap utuh
    
    # Delete
    repo.hapus("c1")
    assert repo.jumlah() == 1
    assert repo.cari_id("c1") is None
