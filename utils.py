#!/usr/bin/env python3
"""CLI helpers and argparse entry-point for YouTube File Storage.

Improvements based on work by @Hinderchik, @IvanSCP, and @sosatel30000.
See: https://github.com/Hinderchik/YouTube-Cloude-Fork
     https://github.com/IvanSCP/YouTube-Cloude
     https://github.com/sosatel30000/YouTube-Cloude
GUI concepts from @Maksim4081862.
"""
import argparse
import os
import sys
from typing import Optional

from core import read_key_from_file
from encoder import YouTubeEncoder
from decoder import YouTubeDecoder


def resolve_key(args: argparse.Namespace) -> Optional[str]:
    """Determine encryption key by priority:
      1. --key TEXT
      2. --key-file PATH
      3. key.txt next to the script (legacy)
    """
    if args.key:
        print("Key from --key argument")
        return args.key

    if args.key_file:
        key = read_key_from_file(args.key_file)
        if key is None:
            print(f"Error: could not read key from: {args.key_file}")
            sys.exit(1)
        return key

    return read_key_from_file()


def add_key_args(subparser: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Add mutually-exclusive encryption key arguments to *subparser*."""
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        '--key',
        metavar='TEXT',
        help='Encryption key as a string',
    )
    group.add_argument(
        '--key-file',
        metavar='PATH',
        help='Path to a file containing the encryption key',
    )


def add_format_arg(subparser: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Add format selection argument to *subparser*."""
    subparser.add_argument(
        '--format',
        metavar='FMT',
        choices=['ytv1', 'ytv2'],
        default='ytv1',
        help='Video format: ytv1 (default, 6 FPS) or ytv2 (15 FPS, 21x denser)',
    )


def add_interlace_arg(subparser: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Add interlace flag to *subparser*."""
    subparser.add_argument(
        '--interlace',
        action='store_true',
        default=False,
        help='Interlace frames for better YouTube compression',
    )


def main() -> None:
    """CLI entry-point."""
    parser = argparse.ArgumentParser(
        prog='coder.py',
        description='YouTube File Storage - encode files into video',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encode without encryption (YTV1 default)
  python coder.py encode file.zip output.mp4

  # Encode in YTV2 format (21x denser, 15 FPS)
  python coder.py encode file.zip output.mp4 --format ytv2

  # Encode with interlacing for better YouTube compression
  python coder.py encode file.zip output.mp4 --interlace

  # Encode a whole directory (one video per file)
  python coder.py encode-dir ./mydata/ ./output/ --format ytv2 --interlace

  # Decode with auto-detect (format + interlace + CRC32)
  python coder.py decode output.mp4

  # If key.txt is next to the script, it is picked up automatically
  python coder.py decode output.mp4
        """,
    )

    subparsers = parser.add_subparsers(dest='command', metavar='COMMAND')
    subparsers.required = True

    # encode
    enc = subparsers.add_parser('encode', help='Encode a file into video')
    enc.add_argument(
        'input_file', metavar='FILE', help='Path to the file to encode'
    )
    enc.add_argument(
        'output_file',
        metavar='VIDEO',
        nargs='?',
        default='output.mp4',
        help='Output MP4 filename (default: output.mp4)',
    )
    add_key_args(enc)
    add_format_arg(enc)
    add_interlace_arg(enc)

    # encode-dir (batch mode)
    enc_dir = subparsers.add_parser(
        'encode-dir', help='Encode all files in a directory'
    )
    enc_dir.add_argument(
        'input_dir', metavar='DIR', help='Directory containing files to encode'
    )
    enc_dir.add_argument(
        'output_dir',
        metavar='OUTDIR',
        nargs='?',
        default='.',
        help='Output directory for MP4 files (default: current)',
    )
    add_key_args(enc_dir)
    add_format_arg(enc_dir)
    add_interlace_arg(enc_dir)

    # decode
    dec = subparsers.add_parser('decode', help='Decode a video back to a file')
    dec.add_argument(
        'video_file', metavar='VIDEO', help='Path to the MP4 to decode'
    )
    dec.add_argument(
        'output_dir',
        metavar='DIR',
        nargs='?',
        default='.',
        help='Output directory (default: current)',
    )
    add_key_args(dec)
    add_format_arg(dec)
    add_interlace_arg(dec)

    args = parser.parse_args()
    key = resolve_key(args)

    if args.command == 'encode':
        encoder = YouTubeEncoder(
            key, format_name=args.format, interlace=args.interlace,
        )
        encoder.encode(args.input_file, args.output_file)

    elif args.command == 'encode-dir':
        _encode_dir(args, key)

    elif args.command == 'decode':
        decoder = YouTubeDecoder(
            key, format_name=args.format, interlace=args.interlace,
        )
        decoder.decode(args.video_file, args.output_dir)


def _encode_dir(args: argparse.Namespace, key: Optional[str]) -> None:
    """Batch-encode all files in *args.input_dir*."""
    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.isdir(input_dir):
        print(f"Error: not a directory: {input_dir}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    files = sorted(
        f for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f))
    )
    if not files:
        print(f"No files found in {input_dir}")
        return

    print(f"Batch encode: {len(files)} file(s) from {input_dir} → {output_dir}")
    encoder = YouTubeEncoder(
        key, format_name=args.format, interlace=args.interlace,
    )

    ok_count = 0
    for i, fname in enumerate(files, 1):
        src = os.path.join(input_dir, fname)
        dst = os.path.join(output_dir, os.path.splitext(fname)[0] + '.mp4')
        print(f"\n--- [{i}/{len(files)}] {fname} ---")
        if encoder.encode(src, dst):
            ok_count += 1

    print(f"\n{'='*60}")
    print(f"Batch complete: {ok_count}/{len(files)} succeeded")
