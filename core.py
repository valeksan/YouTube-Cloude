#!/usr/bin/env python3
"""Shared constants and utilities for YouTube File Storage.

Improvements based on work by @Hinderchik, @IvanSCP, and @sosatel30000.
See: https://github.com/Hinderchik/YouTube-Cloude-Fork
     https://github.com/IvanSCP/YouTube-Cloude
     https://github.com/sosatel30000/YouTube-Cloude
GUI concepts from @Maksim4081862.
"""
from pathlib import Path
from typing import Optional

# ── Dimensions ──────────────────────────────────────────────────────────────
WIDTH: int = 1920
HEIGHT: int = 1080
FPS: int = 6

# ── Block geometry ──────────────────────────────────────────────────────────
BLOCK_HEIGHT: int = 16
BLOCK_WIDTH: int = 24
SPACING: int = 4
MARKER_SIZE: int = 80

# ── Derived grid ────────────────────────────────────────────────────────────
BLOCKS_X: int = (WIDTH - 2 * MARKER_SIZE) // (BLOCK_WIDTH + SPACING)
BLOCKS_Y: int = (HEIGHT - 2 * MARKER_SIZE) // (BLOCK_HEIGHT + SPACING)
BLOCKS_PER_REGION: int = BLOCKS_X * BLOCKS_Y
BLOCKS_PER_FRAME: int = BLOCKS_PER_REGION * 3

# ── 16-colour palette (4-bit string -> BGR tuple) ──────────────────────────
COLORS: dict[str, tuple[int, int, int]] = {
    '0000': (255, 0, 0),
    '0001': (0, 255, 0),
    '0010': (0, 0, 255),
    '0011': (255, 255, 0),
    '0100': (255, 0, 255),
    '0101': (0, 255, 255),
    '0110': (255, 128, 0),
    '0111': (128, 0, 255),
    '1000': (0, 128, 128),
    '1001': (128, 128, 0),
    '1010': (128, 0, 128),
    '1011': (0, 128, 0),
    '1100': (128, 0, 0),
    '1101': (0, 0, 128),
    '1110': (192, 192, 192),
    '1111': (255, 255, 255),
}

# ── End-of-file marker ─────────────────────────────────────────────────────
EOF_MARKER: str = "\u2588" * 64
EOF_BYTES: bytes = EOF_MARKER.encode('utf-8')

# ── Dangerous extensions ───────────────────────────────────────────────────
DANGEROUS_EXTENSIONS: set[str] = {
    '.exe', '.bat', '.sh', '.py', '.js', '.dll', '.so', '.com',
}

# ── Max file size (100 MB) ─────────────────────────────────────────────────
MAX_FILE_SIZE: int = 100 * 1024 * 1024


# ── XOR encryption / decryption ────────────────────────────────────────────
def encrypt_data(data: bytes, key: bytes) -> bytes:
    """XOR-encrypt *data* by cycling through *key*."""
    result = bytearray()
    key_len = len(key)
    for i, byte in enumerate(data):
        result.append(byte ^ key[i % key_len])
    return bytes(result)


def decrypt_data(data: bytes, key: bytes) -> bytes:
    """XOR-decrypt *data* by cycling through *key* (symmetric)."""
    return encrypt_data(data, key)


# ── Bit / byte conversions ─────────────────────────────────────────────────
def data_to_blocks(data: bytes) -> list[str]:
    """Convert raw bytes into a list of 4-bit binary strings."""
    all_bits: list[str] = []
    for byte in data:
        for i in range(7, -1, -1):
            all_bits.append(str((byte >> i) & 1))
    while len(all_bits) % 4 != 0:
        all_bits.append('0')
    return [''.join(all_bits[i:i + 4]) for i in range(0, len(all_bits), 4)]


def blocks_to_bytes(blocks: list[str]) -> bytes:
    """Convert a list of 4-bit strings back to raw bytes."""
    all_bits = ''.join(blocks)
    buf = bytearray()
    for i in range(0, len(all_bits) - 7, 8):
        byte_str = all_bits[i:i + 8]
        if len(byte_str) == 8:
            try:
                buf.append(int(byte_str, 2))
            except ValueError:
                buf.append(0)
    return bytes(buf)


# ── File helpers ───────────────────────────────────────────────────────────
def sanitize_filename(filename: str) -> str:
    """Return a safe basename, stripping dangerous extensions."""
    import re
    name = Path(filename).name
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    parts = name.rsplit('.', 1)
    if len(parts) > 1:
        if f".{parts[1].lower()}" in DANGEROUS_EXTENSIONS:
            name = f"{parts[0]}.bin"
    return name or "file.bin"


def validate_input_file(filepath: str, max_size: int = MAX_FILE_SIZE) -> Path:
    """Validate that *filepath* exists, is a file, and is within *max_size*."""
    path = Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if not path.is_file():
        raise ValueError(f"Not a file: {filepath}")
    size = path.stat().st_size
    if size > max_size:
        raise ValueError(
            f"File too large: {size} bytes (max {max_size})"
        )
    if size == 0:
        raise ValueError("File is empty")
    return path


def read_key_from_file(key_file: str = 'key.txt') -> Optional[str]:
    """Read an encryption key from a text file, or return *None*."""
    import os
    try:
        if os.path.exists(key_file):
            with open(key_file, 'r', encoding='utf-8') as f:
                key = f.read().strip()
                if key:
                    print(f"Key loaded from {key_file}")
                    return key
                else:
                    print(f"Warning: {key_file} is empty")
        else:
            print(f"Info: {key_file} not found, encryption disabled")
    except IOError as e:
        print(f"Warning: could not read key file: {e}")
    return None
