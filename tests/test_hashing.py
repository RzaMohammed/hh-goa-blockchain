"""
Tests for hashing and cryptographic fingerprinting.
"""
import os
import tempfile
import pytest
from utils.hashing import (
    hash_bytes,
    hash_file,
    hex_to_bytes32,
    bytes32_to_hex,
    verify_hashes,
    is_valid_sha256,
    verify_file_hash,
)


def test_hash_bytes_known_value():
    data = b"hello world"
    expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    assert hash_bytes(data) == expected


def test_hash_file_tampering():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(b"Original File Contents 12345")
        temp_path = tf.name

    try:
        orig_hash = hash_file(temp_path)
        assert len(orig_hash) == 64

        # Tamper with 1 byte
        with open(temp_path, "wb") as f:
            f.write(b"Original File Contents 12346")

        tampered_hash = hash_file(temp_path)
        assert tampered_hash != orig_hash
        assert not verify_hashes(orig_hash, tampered_hash)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_hex_to_bytes32_roundtrip():
    original_hex = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    b32 = hex_to_bytes32(original_hex)
    assert len(b32) == 32
    assert bytes32_to_hex(b32) == original_hex


def test_hex_to_bytes32_with_0x_prefix():
    original_hex = "0xb94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    b32 = hex_to_bytes32(original_hex)
    assert len(b32) == 32
    assert bytes32_to_hex(b32) == original_hex[2:].lower()


def test_is_valid_sha256():
    valid = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    assert is_valid_sha256(valid) is True
    assert is_valid_sha256("0x" + valid) is True
    assert is_valid_sha256(valid.upper()) is True
    assert is_valid_sha256("invalid_hash") is False
    assert is_valid_sha256("b94d27b9") is False
    assert is_valid_sha256(12345) is False


def test_verify_file_hash():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(b"Blockchain verification test payload")
        temp_path = tf.name

    try:
        expected = hash_file(temp_path)
        assert verify_file_hash(temp_path, expected) is True
        assert verify_file_hash(temp_path, "0" * 64) is False
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_verify_file_hash_missing_file():
    with pytest.raises(FileNotFoundError):
        verify_file_hash("non_existent_file_path_12345.bin", "0" * 64)

