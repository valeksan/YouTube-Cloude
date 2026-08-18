<div align="center">

# 🎥 YouTube-Cloude

### Hide files in YouTube videos — steganographic file storage

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-optional-green)](https://ffmpeg.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
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

## Features

- 🔐 **XOR encryption** — optional key-based encryption (SHA-256 hashed)
- 🎞️ **Two formats** — YTV1 (standard) and YTV2 (21× denser)
- 📊 **CRC32 integrity** — automatic verification on decode
- 🔀 **Interlacing** — improved YouTube compression quality
- 🖥️ **GUI** — tkinter interface with dark theme
- 📦 **Batch mode** — encode entire directories at once
- 🗜️ **7z compression** — optional pre-encode compression
- 📤 **YouTube upload/download** — via yt-dlp and YouTube Data API v3

## Quick Start

### Install Dependencies

```bash
pip install opencv-python numpy
# Optional: FFmpeg for better video quality
sudo apt install ffmpeg    # Linux
brew install ffmpeg        # macOS
```

### Encode a File

```bash
# Basic encoding (YTV1 format)
python coder.py encode secret.zip video.mp4

# With encryption
python coder.py encode secret.zip video.mp4 --key "my-password"

# YTV2 format (21× denser, 15 FPS)
python coder.py encode secret.zip video.mp4 --format ytv2

# With interlacing (better YouTube quality)
python coder.py encode secret.zip video.mp4 --interlace
```

### Decode a Video

```bash
# Auto-detects format, interlacing, and CRC from the video
python coder.py decode video.mp4

# With decryption key
python coder.py decode video.mp4 --key "my-password"
```

### Batch Encode a Directory

```bash
python coder.py encode-dir ./my-data/ ./output/ --format ytv2 --interlace
```

### Launch GUI

```bash
python gui.py
```

## Format Comparison

| Property | YTV1 | YTV2 |
|----------|------|------|
| Block size | 24×16 px | 8×8 px |
| Spacing | 4 px | 1 px |
| Markers | 80 px | 16 px |
| Grid | 62×46 | 209×116 |
| Blocks/frame | 2,852 | 24,244 |
| FPS | 6 | 15 |
| **Density** | **1×** | **21.3×** |
| Max file | ~100 MB | ~100 MB |

## Project Structure

```
YouTube-Cloude/
├── coder.py        # CLI entry point (backward compatible)
├── core.py         # Constants, CRC32, interlacing, encryption
├── encoder.py      # YouTubeEncoder class
├── decoder.py      # YouTubeDecoder class (auto-detect format)
├── utils.py        # CLI helpers, argparse
├── gui.py          # Tkinter GUI (dark theme)
├── compress.py     # 7z compress/decompress
└── uploader.py     # YouTube upload (OAuth2) / download (yt-dlp)
```

## Encryption

You can encrypt files before encoding:

```bash
# Key from command line
python coder.py encode file.zip video.mp4 --key "secret"

# Key from file (auto-loaded if key.txt exists next to coder.py)
echo "my-secret-key" > key.txt
python coder.py encode file.zip video.mp4
python coder.py decode video.mp4   # key.txt auto-detected
```

> ⚠️ **Warning:** Without the correct key, the decoded file will be garbage. The key is hashed with SHA-256 before use.

## Credits

This project builds on the work of:

| Author | Contribution |
|--------|-------------|
| [**@KorocheVolgin**](https://github.com/KorocheVolgin) | Original concept and implementation |
| [**@Hinderchik**](https://github.com/Hinderchik) | Security hardening, code quality |
| [**@IvanSCP**](https://github.com/IvanSCP) | argparse CLI, key-file support |
| [**@sosatel30000**](https://github.com/sosatel30000) | YTV2 format, region sampling, progress callbacks |
| [**@Maksim4081862**](https://github.com/Maksim4081862) | GUI concepts, tkinter implementation |

## Related Projects

- [YouTube-Cloude (original)](https://github.com/KorocheVolgin/YouTube-Cloude) — @KorocheVolgin's original
- [YouTube-Cloude-Fork](https://github.com/Hinderchik/YouTube-Cloude-Fork) — @Hinderchik's security fork
- [YouTube-Cloude](https://github.com/IvanSCP/YouTube-Cloude) — @IvanSCP's CLI improvements
- [YouTube-Cloud-GUI](https://github.com/Maksim4081862/YouTube-Cloud-GUI) — @Maksim4081862's GUI

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Test: `python coder.py encode test.txt test.mp4 && python coder.py decode test.mp4`
5. Commit and push
6. Open a Pull Request

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Keywords:** file hiding, steganography, YouTube storage, encode file to video, hide data in video, covert channel, video steganography, colour block encoding, file-in-video, YouTube cloud storage

</div>
