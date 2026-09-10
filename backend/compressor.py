"""
compressor.py

Core logic for MiddleMan: fetch content (from a URL or an already-read
file's bytes), compress it, and report the before/after sizes.

Deliberately kept independent of Flask so it can be tested directly from
the command line, per Section 11 (Build Order) of PROJECT_PLAN.md:
"Test this from the command line before touching Flask."

Compression strategy:
- Uses gzip, since it works uniformly on any byte stream (text, binary,
  already-uploaded file bytes) without needing to know the file type.
- Already-compressed formats (zip, jpg, mp4, etc.) will compress poorly
  or barely at all with gzip -- this is expected and handled gracefully
  (see TC05 in PROJECT_PLAN.md Section 9), not treated as an error.
"""

import gzip
import io
import os
from dataclasses import dataclass

import requests


# --- Configuration -----------------------------------------------------

# Matches TC06 in PROJECT_PLAN.md Section 9 ("Oversized file handled").
# 50 MB is a reasonable ceiling for a solo-built demo project.
MAX_SOURCE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

# How long to wait for the source server to respond, in seconds.
FETCH_TIMEOUT_SECONDS = 15


# --- Exceptions ----------------------------------------------------------

class InvalidURLError(ValueError):
    """Raised when the given URL is malformed. Maps to TC03."""


class UnreachableSourceError(RuntimeError):
    """Raised when the URL is well-formed but the source can't be reached.
    Maps to TC04."""


class SourceTooLargeError(RuntimeError):
    """Raised when the source content exceeds MAX_SOURCE_SIZE_BYTES.
    Maps to TC06."""


# --- Result type -----------------------------------------------------

@dataclass
class CompressionResult:
    original_size: int
    compressed_size: int
    compressed_data: bytes

    @property
    def savings_percent(self) -> float:
        if self.original_size == 0:
            return 0.0
        saved = self.original_size - self.compressed_size
        return round((saved / self.original_size) * 100, 1)


# --- Core functions -----------------------------------------------------

def is_valid_url(url: str) -> bool:
    """Basic well-formedness check: must have an http/https scheme and a
    network location. Not a guarantee the URL is reachable -- just that
    it's shaped like a URL. Maps to TC03."""
    if not isinstance(url, str) or not url.strip():
        return False
    parsed = requests.utils.urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def fetch_from_url(url: str) -> bytes:
    """Fetch content from a URL using the server's fast connection.
    Raises InvalidURLError, UnreachableSourceError, or SourceTooLargeError
    as appropriate -- never lets a raw exception escape uncaught."""
    if not is_valid_url(url):
        raise InvalidURLError(f"'{url}' is not a valid http/https URL.")

    try:
        response = requests.get(url, timeout=FETCH_TIMEOUT_SECONDS, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise UnreachableSourceError(
            f"Could not reach '{url}': {exc}"
        ) from exc

    # Check declared size up front if the server tells us.
    declared_size = response.headers.get("Content-Length")
    if declared_size is not None and int(declared_size) > MAX_SOURCE_SIZE_BYTES:
        raise SourceTooLargeError(
            f"Source reports {int(declared_size)} bytes, "
            f"exceeding the {MAX_SOURCE_SIZE_BYTES}-byte limit."
        )

    # Stream and enforce the limit even if Content-Length was missing/wrong.
    buffer = io.BytesIO()
    total = 0
    for chunk in response.iter_content(chunk_size=8192):
        total += len(chunk)
        if total > MAX_SOURCE_SIZE_BYTES:
            raise SourceTooLargeError(
                f"Source exceeded the {MAX_SOURCE_SIZE_BYTES}-byte limit "
                f"while downloading."
            )
        buffer.write(chunk)

    return buffer.getvalue()


def compress_bytes(data: bytes) -> CompressionResult:
    """Compress raw bytes with gzip and report the size comparison.
    Works the same whether `data` came from a URL fetch or an uploaded
    file -- this function doesn't care about the source."""
    original_size = len(data)
    compressed_data = gzip.compress(data)
    compressed_size = len(compressed_data)

    return CompressionResult(
        original_size=original_size,
        compressed_size=compressed_size,
        compressed_data=compressed_data,
    )


def process_url(url: str) -> CompressionResult:
    """End-to-end: fetch a URL, then compress the result.
    This is the function backend/app.py will call from the /process route."""
    data = fetch_from_url(url)
    return compress_bytes(data)


def process_file_bytes(data: bytes) -> CompressionResult:
    """End-to-end for an already-uploaded file: just compress it.
    Still runs through the same size check as URL fetches, so an
    oversized upload is rejected the same way as an oversized URL fetch."""
    if len(data) > MAX_SOURCE_SIZE_BYTES:
        raise SourceTooLargeError(
            f"Uploaded file is {len(data)} bytes, "
            f"exceeding the {MAX_SOURCE_SIZE_BYTES}-byte limit."
        )
    return compress_bytes(data)


# --- Command-line test entry point -----------------------------------

def _human_readable(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python compressor.py <url>")
        sys.exit(1)

    test_url = sys.argv[1]
    print(f"Fetching: {test_url}")

    try:
        result = process_url(test_url)
    except (InvalidURLError, UnreachableSourceError, SourceTooLargeError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"Original size:   {_human_readable(result.original_size)}")
    print(f"Compressed size: {_human_readable(result.compressed_size)}")
    print(f"Savings:         {result.savings_percent}%")
