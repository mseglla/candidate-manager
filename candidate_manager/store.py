"""Storage module with privacy features.

This module provides a :class:`CandidateStore` that handles candidate data
with explicit consent checks, anonymization, right to be forgotten, limited
retention and simple XOR based encryption for data at rest and in transit.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import os
import time
import base64
from typing import Dict, Optional


@dataclass
class Candidate:
    """Representation of a candidate."""
    candidate_id: str
    name: Optional[str]
    email: Optional[str]
    cv: Optional[str]
    consent: bool
    created_at: float | None = None
    anonymized: bool = False


class ConsentRequiredError(Exception):
    """Raised when trying to store candidate data without consent."""


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """Return XOR of ``data`` with ``key`` repeated as needed."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """Encrypt ``plaintext`` using XOR and return base64 encoded bytes."""
    return base64.b64encode(_xor_bytes(plaintext, key))


def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """Decrypt base64 encoded ``ciphertext`` produced by :func:`encrypt`."""
    raw = base64.b64decode(ciphertext)
    return _xor_bytes(raw, key)


class CandidateStore:
    """Store candidate information with privacy features."""

    def __init__(self, file_path: str, key: bytes):
        self.file_path = file_path
        self.key = key
        self._data: Dict[str, Candidate] = {}
        if os.path.exists(self.file_path):
            self._load()

    def _load(self) -> None:
        with open(self.file_path, "rb") as fh:
            plaintext = decrypt(fh.read(), self.key)
        raw = json.loads(plaintext.decode())
        self._data = {cid: Candidate(**c) for cid, c in raw.items()}

    def _save(self) -> None:
        raw = {cid: asdict(c) for cid, c in self._data.items()}
        plaintext = json.dumps(raw).encode()
        ciphertext = encrypt(plaintext, self.key)
        with open(self.file_path, "wb") as fh:
            fh.write(ciphertext)

    def add(self, candidate: Candidate) -> None:
        """Add a candidate after verifying consent."""
        if not candidate.consent:
            raise ConsentRequiredError("Explicit consent required")
        candidate.created_at = time.time()
        self._data[candidate.candidate_id] = candidate
        self._save()

    def get(self, candidate_id: str) -> Optional[Candidate]:
        return self._data.get(candidate_id)

    def anonymize(self, candidate_id: str) -> None:
        cand = self._data.get(candidate_id)
        if not cand:
            return
        cand.name = None
        cand.email = None
        cand.cv = None
        cand.anonymized = True
        self._save()

    def delete(self, candidate_id: str) -> None:
        if candidate_id in self._data:
            del self._data[candidate_id]
            self._save()

    def purge_expired(self, retention_days: int) -> None:
        """Remove candidates older than ``retention_days`` days."""
        cutoff = time.time() - retention_days * 86400
        to_delete = [cid for cid, c in self._data.items() if c.created_at and c.created_at < cutoff]
        for cid in to_delete:
            del self._data[cid]
        if to_delete:
            self._save()

    def export_encrypted(self, candidate_id: str) -> Optional[bytes]:
        """Return encrypted payload for secure transit."""
        cand = self._data.get(candidate_id)
        if not cand:
            return None
        payload = json.dumps(asdict(cand)).encode()
        return encrypt(payload, self.key)

    def import_encrypted(self, data: bytes) -> Candidate:
        """Import candidate data from an encrypted payload."""
        payload = decrypt(data, self.key)
        cdict = json.loads(payload.decode())
        candidate = Candidate(**cdict)
        self._data[candidate.candidate_id] = candidate
        self._save()
        return candidate
