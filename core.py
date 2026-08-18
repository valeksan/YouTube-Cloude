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

# ── YTV1 format (default, backward compatible) ─────────────────────────────
YTV1: dict = {
    'name': 'YTV1',
    'fps': 6,
    'block_height': 16,
    'block_width': 24,
    'spacing': 4,
    'marker_size': 80,
}

# ── YTV2 format (125x denser, from @sosatel30000) ──────────────────────────
YTV2: dict = {
    'name': 'YTV2',
    'fps': 15,
    'block_height': 8,
    'block_width': 8,
    'spacing': 1,
    'marker_size': 16,
}

# ── All known formats ───────────────────────────────────────────────────────
FORMATS: dict[str, dict] = {
    'ytv1': YTV1,
    'ytv2': YTV2,
}


def get_format(name: str = 'ytv1') -> dict:
    """Return format parameters by name ('ytv1' | 'ytv2')."""
    key = name.lower().strip()
    if key not in FORMATS:
        raise ValueError(f"Unknown format: {name!r}. Choose from: {list(FORMATS)}")
    return FORMATS[key]


def compute_grid(fmt: dict) -> dict:
    """Compute derived grid values from a format dict.

    Returns dict with: name, fps, blocks_x, blocks_y, blocks_per_region,
    blocks_per_frame, marker_size, block_width, block_height, spacing.
    """
    bw = fmt['block_width']
    bh = fmt['block_height']
    sp = fmt['spacing']
    ms = fmt['marker_size']
    bx = (WIDTH - 2 * ms) // (bw + sp)
    by = (HEIGHT - 2 * ms) // (bh + sp)
    bpr = bx * by
    return {
        'name': fmt['name'],
        'fps': fmt['fps'],
        'block_width': bw,
        'block_height': bh,
        'spacing': sp,
        'marker_size': ms,
        'blocks_x': bx,
        'blocks_y': by,
        'blocks_per_region': bpr,
        'blocks_per_frame': bpr * 3,
    }


def detect_format(marker_size: int) -> dict:
    """Auto-detect format from marker size observed in the first frame.

    YTV1 markers are 80px, YTV2 are 16px.
    """
    for fmt in FORMATS.values():
        if fmt['marker_size'] == marker_size:
            return fmt
    # Fallback: small marker → YTV2, large → YTV1
    return YTV2 if marker_size < 40 else YTV1

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
