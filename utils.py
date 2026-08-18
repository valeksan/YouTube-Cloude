#!/usr/bin/env python3
"""CLI helpers and argparse entry-point for YouTube File Storage.

Improvements based on work by @Hinderchik, @IvanSCP, and @sosatel30000.
See: https://github.com/Hinderchik/YouTube-Cloude-Fork
     https://github.com/IvanSCP/YouTube-Cloude
     https://github.com/sosatel30000/YouTube-Cloude
GUI concepts from @Maksim4081862.
"""
import argparse
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


def main() -> None:
    """CLI entry-point."""
    parser = argparse.ArgumentParser(
        prog='coder.py',
        description='YouTube File Storage (6 FPS) - encode files into video',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encode without encryption
  python coder.py encode file.zip output.mp4

  # Encode with key on command line
  python coder.py encode file.zip output.mp4 --key "mysecretpassword"

  # Encode with key from file
  python coder.py encode file.zip output.mp4 --key-file /path/to/key.txt

  # Decode with key on command line
  python coder.py decode output.mp4 --key "mysecretpassword"

  # Decode with key from file
  python coder.py decode output.mp4 --key-file /path/to/key.txt

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

    args = parser.parse_args()
    key = resolve_key(args)

    if args.command == 'encode':
        encoder = YouTubeEncoder(key)
        encoder.encode(args.input_file, args.output_file)

    elif args.command == 'decode':
        decoder = YouTubeDecoder(key)
        decoder.decode(args.video_file, args.output_dir)
