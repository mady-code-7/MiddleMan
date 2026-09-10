"""
test_app.py

Tests the Flask routes directly using Flask's test client (no real
sockets needed). Covers TC07 from Section 9 of PROJECT_PLAN.md, plus
route-level checks for the error paths already covered at the
compressor level in test_compressor.py.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as client:
        yield client


RELIABLE_TEST_URL = "https://raw.githubusercontent.com/torvalds/linux/master/README"


# TC07 -- Download endpoint serves correct file
def test_download_serves_correct_file(client):
    process_resp = client.post("/process", json={"url": RELIABLE_TEST_URL})
    assert process_resp.status_code == 200
    job_id = process_resp.get_json()["job_id"]

    download_resp = client.get(f"/download/{job_id}")
    assert download_resp.status_code == 200
    assert len(download_resp.data) == process_resp.get_json()["compressed_size"]


def test_download_missing_job_returns_404(client):
    resp = client.get("/download/nonexistent-job-id")
    assert resp.status_code == 404


def test_process_requires_url_or_file(client):
    resp = client.post("/process", json={})
    assert resp.status_code == 400
