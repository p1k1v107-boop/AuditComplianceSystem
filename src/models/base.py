"""Kelas dasar (superclass) untuk semua entitas domain."""

import uuid
from datetime import datetime


class BaseEntity:
    """Superclass dengan atribut dan method umum untuk semua entitas."""

    def __init__(self, id: str = None):
        self._id = id or str(uuid.uuid4())
        self._created_at = datetime.now().isoformat()
        self._updated_at = datetime.now().isoformat()

    @property
    def id(self) -> str:
        return self._id

    @property
    def created_at(self) -> str:
        return self._created_at

    @property
    def updated_at(self) -> str:
        return self._updated_at

    def _touch(self):
        """Update timestamp saat data diubah."""
        self._updated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Konversi entitas ke dictionary untuk serialisasi."""
        return {
            "id": self._id,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Buat instance dari dictionary."""
        obj = cls.__new__(cls)
        obj._id = data.get("id", str(uuid.uuid4()))
        obj._created_at = data.get("created_at", datetime.now().isoformat())
        obj._updated_at = data.get("updated_at", datetime.now().isoformat())
        return obj

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self._id})"
