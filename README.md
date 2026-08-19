<div align="center">

# 🎥 YouTube-Cloude

### Hide files in YouTube videos — steganographic file storage

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
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

- 🔐 **AES-256-CBC encryption** — optional key-based encryption (SHA-256 key derivation, random IV)
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
pip install -r requirements.txt
# Or manually:
pip install opencv-python numpy pycryptodome
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

# Override max file size (default: 100 MB for YTV1, 500 MB for YTV2)
python coder.py encode big.iso video.mp4 --max-size 200
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
| Max file (default) | 100 MB (~3.4h video) | 500 MB (~48 min video) |
| Max file (override) | `--max-size 200` | `--max-size 200` |

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

Files can be encrypted with AES-256-CBC before encoding:

```bash
# Key from command line
python coder.py encode file.zip video.mp4 --key "secret"

# Key from file (auto-loaded if key.txt exists next to coder.py)
echo "my-secret-key" > key.txt
python coder.py encode file.zip video.mp4
python coder.py decode video.mp4   # key.txt auto-detected
```

> ⚠️ **Warning:** Without the correct key, the decoded file will be garbage. The key is derived via SHA-256 and each encode generates a unique random IV.

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
3. Make your changes
4. Test: `python coder.py encode test.txt test.mp4 && python coder.py decode test.mp4`
5. Commit and push
6. Open a Pull Request

## License

**No license has been set by the original author or any contributor.** This project builds on unlicensed code, which means it is technically "All Rights Reserved" under copyright law.

If you are the original author ([@KorocheVolgin](https://github.com/KorocheVolgin)) or a contributor and would like to add an open-source license (e.g., MIT), please open an issue or contact me. Adding a license would benefit the entire community.

Until then, please respect the author's rights and use this code for personal/educational purposes only.

---

<div align="center">

**Keywords:** file hiding, steganography, YouTube storage, encode file to video, hide data in video, covert channel, video steganography, colour block encoding, file-in-video, YouTube cloud storage

</div>
