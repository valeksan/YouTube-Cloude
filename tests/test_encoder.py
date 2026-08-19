#!/usr/bin/env python3
"""Tests for YouTube-Cloude encode/decode pipeline.

Covers:
- Core utilities (CRC32, interlace, bit conversions, AES encryption)
- Full encode → decode roundtrip with correctness verification
- Format auto-detection
"""
import os
import sys
import tempfile
import shutil

import numpy as np
import pytest

# Ensure project root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import (
    WIDTH, HEIGHT,
    crc32_hex, verify_crc32,
    interlace_frame, deinterlace_frame,
    data_to_blocks, blocks_to_bytes,
    generate_iv, derive_key, encrypt_data, decrypt_data,
    get_format, compute_grid, detect_format,
    YTV1, YTV2, FORMATS,
)


# ── Core utilities ──────────────────────────────────────────────────────────

class TestCRC32:
    def test_roundtrip(self):
        data = b'hello world'
        crc = crc32_hex(data)
        assert len(crc) == 8
        assert verify_crc32(data, crc)

    def test_wrong_data_fails(self):
        crc = crc32_hex(b'hello')
        assert not verify_crc32(b'world', crc)

    def test_empty_data(self):
        crc = crc32_hex(b'')
        assert verify_crc32(b'', crc)


class TestInterlace:
    def test_roundtrip(self):
        frame = np.random.randint(0, 256, (HEIGHT, WIDTH, 3), dtype=np.uint8)
        interlaced = interlace_frame(frame)
        deinterlaced = deinterlace_frame(interlaced)
        assert np.array_equal(frame, deinterlaced)

    def test_changes_frame(self):
        frame = np.random.randint(0, 256, (HEIGHT, WIDTH, 3), dtype=np.uint8)
        interlaced = interlace_frame(frame)
        assert not np.array_equal(frame, interlaced)

    def test_preserves_shape(self):
        frame = np.random.randint(0, 256, (HEIGHT, WIDTH, 3), dtype=np.uint8)
        interlaced = interlace_frame(frame)
        assert interlaced.shape == frame.shape


class TestBitConversions:
    def test_roundtrip(self):
        data = b'test data for bit conversion'
        blocks = data_to_blocks(data)
        recovered = blocks_to_bytes(blocks)
        assert recovered == data

    def test_empty_data(self):
        blocks = data_to_blocks(b'')
        recovered = blocks_to_bytes(blocks)
        assert recovered == b''

    def test_single_byte(self):
        for byte in range(256):
            data = bytes([byte])
            blocks = data_to_blocks(data)
            recovered = blocks_to_bytes(blocks)
            assert recovered == data

    def test_blocks_are_4bit_strings(self):
        blocks = data_to_blocks(b'\xff')
        assert len(blocks) == 2  # 8 bits / 4 = 2 blocks
        for b in blocks:
            assert len(b) == 4
            assert all(c in '01' for c in b)


class TestAES:
    def test_roundtrip(self):
        key = derive_key('test-password')
        iv = generate_iv()
        data = b'_sensitive data_1234567890'
        encrypted = encrypt_data(data, key, iv)
        decrypted = decrypt_data(encrypted, key, iv)
        assert decrypted == data

    def test_different_ivs_different_ciphertext(self):
        key = derive_key('test-password')
        data = b'same data'
        iv1 = generate_iv()
        iv2 = generate_iv()
        enc1 = encrypt_data(data, key, iv1)
        enc2 = encrypt_data(data, key, iv2)
        assert enc1 != enc2

    def test_wrong_key_fails(self):
        key = derive_key('correct-password')
        iv = generate_iv()
        data = b'secret'
        encrypted = encrypt_data(data, key, iv)
        wrong_key = derive_key('wrong-password')
        # AES-CBC + unpad may or may not raise depending on garbage bytes.
        # Verify the decrypted data is NOT the original.
        try:
            decrypted = decrypt_data(encrypted, wrong_key, iv)
            assert decrypted != data, "Wrong key produced correct data — encryption broken!"
        except Exception:
            pass  # Raised (bad padding) — also acceptable

    def test_deterministic_with_same_iv(self):
        key = derive_key('test')
        iv = generate_iv()
        data = b'deterministic'
        enc1 = encrypt_data(data, key, iv)
        enc2 = encrypt_data(data, key, iv)
        assert enc1 == enc2


class TestFormatDetection:
    def test_get_format_ytv1(self):
        fmt = get_format('ytv1')
        assert fmt['name'] == 'YTV1'
        assert fmt['fps'] == 6

    def test_get_format_ytv2(self):
        fmt = get_format('ytv2')
        assert fmt['name'] == 'YTV2'
        assert fmt['fps'] == 15

    def test_get_format_invalid(self):
        with pytest.raises(ValueError):
            get_format('ytv3')

    def test_compute_grid_ytv1(self):
        g = compute_grid(YTV1)
        assert g['blocks_x'] == 62
        assert g['blocks_y'] == 46
        assert g['blocks_per_region'] == 2852

    def test_compute_grid_ytv2(self):
        g = compute_grid(YTV2)
        assert g['blocks_x'] == 209
        assert g['blocks_y'] == 116
        assert g['blocks_per_region'] == 24244

    def test_detect_format_80px(self):
        assert detect_format(80)['name'] == 'YTV1'

    def test_detect_format_16px(self):
        assert detect_format(16)['name'] == 'YTV2'


# ── Full encode/decode roundtrip ────────────────────────────────────────────

class TestEncodeDecodeRoundtrip:
    """Encode a small file to video, decode it back, verify correctness."""

    @pytest.fixture
    def tmp_dir(self):
        d = tempfile.mkdtemp(prefix='ytcloud_test_')
        yield d
        shutil.rmtree(d, ignore_errors=True)

    def _roundtrip(self, data: bytes, filename: str, format_name: str,
                    key: str = None, interlace: bool = False, tmp_dir: str = None):
        """Helper: write data → encode → decode → verify."""
        from encoder import YouTubeEncoder
        from decoder import YouTubeDecoder

        if tmp_dir is None:
            tmp_dir = tempfile.mkdtemp(prefix='ytcloud_rt_')

        # Write input file
        input_path = os.path.join(tmp_dir, filename)
        with open(input_path, 'wb') as f:
            f.write(data)

        output_video = os.path.join(tmp_dir, 'output.mp4')

        # Encode
        encoder = YouTubeEncoder(key=key, format_name=format_name, interlace=interlace)
        ok = encoder.encode(input_path, output_video)
        assert ok, "Encoder returned False"
        assert os.path.exists(output_video), "Video file not created"
        assert os.path.getsize(output_video) > 0, "Video file is empty"

        # Decode
        decode_dir = os.path.join(tmp_dir, 'decoded')
        os.makedirs(decode_dir)
        decoder = YouTubeDecoder(key=key, interlace=interlace)
        ok = decoder.decode(output_video, decode_dir)
        assert ok, "Decoder returned False"

        # Verify file exists
        restored_path = os.path.join(decode_dir, filename)
        assert os.path.exists(restored_path), f"Restored file not found: {restored_path}"

        # Verify content
        with open(restored_path, 'rb') as f:
            restored_data = f.read()
        assert restored_data == data, (
            f"Data mismatch! Original {len(data)} bytes, "
            f"restored {len(restored_data)} bytes"
        )

        return restored_path

    def test_small_text_no_encrypt(self, tmp_dir):
        data = b'Hello, YouTube-Cloude! This is a test file.'
        self._roundtrip(data, 'test.txt', 'ytv1', tmp_dir=tmp_dir)

    def test_small_binary_no_encrypt(self, tmp_dir):
        data = os.urandom(1024)
        self._roundtrip(data, 'random.bin', 'ytv1', tmp_dir=tmp_dir)

    def test_small_text_with_aes(self, tmp_dir):
        data = b'Secret data encrypted with AES-256-CBC!'
        self._roundtrip(data, 'secret.txt', 'ytv1', key='my-password', tmp_dir=tmp_dir)

    def test_small_text_with_interlace(self, tmp_dir):
        data = b'Interlaced frame test data'
        self._roundtrip(data, 'interlaced.txt', 'ytv1', interlace=True, tmp_dir=tmp_dir)

    def test_small_text_with_aes_and_interlace(self, tmp_dir):
        data = b'AES + interlace combined test'
        self._roundtrip(data, 'combined.txt', 'ytv1',
                        key='test-key', interlace=True, tmp_dir=tmp_dir)

    @pytest.mark.slow
    def test_ytv2_roundtrip(self, tmp_dir):
        data = b'YTV2 format roundtrip test'
        self._roundtrip(data, 'ytv2_test.txt', 'ytv2', tmp_dir=tmp_dir)

    @pytest.mark.slow
    def test_ytv2_with_aes(self, tmp_dir):
        data = b'YTV2 + AES encryption test'
        self._roundtrip(data, 'ytv2_aes.txt', 'ytv2', key='ytv2-key', tmp_dir=tmp_dir)

    def test_1KB_no_encrypt(self, tmp_dir):
        data = os.urandom(1024)
        self._roundtrip(data, '1kb.bin', 'ytv1', tmp_dir=tmp_dir)

    def test_wrong_key_gives_garbage(self, tmp_dir):
        """Encoding with key A, decoding with key B should NOT match."""
        from encoder import YouTubeEncoder
        from decoder import YouTubeDecoder

        data = b'Encrypted content'
        input_path = os.path.join(tmp_dir, 'enc.txt')
        with open(input_path, 'wb') as f:
            f.write(data)

        video = os.path.join(tmp_dir, 'enc.mp4')
        encoder = YouTubeEncoder(key='correct-key', format_name='ytv1')
        encoder.encode(input_path, video)

        decode_dir = os.path.join(tmp_dir, 'wrong_decode')
        os.makedirs(decode_dir)
        decoder = YouTubeDecoder(key='wrong-key')
        decoder.decode(video, decode_dir)

        restored = os.path.join(decode_dir, 'enc.txt')
        if os.path.exists(restored):
            with open(restored, 'rb') as f:
                restored_data = f.read()
            # With wrong key, data should be different (garbage)
            assert restored_data != data, "Wrong key produced correct data — encryption broken!"
