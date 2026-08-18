#!/usr/bin/env python3
"""YouTube video encoder — encodes arbitrary files into colour-block frames.

Improvements based on work by @Hinderchik, @IvanSCP, and @sosatel30000.
See: https://github.com/Hinderchik/YouTube-Cloude-Fork
     https://github.com/IvanSCP/YouTube-Cloude
     https://github.com/sosatel30000/YouTube-Cloude
"""
import cv2
import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Callable

import numpy as np

from core import (
    WIDTH, HEIGHT, COLORS, EOF_MARKER, EOF_BYTES,
    get_format, compute_grid, MAX_FILE_SIZES,
    encrypt_data, generate_iv, derive_key,
    data_to_blocks, sanitize_filename, validate_input_file,
    crc32_hex, interlace_frame,
)


class YouTubeEncoder:
    """Encode a file into a video of colour-block frames."""

    def __init__(self, key: Optional[str] = None,
                 format_name: str = 'ytv1',
                 interlace: bool = False,
                 max_file_size: Optional[int] = None) -> None:
        self.width = WIDTH
        self.height = HEIGHT
        self.max_file_size = max_file_size or MAX_FILE_SIZES.get(format_name, 100 * 1024 * 1024)
        self.interlace = interlace

        # Format-specific parameters
        fmt = get_format(format_name)
        g = compute_grid(fmt)
        self.fps = g['fps']
        self.block_height = g['block_height']
        self.block_width = g['block_width']
        self.spacing = g['spacing']
        self.marker_size = g['marker_size']
        self.blocks_x = g['blocks_x']
        self.blocks_y = g['blocks_y']
        self.blocks_per_region = g['blocks_per_region']
        self.blocks_per_frame = g['blocks_per_frame']
        self.format_name = g['name']

        if key and str(key).strip():
            self.key: Optional[bytes] = derive_key(str(key))
            self.use_encryption = True
        else:
            self.key = None
            self.use_encryption = False

        self.colors = COLORS
        self.eof_marker = EOF_MARKER
        self.eof_bytes = EOF_BYTES

        print("=" * 60)
        print(f"YouTube ENCODER ({self.format_name} | {self.fps} FPS)")
        print("=" * 60)
        print(f"  Grid: {self.blocks_x} x {self.blocks_y} blocks per region")
        print(f"  FPS:  {self.fps}")
        print(f"  Encryption: {'AES-256-CBC' if self.use_encryption else 'OFF'}")
        print(f"  Interlace:  {'ON' if self.interlace else 'OFF'}")
        print(f"  Max file:   {self.max_file_size / 1024 / 1024:.0f} MB")

    # ── Drawing helpers ─────────────────────────────────────────────────
    def draw_markers(self, frame: np.ndarray) -> np.ndarray:
        """Draw alignment markers in each corner."""
        for x, y in [
            (0, 0),
            (self.width - self.marker_size, 0),
            (0, self.height - self.marker_size),
            (self.width - self.marker_size, self.height - self.marker_size),
        ]:
            cv2.rectangle(
                frame,
                (x, y),
                (x + self.marker_size, y + self.marker_size),
                (255, 255, 255),
                -1,
            )
            cv2.rectangle(
                frame,
                (x, y),
                (x + self.marker_size, y + self.marker_size),
                (0, 0, 0),
                2,
            )
        return frame

    def draw_block(
        self,
        frame: np.ndarray,
        x: int,
        y: int,
        color: tuple,
    ) -> bool:
        """Draw a single colour block; return *True* if within bounds."""
        x1 = self.marker_size + x * (self.block_width + self.spacing)
        y1 = self.marker_size + y * (self.block_height + self.spacing)
        x2 = x1 + self.block_width
        y2 = y1 + self.block_height

        if x2 > self.width - self.marker_size or y2 > self.height - self.marker_size:
            return False

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 1)
        return True

    def bits_to_color(self, bits: str) -> tuple:
        """Map a 4-bit string to its palette colour."""
        while len(bits) < 4:
            bits = '0' + bits
        return self.colors.get(bits, (255, 0, 0))

    # ── Main encode routine ─────────────────────────────────────────────
    def encode(
        self,
        input_file: str,
        output_file: str = "output.mp4",
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> bool:
        """Encode *input_file* into *output_file* (MP4)."""

        print("\n  ENCODE FILE")
        print("-" * 40)

        try:
            input_path = validate_input_file(input_file, self.max_file_size)
        except (FileNotFoundError, ValueError) as e:
            print(f"  Error: {e}")
            return False

        original_filename = sanitize_filename(input_path.name)

        print(f"  File:   {original_filename}")
        print(f"  Size:   {input_path.stat().st_size} bytes")

        try:
            with open(input_path, 'rb') as f:
                data = f.read()
        except IOError as e:
            print(f"  Read error: {e}")
            return False

        if self.use_encryption:
            iv = generate_iv()
            encrypted_data = encrypt_data(data, self.key, iv)
            iv_hex = iv.hex()
            print("  Data encrypted (AES-256-CBC)")
        else:
            encrypted_data = data
            iv_hex = None

        # CRC32 of encrypted data for integrity check
        data_crc = crc32_hex(encrypted_data)

        # Header: FORMAT:YTV2:FILE:name:SIZE:123:ENC_SIZE:456:IV:hex...:CRC:abcdef12|
        if iv_hex:
            header = (
                f"FORMAT:{self.format_name}:FILE:{original_filename}:"
                f"SIZE:{len(data)}:ENC_SIZE:{len(encrypted_data)}:"
                f"IV:{iv_hex}:CRC:{data_crc}|"
            )
        else:
            header = f"FORMAT:{self.format_name}:FILE:{original_filename}:SIZE:{len(data)}:CRC:{data_crc}|"
        try:
            header_bytes = header.encode('latin-1')
        except UnicodeEncodeError:
            print("  Invalid characters in filename")
            return False
        print(f"  Header: {header}")

        header_blocks = data_to_blocks(header_bytes)
        data_blocks = data_to_blocks(encrypted_data)
        eof_blocks = data_to_blocks(self.eof_bytes)
        all_blocks = header_blocks + data_blocks + eof_blocks

        print(f"  Total blocks: {len(all_blocks)}")
        print(f"  EOF marker:   {len(eof_blocks)} blocks")

        frames_needed = math.ceil(len(all_blocks) / self.blocks_per_region) + 5
        print(f"  Frames needed: {frames_needed}")
        print(f"  Duration:      {frames_needed / self.fps:.1f} sec")

        temp_dir = tempfile.mkdtemp(prefix="youtube_encoder_")
        print(f"  Temp dir: {temp_dir}")

        try:
            for frame_num in range(frames_needed - 5):
                if progress_callback:
                    progress_callback(frame_num + 1, frames_needed)
                print(f"\n  Frame {frame_num + 1}/{frames_needed}")

                frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                frame = self.draw_markers(frame)

                start_idx = frame_num * self.blocks_per_region
                end_idx = min(start_idx + self.blocks_per_region, len(all_blocks))
                frame_blocks = all_blocks[start_idx:end_idx]

                # Primary region
                for idx, bits in enumerate(frame_blocks):
                    y = idx // self.blocks_x
                    x = idx % self.blocks_x
                    if y < self.blocks_y:
                        color = self.bits_to_color(bits)
                        self.draw_block(frame, x, y, color)

                # Reserve 1
                for idx, bits in enumerate(frame_blocks):
                    y = idx // self.blocks_x
                    x = idx % self.blocks_x + self.blocks_x
                    if x < self.blocks_x * 2 and y < self.blocks_y:
                        color = self.bits_to_color(bits)
                        self.draw_block(frame, x, y, color)

                # Reserve 2
                for idx, bits in enumerate(frame_blocks):
                    y = idx // self.blocks_x + self.blocks_y
                    x = idx % self.blocks_x
                    if x < self.blocks_x and y < self.blocks_y * 2:
                        color = self.bits_to_color(bits)
                        self.draw_block(frame, x, y, color)

                frame_file = os.path.join(temp_dir, f"frame_{frame_num:05d}.png")
                if self.interlace:
                    frame = interlace_frame(frame)
                cv2.imwrite(frame_file, frame)

            # Guard frames (blue)
            print("\n  Creating guard frames...")
            for i in range(5):
                frame_num = frames_needed - 5 + i
                frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                frame = self.draw_markers(frame)
                for y in range(self.blocks_y * 2):
                    for x in range(self.blocks_x * 2):
                        self.draw_block(frame, x, y, (255, 0, 0))
                frame_file = os.path.join(temp_dir, f"frame_{frame_num:05d}.png")
                cv2.imwrite(frame_file, frame)
                print(f"  Guard frame {i + 1}/5")

            # Convert to MP4
            print("\n  Converting to MP4...")
            try:
                subprocess.run(
                    ['ffmpeg', '-version'],
                    capture_output=True,
                    check=True,
                )
                cmd = [
                    'ffmpeg',
                    '-framerate', str(self.fps),
                    '-i', os.path.join(temp_dir, 'frame_%05d.png'),
                    '-c:v', 'libx264',
                    '-preset', 'slow',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-an',
                    '-movflags', '+faststart',
                    '-y',
                    output_file,
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                print("  FFmpeg conversion OK")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("  FFmpeg unavailable, falling back to OpenCV...")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(
                    output_file, fourcc, self.fps, (self.width, self.height)
                )
                for frame_num in range(frames_needed):
                    frame_file = os.path.join(
                        temp_dir, f"frame_{frame_num:05d}.png"
                    )
                    frame = cv2.imread(frame_file)
                    if frame is not None:
                        out.write(frame)
                out.release()

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            print("  Temp files cleaned up")

        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"\n  Video saved: {output_file}")
            print(f"  Size:        {size} bytes ({size / 1024 / 1024:.2f} MB)")
            print(f"  Frames:      {frames_needed}")
            print(f"  Duration:    {frames_needed / self.fps:.1f} sec")
            return True
        return False
