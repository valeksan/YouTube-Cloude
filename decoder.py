#!/usr/bin/env python3
"""YouTube video decoder — extracts files from colour-block frame videos.

Improvements based on work by @Hinderchik, @IvanSCP, and @sosatel30000.
See: https://github.com/Hinderchik/YouTube-Cloude-Fork
     https://github.com/IvanSCP/YouTube-Cloude
     https://github.com/sosatel30000/YouTube-Cloude
"""
import cv2
import os
import re
from pathlib import Path
from typing import Optional, Callable

import numpy as np

from core import (
    WIDTH, HEIGHT, COLORS, EOF_BYTES,
    get_format, compute_grid, detect_format,
    decrypt_data, blocks_to_bytes, data_to_blocks,
    verify_crc32, deinterlace_frame,
)


class YouTubeDecoder:
    """Decode a colour-block video back into the original file."""

    def __init__(self, key: Optional[str] = None,
                 format_name: Optional[str] = None,
                 interlace: bool = False) -> None:
        self.width = WIDTH
        self.height = HEIGHT
        self.format_name = format_name  # None = auto-detect from video
        self._format_configured = False
        self.interlace = interlace

        import hashlib
        if key and str(key).strip():
            self.key: Optional[bytes] = hashlib.sha256(str(key).encode()).digest()
        else:
            self.key = None

        self.colors = COLORS
        self.color_values = np.array(list(self.colors.values()), dtype=np.int32)
        self.color_keys = list(self.colors.keys())
        self.color_cache: dict[tuple, str] = {}
        self.cache_hits = 0
        self.cache_misses = 0

        # If format known at init time, configure grid now
        if format_name:
            self._configure_format(get_format(format_name))

        print("=" * 60)
        if format_name:
            print(f"YouTube DECODER ({self.format_name})")
        else:
            print("YouTube DECODER (auto-detect)")
        print("=" * 60)
        if self._format_configured:
            print(f"  Grid:   {self.blocks_x} x {self.blocks_y} blocks")
        print(f"  Key:    {'YES' if self.key else 'NO'}")

    def _configure_format(self, fmt: dict) -> None:
        """Set grid parameters from a format dict."""
        g = compute_grid(fmt)
        self.format_name = g['name']
        self.block_height = g['block_height']
        self.block_width = g['block_width']
        self.spacing = g['spacing']
        self.marker_size = g['marker_size']
        self.blocks_x = g['blocks_x']
        self.blocks_y = g['blocks_y']
        self.blocks_per_region = g['blocks_per_region']
        self._precompute_coordinates()
        self._format_configured = True

    # ── Coordinate pre-computation ──────────────────────────────────────
    def _detect_marker_size(self, frame: np.ndarray) -> int:
        """Detect marker size from the top-left corner of the first frame.

        Scans along the top edge for the transition from white marker to black.
        """
        if frame.shape[1] != self.width or frame.shape[0] != self.height:
            frame = cv2.resize(
                frame, (self.width, self.height), interpolation=cv2.INTER_NEAREST
            )
        # Scan row y=marker_center, from x=0 rightward
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        center_y = 40  # sample row
        for x in range(10, min(200, self.width)):
            if gray[center_y, x] < 128:  # dark = end of white marker
                # Markers are square; check vertical too
                center_x = x // 2
                for y in range(10, min(200, self.height)):
                    if gray[y, center_x] < 128:
                        return x  # approximate marker size
        return 80  # fallback to YTV1

    def _precompute_coordinates(self) -> None:
        """Precompute centre pixel coordinates for every block."""
        self.block_coords: list[tuple[int, int]] = []
        for idx in range(self.blocks_per_region):
            y = idx // self.blocks_x
            x = idx % self.blocks_x
            if y < self.blocks_y:
                cx = (
                    self.marker_size
                    + x * (self.block_width + self.spacing)
                    + self.block_width // 2
                )
                cy = (
                    self.marker_size
                    + y * (self.block_height + self.spacing)
                    + self.block_height // 2
                )
                self.block_coords.append((cx, cy))

    # ── Fast colour lookup ──────────────────────────────────────────────
    def color_to_bits_fast(self, color: np.ndarray) -> str:
        """Map a BGR colour (np.ndarray) to its 4-bit string, using a cache."""
        color_key = (int(color[0]), int(color[1]), int(color[2]))

        if color_key in self.color_cache:
            self.cache_hits += 1
            return self.color_cache[color_key]

        self.cache_misses += 1

        # Quick path for dominant blue
        if color[0] > 200 and color[1] < 50 and color[2] < 50:
            self.color_cache[color_key] = '0000'
            return '0000'

        color_arr = np.array([color[0], color[1], color[2]], dtype=np.int32)
        distances = np.sum((self.color_values - color_arr) ** 2, axis=1)
        best_idx = int(np.argmin(distances))
        result = self.color_keys[best_idx]
        self.color_cache[color_key] = result
        return result

    # ── Frame decoding ──────────────────────────────────────────────────
    def decode_frame_fast(self, frame: np.ndarray) -> list[str]:
        """Decode one frame into 4-bit block strings (region-sampled)."""
        if frame.shape[1] != self.width or frame.shape[0] != self.height:
            frame = cv2.resize(
                frame,
                (self.width, self.height),
                interpolation=cv2.INTER_NEAREST,
            )
        if self.interlace:
            frame = deinterlace_frame(frame)

        blocks: list[str] = []
        h, w = frame.shape[:2]

        for cx, cy in self.block_coords:
            if cx < w and cy < h:
                x1, y1 = max(0, cx - 2), max(0, cy - 2)
                x2, y2 = min(w, cx + 3), min(h, cy + 3)
                region = frame[y1:y2, x1:x2]
                avg_color = region.mean(axis=(0, 1))
                bits = self.color_to_bits_fast(avg_color)
                blocks.append(bits)
            else:
                blocks.append('0000')

        return blocks

    # ── EOF detection ───────────────────────────────────────────────────
    @staticmethod
    def find_eof_marker(data: bytes) -> int:
        """Return the byte offset of the EOF marker, or -1 if absent."""
        eof_bytes = EOF_BYTES
        for i in range(len(data) - len(eof_bytes) + 1):
            if data[i:i + len(eof_bytes)] == eof_bytes:
                return i
        return -1

    # ── Main decode routine ─────────────────────────────────────────────
    def decode(
        self,
        video_file: str,
        output_dir: str = '.',
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> bool:
        """Decode *video_file* and write recovered file(s) into *output_dir*."""

        print("\n  DECODE VIDEO")
        print("-" * 40)

        if not Path(video_file).exists():
            print(f"  Error: file not found: {video_file}")
            return False

        cap = cv2.VideoCapture(video_file)
        if not cap.isOpened():
            print("  Error: could not open video")
            return False

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"  Frames:  {total_frames}")
        print(f"  FPS:     {fps}")
        print(f"  Size:    {width}x{height}")

        self.cache_hits = 0
        self.cache_misses = 0
        start_time = cv2.getTickCount()

        # If format not yet configured, detect from first frame's marker
        if not self._format_configured:
            ret, first_frame = cap.read()
            if ret:
                detected_ms = self._detect_marker_size(first_frame)
                print(f"  Detected marker size: {detected_ms}px")
                self._configure_format(detect_format(detected_ms))
                print(f"  Auto-detected format: {self.format_name}")
                print(f"  Grid: {self.blocks_x} x {self.blocks_y} blocks")
                # Seek back to frame 0
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                # Can't read first frame → default to YTV1
                self._configure_format(get_format('ytv1'))
                print("  Warning: cannot read first frame, defaulting to YTV1")

        all_blocks: list[str] = []
        frames_processed = 0

        for frame_num in range(total_frames):
            if progress_callback:
                progress_callback(frame_num + 1, total_frames)

            ret, frame = cap.read()
            if not ret:
                break

            frames_processed += 1

            if frame_num % 100 == 0:
                elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
                speed = frames_processed / elapsed if elapsed > 0 else 0
                total_cache = self.cache_hits + self.cache_misses
                cache_ratio = (
                    (self.cache_hits / total_cache * 100) if total_cache > 0 else 0
                )
                print(
                    f"  Progress: {frame_num}/{total_frames} | "
                    f"Speed: {speed:.1f} fps | "
                    f"Cache: {cache_ratio:.1f}%"
                )

            frame_blocks = self.decode_frame_fast(frame)
            all_blocks.extend(frame_blocks)

        cap.release()

        elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        print(f"\n  Stats: {len(all_blocks)} blocks in {elapsed:.1f}s")
        total_cache = self.cache_hits + self.cache_misses
        print(
            f"  Cache: {self.cache_hits} hits, {self.cache_misses} misses"
        )
        print(f"  Frames processed: {frames_processed}")

        bytes_data = blocks_to_bytes(all_blocks)
        print(f"  Bytes recovered: {len(bytes_data)}")

        eof_pos = self.find_eof_marker(bytes_data)
        if eof_pos > 0:
            bytes_data = bytes_data[:eof_pos]
            print(f"  EOF marker found at position {eof_pos}")
            print(f"  Bytes after trim: {len(bytes_data)}")
        else:
            print("  Warning: EOF marker not found")

        # Parse header — supports:
        #   New+ CRC: FORMAT:YTV2:FILE:name:SIZE:123:CRC:abcdef12|
        #   New:      FORMAT:YTV2:FILE:name:SIZE:123|
        #   Old:      FILE:name:SIZE:123|  (backward compat)
        data_str = bytes_data[:1000].decode('latin-1', errors='ignore')
        pattern_crc = r'FORMAT:([^:]+):FILE:([^:]+):SIZE:(\d+):CRC:([0-9a-fA-F]{8})\|'
        pattern_new = r'FORMAT:([^:]+):FILE:([^:]+):SIZE:(\d+)\|'
        pattern_old = r'FILE:([^:]+):SIZE:(\d+)\|'

        expected_crc: Optional[str] = None

        match = re.search(pattern_crc, data_str)
        if match:
            header_format = match.group(1)
            filename = match.group(2)
            filesize = int(match.group(3))
            expected_crc = match.group(4).lower()
            header_str = match.group(0)
            if not self._format_configured:
                try:
                    self._configure_format(get_format(header_format))
                    print(f"  Auto-detected format: {self.format_name}")
                except ValueError:
                    print(f"  Warning: unknown format '{header_format}', using defaults")
        else:
            match = re.search(pattern_new, data_str)
            if match:
                header_format = match.group(1)
                filename = match.group(2)
                filesize = int(match.group(3))
                header_str = match.group(0)
                if not self._format_configured:
                    try:
                        self._configure_format(get_format(header_format))
                        print(f"  Auto-detected format: {self.format_name}")
                    except ValueError:
                        print(f"  Warning: unknown format '{header_format}', using defaults")
            else:
                match = re.search(pattern_old, data_str)
                if match:
                    filename = match.group(1)
                    filesize = int(match.group(2))
                    header_str = match.group(0)
                    if not self._format_configured:
                        self._configure_format(get_format('ytv1'))
                        print("  Auto-detected format: YTV1 (legacy header)")
                else:
                    print("  Error: header not found")
                    output_path = os.path.join(output_dir, "decoded_data.bin")
                    with open(output_path, 'wb') as f:
                        f.write(bytes_data)
                    print(f"\n  Raw data saved: {output_path}")
                    return False

        print(f"\n  Header found: {filename}, size: {filesize} bytes")
        if expected_crc:
            print(f"  CRC32 expected: {expected_crc}")

        header_bytes_enc = header_str.encode('latin-1')
        header_pos = bytes_data.find(header_bytes_enc)

        if header_pos >= 0:
            encrypted_data = bytes_data[
                header_pos + len(header_bytes_enc):
                header_pos + len(header_bytes_enc) + filesize
            ]

            if self.key:
                file_data = decrypt_data(encrypted_data, self.key)
                print("  Data decrypted")
            else:
                file_data = encrypted_data
                print("  Warning: data not decrypted (no key)")

            output_path = os.path.join(output_dir, filename)
            counter = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(output_path):
                output_path = os.path.join(output_dir, f"{base}_{counter}{ext}")
                counter += 1

            with open(output_path, 'wb') as f:
                f.write(file_data)

            print(f"\n  File restored: {output_path}")
            print(f"  Size: {len(file_data)} bytes")

            if len(file_data) == filesize:
                print("  Size matches original")
            else:
                print(f"  Size mismatch: {len(file_data)} != {filesize}")

            if expected_crc:
                if verify_crc32(encrypted_data, expected_crc):
                    print("  CRC32 verified OK")
                else:
                    print(f"  WARNING: CRC32 MISMATCH — data may be corrupted!")

            return True

        # Fallback: save raw bytes
        output_path = os.path.join(output_dir, "decoded_data.bin")
        with open(output_path, 'wb') as f:
            f.write(bytes_data)
        print(f"\n  Raw data saved: {output_path}")
        return False
