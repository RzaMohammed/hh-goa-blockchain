"""
Cryptographic Hashing Utilities using SHA-256.
Generates and verifies cryptographic fingerprints of raw file bytes for blockchain storage.
"""
import hashlib
import os
from typing import Union


def hash_bytes(data: bytes) -> str:
    """
    Computes the SHA-256 cryptographic hash of raw byte data.
    Returns 64-character lowercase hexadecimal string.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(f"Expected bytes or bytearray, got {type(data)}")
    return hashlib.sha256(data).hexdigest().lower()


def hash_file(file_path: str, chunk_size: int = 65536) -> str:
    """
    Computes the SHA-256 cryptographic hash of a file by streaming its bytes.
    Returns 64-character lowercase hexadecimal string.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest().lower()


def hex_to_bytes32(hex_string: str) -> bytes:
    """
    Converts a 64-character hexadecimal string (with or without '0x' prefix)
    into a 32-byte binary object for Solidity bytes32 representation.
    """
    clean_hex = hex_string.strip()
    if clean_hex.startswith("0x") or clean_hex.startswith("0X"):
        clean_hex = clean_hex[2:]

    if len(clean_hex) != 64:
        raise ValueError(f"Hex string must be 64 characters long (32 bytes), got {len(clean_hex)}")

    return bytes.fromhex(clean_hex)


def bytes32_to_hex(b32: Union[bytes, str]) -> str:
    """
    Converts a 32-byte binary object or hex string into a standard
    64-character lowercase hexadecimal string.
    """
    if isinstance(b32, str):
        clean = b32.strip().lower()
        return clean[2:] if clean.startswith("0x") else clean
    elif isinstance(b32, (bytes, bytearray)):
        return b32.hex().lower()
    else:
        raise TypeError(f"Expected bytes or str, got {type(b32)}")


def verify_hashes(hash_a: str, hash_b: str) -> bool:
    """
    Case-insensitive comparison of two hex hashes.
    """
    return bytes32_to_hex(hash_a) == bytes32_to_hex(hash_b)


def is_valid_sha256(hex_string: str) -> bool:
    """
    Validates if a string represents a valid 64-character SHA-256 hexadecimal digest.
    """
    if not isinstance(hex_string, str):
        return False
    clean = hex_string.strip()
    if clean.startswith("0x") or clean.startswith("0X"):
        clean = clean[2:]
    if len(clean) != 64:
        return False
    return all(c in "0123456789abcdefABCDEF" for c in clean)


def verify_file_hash(file_path: str, expected_hash: str) -> bool:
    """
    Verifies if the SHA-256 hash of a file matches an expected hash digest.
    Returns True if hashes match, False otherwise.
    Raises FileNotFoundError if file_path does not exist.
    """
    actual_hash = hash_file(file_path)
    return verify_hashes(actual_hash, expected_hash)

