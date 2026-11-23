#!/usr/bin/env python3
"""Entry point for the make.fun news-image-20261123 entry.

Copies the pre-rendered front page (entry.png, 1024x1024) into the output
directory the harness provides via MAKEFUN_OUTPUT_DIR.
Standard library only.
"""
import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024


def png_dimensions(path):
    """Read width/height from a PNG IHDR chunk (stdlib only)."""
    with open(path, "rb") as f:
        header = f.read(33)
    if header[:8] != PNG_MAGIC:
        raise ValueError(f"{path}: not a PNG file")
    if header[12:16] != b"IHDR":
        raise ValueError(f"{path}: missing IHDR chunk")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    width, height = png_dimensions(src)
    if (width, height) != (1024, 1024):
        print(f"entry.png is {width}x{height}, expected 1024x1024", file=sys.stderr)
        return 1
    size = os.path.getsize(src)
    if size > MAX_BYTES:
        print(f"entry.png is {size} bytes, over the 1 MiB limit", file=sys.stderr)
        return 1
    shutil.copyfile(src, dst)
    copied_size = os.path.getsize(dst)
    if copied_size != size:
        print(f"copy size mismatch: {copied_size} != {size}", file=sys.stderr)
        return 1
    print(f"copied {src} -> {dst}")
    print(f"entry.png: {width}x{height}, {size} bytes, sha256 {sha256_file(dst)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
