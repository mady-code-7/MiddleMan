"""
test_compressor.py

pytest suite for MiddleMan's core logic, matching the test case table
in Section 9 of PROJECT_PLAN.md exactly (TC01-TC07).

Run with:  pytest tests/ -v
Also runnable server-side via the /run-tests Flask route, which returns
the real pass/fail count to the frontend for the Testing & QA banner.
"""

import gzip
import io
import os
import sys
import zipfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compressor import (
    InvalidURLError,
    SourceTooLargeError,
    UnreachableSourceError,
    MAX_SOURCE_SIZE_BYTES,
    compress_bytes,
    is_valid_url,
    process_file_bytes,
    process_url,
)

# A small, reliably-reachable, highly compressible text file.
RELIABLE_TEST_URL = "https://raw.githubusercontent.com/torvalds/linux/master/README"


# TC01 -- Valid URL processed successfully
def test_valid_url_processed_successfully():
    result = process_url(RELIABLE_TEST_URL)
    assert result.original_size > 0
    assert result.compressed_size < result.original_size


# TC02 -- Compression actually reduces size (using a controlled local
# text buffer, so this test doesn't depend on network content changing)
def test_compression_reduces_size_for_compressible_data():
    text_data = ("MiddleMan compresses this text. " * 200).encode("utf-8")
    result = compress_bytes(text_data)
    assert result.compressed_size < result.original_size
    assert result.savings_percent > 0


# TC03 -- Invalid/malformed URL rejected
def test_invalid_url_rejected():
    assert is_valid_url("not-a-url") is False
    with pytest.raises(InvalidURLError):
        process_url("not-a-url")


# TC04 -- Unreachable source handled
def test_unreachable_source_handled():
    with pytest.raises(UnreachableSourceError):
        process_url("https://this-domain-absolutely-does-not-exist-12345.com/file.zip")


# TC05 -- Already-compressed file handled reasonably (does not error out)
def test_already_compressed_file_handled_without_error():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("test.txt", "some content" * 50)
    zip_bytes = buf.getvalue()

    result = process_file_bytes(zip_bytes)
    assert result.original_size == len(zip_bytes)
    assert result.compressed_size > 0  # no crash, produced *some* output


# TC06 -- Oversized file handled
def test_oversized_file_rejected():
    oversized_data = b"x" * (MAX_SOURCE_SIZE_BYTES + 1)
    with pytest.raises(SourceTooLargeError):
        process_file_bytes(oversized_data)


# TC07 -- Download endpoint serves correct file (covered at the Flask
# layer, not the compressor layer -- see test_app.py)
