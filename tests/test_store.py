import os
import json
from candidate_manager.store import CandidateStore, Candidate, ConsentRequiredError, decrypt


def make_store(tmp_path):
    key = b"supersecret"
    file_path = tmp_path / "data.enc"
    return CandidateStore(str(file_path), key)


def test_add_with_consent(tmp_path):
    store = make_store(tmp_path)
    cand = Candidate("1", "Ana", "ana@example.com", "cv", True)
    store.add(cand)
    assert store.get("1").name == "Ana"


def test_add_without_consent(tmp_path):
    store = make_store(tmp_path)
    cand = Candidate("1", "Ana", "ana@example.com", "cv", False)
    try:
        store.add(cand)
    except ConsentRequiredError:
        pass
    else:
        assert False, "ConsentRequiredError not raised"


def test_anonymize(tmp_path):
    store = make_store(tmp_path)
    cand = Candidate("1", "Ana", "ana@example.com", "cv", True)
    store.add(cand)
    store.anonymize("1")
    res = store.get("1")
    assert res.name is None and res.anonymized


def test_delete_and_purge(tmp_path):
    store = make_store(tmp_path)
    cand = Candidate("1", "Ana", "ana@example.com", "cv", True)
    store.add(cand)
    store.delete("1")
    assert store.get("1") is None

    # re-add and simulate old timestamp for purge
    store.add(cand)
    store._data["1"].created_at = 1
    store._save()
    store.purge_expired(retention_days=1)
    assert store.get("1") is None


def test_file_is_encrypted(tmp_path):
    key = b"supersecret"
    file_path = tmp_path / "data.enc"
    store = CandidateStore(str(file_path), key)
    cand = Candidate("1", "Ana", "ana@example.com", "cv", True)
    store.add(cand)
    with open(file_path, "rb") as fh:
        raw = fh.read()
    assert b"Ana" not in raw
    # ensure decrypting retrieves data
    assert b"Ana" in decrypt(raw, key)


def test_export_import(tmp_path):
    store = make_store(tmp_path)
    cand = Candidate("1", "Ana", "ana@example.com", "cv", True)
    store.add(cand)
    payload = store.export_encrypted("1")
    # payload should not contain plaintext name
    assert b"Ana" not in payload
    # import into new store
    new_store = make_store(tmp_path)
    new_store.import_encrypted(payload)
    assert new_store.get("1").name == "Ana"
