"""
Tests for hashing and cryptographic fingerprinting.
"""
import os
import tempfile
import pytest
from utils.hashing import hash_bytes, hash_file, hex_to_bytes32, bytes32_to_hex, verify_hashes


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
