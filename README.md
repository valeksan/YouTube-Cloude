<div align="center">

# 🎥 YouTube-Cloude

### Hide files in YouTube videos — steganographic file storage

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-orange)](https://ffmpeg.org/)
[![License](https://img.shields.io/badge/License-None%20(yet)-red)](#license)
[![Tests](https://github.com/valeksan/YouTube-Cloude/actions/workflows/test.yml/badge.svg)](https://github.com/valeksan/YouTube-Cloude/actions/workflows/test.yml)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()

*Encode any file into a video of colour-block frames, upload to YouTube, and download it back — even if YouTube re-encodes the video.*

</div>

---

## How It Works

```
File → [Encoder] → Coloured blocks in video frames → YouTube
YouTube → [Decoder] → Coloured blocks → Original file
```

Each 4-bit chunk of your file is mapped to one of 16 colours and drawn as a block on a 1920×1080 frame. Three redundant copies per frame survive YouTube's compression. An end-of-file marker and header with filename/size ensure reliable recovery.

## ⚠️ Risks and Disclaimer

### Educational and Research Purpose

This project is an **educational and research tool** designed to demonstrate steganographic techniques and highlight the resilience of lossy video compression against data embedding. It is **not intended for production use or any activity that may violate applicable laws or terms of service.**

### How This Differs from an Attack

This project does **not** cause direct harm to YouTube or its users:

- It does **not** damage platform infrastructure, servers, or data
- It does **not** disrupt the service for other users
- It does **not** bypass security controls, access controls, or authentication
- It does **not** distribute malware, spam, or harmful content

The concern is **misuse of service** — YouTube is designed for sharing video content with viewers, not for covert data storage. Using it as a "cloud drive" via steganography falls outside the platform's intended purpose.

### YouTube Terms of Service

Uploading steganographic content to YouTube may be considered a misuse of the platform under [YouTube's Terms of Service](https://www.youtube.com/t/terms):

- **Section 5, paragraph 1:** YouTube is a platform for sharing video content with an audience, not for data storage or covert communication.
- **Section 5, paragraph 5:** Using the service in a manner not intended by its design may result in content removal or account restrictions.

YouTube's automated processing systems may detect and remove content that doesn't align with the platform's purpose. Accounts uploading such content may face restrictions, suspension, or termination.

### Legal Considerations

- **Unauthorised data concealment** may be interpreted as misuse of computer services in certain jurisdictions (e.g., [Computer Misuse Act 1990](https://www.legislation.gov.uk/ukpga/1990/18/contents) in the UK, [18 U.S.C. § 1030](https://www.law.cornell.edu/uscode/text/18/1030) in the US).
- **Breach of platform ToS** may result in civil liability or account termination.
- **Data uploaded to third-party platforms** may be subject to the platform's data retention, monitoring, and disclosure policies.

### Responsible Disclosure

This project was created to **highlight the resilience of steganographic methods against lossy video compression** — a known property of video codecs that has implications for content processing pipelines. The author advocates for:

- **Responsible disclosure** of potential misuse vectors to affected platforms
- **Educational use** to help security researchers understand steganographic techniques
- **Improving platform defences** through awareness of these methods

### No Warranty

This software is provided **"as is"** without warranty of any kind. The authors and contributors are not responsible for any misuse of this software. Users are solely responsible for ensuring that their use complies with all applicable laws, regulations, and platform terms of service.

**By using this software, you acknowledge that you have read this disclaimer and agree to use the software only for lawful, educational, and research purposes.**

## Features

- 🔐 **AES-256-GCM encryption** — PBKDF2-HMAC-SHA256 (200k iters) + random salt/nonce/tag, legacy CBC still decodes
- 🎞️ **Three formats** — YTV1 (standard), YTV2 (21× denser), **YTV3** (30 FPS, RS + luma, yuv420p-resilient)
- 📊 **Reed-Solomon + CRC32** — RS(255,223) corrects 16 byte errors/chunk (YTV3) + CRC32 on all formats
- 🔀 **Interlacing** — improved YouTube retention (YTV1/YTV2, ignored for YTV3)
- 🗜️ **zlib compression** — `--compress` before encoding, auto-skipped if would enlarge
- 🖥️ **GUI** — PySide6 (Qt) primary, unified `gui_service` layer; Tkinter deprecated, Kivy for Android
- 📱 **Android** — Buildozer APK (arm64, API 33), Kivy GUI
- 📦 **Batch mode** — encode entire directories at once
- 📤 **YouTube upload/download** — via yt-dlp and YouTube Data API v3

## Quick Start

### Install Dependencies

```bash
# Using Makefile (creates .venv/ automatically)
make setup         # runtime only
make setup-dev     # + pytest for development

# Or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Required: FFmpeg (install separately, not included in pip)
sudo apt install ffmpeg    # Linux
brew install ffmpeg        # macOS
```

### Encode a File

```bash
# Basic encoding (YTV1 format)
youtube-cloude encode secret.zip video.mp4

# With encryption (PBKDF2 + AES-GCM)
youtube-cloude encode secret.zip video.mp4 --key "my-password"

# YTV2 format (21× denser, 15 FPS)
youtube-cloude encode secret.zip video.mp4 --format ytv2

# YTV3 format (30 FPS, RS + grayscale luma — best for YouTube, no interlace needed)
youtube-cloude encode secret.zip video.mp4 --format ytv3

# With compression (zlib, auto-skipped if would enlarge)
youtube-cloude encode secret.zip video.mp4 --compress

# YTV3 + GCM + compress (recommended for text/logs)
youtube-cloude encode secret.zip video.mp4 --format ytv3 --key "my-password" --compress

# With interlacing (YTV1/YTV2 only, better YouTube quality)
youtube-cloude encode secret.zip video.mp4 --interlace

# Override max file size (default: 100 MB YTV1, 500 MB YTV2/YTV3)
youtube-cloude encode big.iso video.mp4 --max-size 200

# Or via Makefile
make run CMD="encode secret.zip video.mp4"
```

### Decode a Video

```bash
# Auto-detects format, interlacing, RS, compression and CRC from the video
youtube-cloude decode video.mp4

# With decryption key (PBKDF2 + GCM, legacy CBC also supported)
youtube-cloude decode video.mp4 --key "my-password"
```

### Batch Encode a Directory

```bash
youtube-cloude encode-dir ./my-data/ ./output/ --format ytv3 --compress
```

### Launch GUI

```bash
# PySide6 (Qt) — recommended, responsive layout
youtube-cloude-gui-qt
make gui-qt

# Tkinter — legacy, simpler
youtube-cloude-gui
make gui
```
```

### Windows SmartScreen

The `.exe` files in Releases are **unsigned** (no paid code-signing certificate). On first launch Windows may show:

> **"Windows protected your PC" / "SmartScreen prevented an unrecognized app"**

Click `More info` → `Run anyway` to start. Alternative: right-click the `.exe` → `Properties` → check `Unblock`, or in PowerShell:

```powershell
Unblock-File .\youtube-cloude-gui-*.exe
# or for all downloads
Get-ChildItem -Recurse | Unblock-File
```

The warning disappears after the file gains reputation (enough installs without detections). Future signed builds will not show this.

### Build Standalone Binaries

```bash
make build          # CLI binary via PyInstaller
make build-gui      # GUI app via PyInstaller (--windowed, no console)
make build-nuitka   # CLI binary via Nuitka (alternative)
# Output: dist/youtube-cloude  or  dist/youtube-cloude-gui
```

### Run Tests

```bash
make test           # full suite
make test-fast      # stop on first failure
```

## Format Comparison

| Property | YTV1 | YTV2 | **YTV3** |
|----------|------|------|----------|
| Block size | 24×16 px | 8×8 px | 8×8 px |
| Spacing | 4 px | 1 px | 2 px |
| Markers | 80 px | 16 px | 16 px |
| Grid | 62×46 | 209×116 | 188×104 |
| Blocks/frame | 2,852 | 24,244 | 19,552 |
| FPS | 6 | 15 | **30** |
| Palette | 16 colours (4 bit) | 16 colours (4 bit) | **4 grays (2 bit luma)** |
| ECC | none | 3× replication | **RS(255,223)** |
| **Density** | **1×** | **21.3×** | **~16× + RS** |
| yuv420p safe | No (needs interlace) | No (needs interlace) | **Yes** |
| Max file (default) | 100 MB (~3.4h) | 500 MB (~48 min) | 500 MB (~32 min) |
| Max file (override) | `--max-size 200` | `--max-size 200` | `--max-size 200` |

## Benchmark

**Test system (2026-08-31):** AMD Ryzen 3 PRO 4350G (4C/8T, 3.8 GHz), 28 GB RAM, Windows 11, Python 3.13, FFmpeg N-111283, `benchmark_input.png` 550 KB (800×600 geometric + 80k noise pixels). All variants verified with MD5 — **12/12 passed**.

| Variant | Encode | Decode | Video Size | Overhead | Verified |
|---------|--------|--------|------------|----------|----------|
| YTV1 | 45.8s | 13.4s | 45.8 MB | 85.2× | YES |
| YTV1 + AES | 45.0s | 13.5s | 45.8 MB | 85.2× | YES |
| YTV1 + interlace | 39.5s | 13.9s | 367.7 MB | 684.3× | YES |
| YTV1 + interlace + AES | 39.0s | 14.7s | 368.5 MB | 685.8× | YES |
| YTV2 | 18.0s | 13.8s | 17.9 MB | 33.2× | YES |
| YTV2 + AES | 18.2s | 13.8s | 17.9 MB | 33.3× | YES |
| YTV2 + interlace | 15.4s | 10.7s | 137.3 MB | 255.5× | YES |
| YTV2 + interlace + AES | 16.3s | 12.1s | 137.6 MB | 256.2× | YES |
| **YTV3** | 32.6s | 26.4s | 21.0 MB | 39.1× | YES |
| **YTV3 + AES** | 32.0s | 26.4s | 21.0 MB | 39.0× | YES |
| **YTV3 + compress** | 31.8s | 26.2s | 21.0 MB | 39.1× | YES |
| **YTV3 + compress + AES** | 31.9s | 26.4s | 21.0 MB | 39.0× | YES |

*Previous system (2026-08-21):* Ryzen 5 1600, 16 GB, Linux 6.12 — YTV1 33.8s/36 MB, YTV2 16.0s/18.5 MB (513 KB input).

### Key Findings

- **YTV2 is 2.5× faster to encode** than YTV1 (18s vs 46s, fewer frames: 52 vs 79)
- **YTV2 produces 2.5× smaller video** (17.9 MB vs 45.8 MB) — highest density
- **YTV3** trades density for resilience: 21 MB (39×) vs YTV2 17.9 MB (33×) but **yuv420p-safe without interlace** + RS(255,223) corrects 16 byte errors/chunk
- **AES-GCM + PBKDF2 adds <1s overhead** — negligible vs AES-CBC SHA256
- **Interlace produces 15× larger files** (yuv444p CRF 0) — YTV3 avoids this entirely
- **Compress** (`--compress` zlib) on this incompressible PNG shows no gain (as expected); on text/logs yields 100–200× reduction (see §Compression)

## How Interlace Works

### The Pipeline

```
Interlace кодирование:     YouTube:              Скачанное:
┌─────────────────┐   ┌──────────────────┐   ┌──────────────┐
│ 365 MB lossless │ → │ Re-encode H.264  │ → │ ~5-10 MB     │
│ yuv444p CRF 0   │   │ yuv420p CRF ~23  │   │ yuv420p      │
└─────────────────┘   └──────────────────┘   └──────────────┘
                                              ↓ deinterlace
                                         ┌──────────────┐
                                         │ Файл идентичен│
                                         │ оригиналу!    │
                                         └──────────────┘
```

YouTube **убивает** lossless и yuv444p — оставляет lossy H.264. Но данные внутри блоков переживают, потому что interlace уже "спрятал" их между строками. Кодек видит "шумную" картинку и сохраняет detail. При скачивании — deinterlace, и блоки на месте.

### The Problem

YouTube re-encodes every uploaded video with H.264. This codec uses **chroma subsampling (yuv420p)** which halves vertical color resolution. For our coloured blocks this is catastrophic — the encoder sees sharp colour transitions and "smooths" them, destroying the block data.

```
Original blocks:     After yuv420p subsampling:
┌───┬───┬───┐        ┌───┬───┬───┐
│RED│GRN│BLU│   →    │RED│GRN│BLU│  ← looks ok...
├───┼───┼───┤        ├───┼───┼───┤
│BLU│RED│GRN│        │???│???│???│  ← colors blend together
└───┴───┴───┘        └───┴───┴───┘
```

Adjacent rows with different colours get merged by the encoder — it doesn't know those colours are "important data" and treats them as noise to compress.

### The Solution: Interlace

**Before encoding**, we interlace the frame — interleave rows from the top and bottom halves:

```
Original:              After interlace:
Row 0: ██ RED ██       Row 0: ██ RED ██     (from top half)
Row 1: ██ GRN ██       Row 1: ██ BLU ██     (from bottom half)
Row 2: ██ BLU ██       Row 2: ██ GRN ██     (from top half)
Row 3: ██ RED ██       Row 3: ██ RED ██     (from bottom half)
Row 4: ██ GRN ██       Row 4: ██ GRN ██     (from top half)
Row 5: ██ BLU ██       Row 5: ██ GRN ██     (from bottom half)
```

Now adjacent rows are **spatially distant** in the original image. H.264's motion compensation and DCT transforms can't correlate them — the codec treats the frame as "noisy" and preserves more detail. After YouTube re-encodes and downloads, we **deinterlace** to restore the original layout.

### Why the File is 20× Larger

Interlace requires **lossless encoding** (CRF 0) to preserve the exact block colours. Lossless H.264 with **yuv444p** (full chroma resolution) produces massive files — but it's the only way to guarantee the blocks survive YouTube's processing pipeline.

### When to Use Interlace

| Scenario | Use Interlace? |
|----------|---------------|
| Local storage / backup | No — wastes space |
| Upload to YouTube | **Yes** — blocks survive re-encoding |
| Testing locally | No — not needed |
| Research / demos | Optional — for completeness |

## Project Structure

```
YouTube-Cloude/
├── src/youtube_cloude/
│   ├── __init__.py      # Package version (1.1.0)
│   ├── __main__.py      # CLI entry point (python -m youtube_cloude)
│   ├── cli.py           # PyInstaller CLI entry (absolute imports)
│   ├── core.py          # Constants, CRC32, interlacing, RS, encryption (PBKDF2+GCM)
│   ├── encoder.py       # YouTubeEncoder class (YTV3, compress)
│   ├── decoder.py       # YouTubeDecoder class (auto-detect YTV3, RS, GCM)
│   ├── utils.py         # CLI helpers, argparse (--compress)
│   ├── gui_service.py   # Shared service layer (unified GUI logic)
│   ├── gui.py           # Tkinter GUI (deprecated, use Qt)
│   ├── gui_cli.py       # Tkinter entry for PyInstaller
│   ├── gui_qt.py        # PySide6 GUI (responsive, dark theme, primary)
│   ├── gui_qt_cli.py    # PySide6 entry for PyInstaller
│   ├── compress.py      # 7z compress/decompress (legacy)
│   └── uploader.py      # YouTube upload (OAuth2) / download (yt-dlp)
├── tests/
│   └── test_encoder.py  # 36 tests (unit + YouTube re-encoding simulation)
├── .github/workflows/
│   ├── test.yml         # CI: test on push/PR
│   └── release.yml      # CI: build all platforms on tag push
├── pyproject.toml       # PEP 621 metadata, deps, entry points
├── Makefile             # venv, install, run, build, test, clean
└── README.md
```

## Encryption

Files can be encrypted with **AES-256-GCM** (PBKDF2-HMAC-SHA256, 200k iters) before encoding — legacy `AES-CBC` files still decode:

```bash
# Key from command line
youtube-cloude encode file.zip video.mp4 --key "secret"

# Key from file (auto-loaded if key.txt exists)
echo "my-secret-key" > key.txt
youtube-cloude encode file.zip video.mp4
youtube-cloude decode video.mp4   # key.txt auto-detected
```

> ℹ️ New files use `SALT:NONCE:TAG` (GCM); old `IV` (CBC) files auto-fallback. Wrong key fails with `MAC check failed`.

## Compression

Optional zlib compression before encoding (auto-skipped if would enlarge):

```bash
youtube-cloude encode big.log video.mp4 --compress
youtube-cloude encode big.log video.mp4 --format ytv3 --compress --key "secret"
```

Header carries `:COMPRESS:zlib` and the decoder decompresses transparently.

## Credits

This project builds on the work of:

| Author | Contribution |
|--------|-------------|
| [**@KorocheVolgin**](https://github.com/KorocheVolgin) | Original concept and implementation |
| [**@Hinderchik**](https://github.com/Hinderchik) | Security hardening, code quality |
| [**@IvanSCP**](https://github.com/IvanSCP) | argparse CLI, key-file support |
| [**@sosatel30000**](https://github.com/sosatel30000) | YTV2 format, region sampling, progress callbacks |
| [**@Maksim4081862**](https://github.com/Maksim4081862) | GUI concepts, tkinter implementation |
| [**@Verdgil**](https://github.com/Verdgil) | AES-256-CBC encryption (PR [#10](https://github.com/KorocheVolgin/YouTube-Cloude/pull/10)) |

## Related Projects

- [YouTube-Cloude (original)](https://github.com/KorocheVolgin/YouTube-Cloude) — @KorocheVolgin's original
- [YouTube-Cloude-Fork](https://github.com/Hinderchik/YouTube-Cloude-Fork) — @Hinderchik's security fork
- [YouTube-Cloude](https://github.com/IvanSCP/YouTube-Cloude) — @IvanSCP's CLI improvements
- [YouTube-Cloud-GUI](https://github.com/Maksim4081862/YouTube-Cloud-GUI) — @Maksim4081862's GUI

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Set up dev environment: `make setup-dev`
4. Make your changes
5. Test: `make test`
6. Commit and push
7. Open a Pull Request

## License

**No license has been set by the original author or any contributor.** This project builds on unlicensed code, which means it is technically "All Rights Reserved" under copyright law.

If you are the original author ([@KorocheVolgin](https://github.com/KorocheVolgin)) or a contributor and would like to add an open-source license (e.g., MIT), please open an issue or contact me. Adding a license would benefit the entire community.

Until then, please respect the author's rights and use this code for personal/educational purposes only.

---

<div align="center">

**Keywords:** file hiding, steganography, YouTube storage, encode file to video, hide data in video, covert channel, video steganography, colour block encoding, file-in-video, YouTube cloud storage

</div>
