"""
app.py

Flask backend for MiddleMan. Wraps compressor.py's fetch-and-compress
logic in HTTP routes, per Section 8 of PROJECT_PLAN.md:

    /              GET         Serves a simple status message
    /process       POST        Accepts a URL or uploaded file, returns job info
    /download/<id> GET         Serves the compressed file for a completed job
    /run-tests     GET/POST    Runs the pytest suite, returns real pass/fail JSON

CORS is enabled so the React frontend (a separate Render Static Site,
on its own domain) can call this API.
"""

import os
import subprocess
import sys

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

import database
from compressor import (
    InvalidURLError,
    SourceTooLargeError,
    UnreachableSourceError,
    process_file_bytes,
    process_url,
)

app = Flask(__name__)
CORS(app)

COMPRESSED_FILES_DIR = "compressed_files"
os.makedirs(COMPRESSED_FILES_DIR, exist_ok=True)

database.init_db()


@app.route("/")
def index():
    return jsonify({"status": "ok", "service": "MiddleMan backend"})


@app.route("/process", methods=["POST"])
def process():
    """
    Accepts either:
      - JSON body: {"url": "https://..."}
      - multipart/form-data with a "file" field

    Returns on success (200):
      {
        "job_id": "...",
        "original_size": 12345,
        "compressed_size": 4321,
        "savings_percent": 65.0
      }

    Returns on failure (400): {"error": "..."}
    """
    uploaded_file = request.files.get("file")
    url = None
    if uploaded_file is None:
        body = request.get_json(silent=True) or {}
        url = body.get("url")

    if uploaded_file is None and not url:
        return jsonify({"error": "Provide either a 'url' field or a 'file' upload."}), 400

    source_type = "file" if uploaded_file else "url"
    job_id = database.create_job(source_type)

    try:
        if uploaded_file:
            data = uploaded_file.read()
            result = process_file_bytes(data)
        else:
            result = process_url(url)
    except (InvalidURLError, SourceTooLargeError) as exc:
        # Client-side mistakes: bad input shape, or the file is too big.
        database.mark_job_failed(job_id, str(exc))
        return jsonify({"error": str(exc)}), 400
    except UnreachableSourceError as exc:
        # Server-side reachability problem, but still not our bug -- 400 is
        # appropriate since it's the *source* that's the problem, not us.
        database.mark_job_failed(job_id, str(exc))
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # noqa: BLE001 -- last-resort safety net for a live demo
        database.mark_job_failed(job_id, "Unexpected server error.")
        return jsonify({"error": "Unexpected server error. Please try again."}), 500

    compressed_path = os.path.join(COMPRESSED_FILES_DIR, f"{job_id}.gz")
    with open(compressed_path, "wb") as f:
        f.write(result.compressed_data)

    database.mark_job_success(
        job_id, result.original_size, result.compressed_size, compressed_path
    )

    return jsonify(
        {
            "job_id": job_id,
            "original_size": result.original_size,
            "compressed_size": result.compressed_size,
            "savings_percent": result.savings_percent,
        }
    )


@app.route("/download/<job_id>", methods=["GET"])
def download(job_id):
    job = database.get_job(job_id)

    if job is None:
        return jsonify({"error": "No job found with that ID."}), 404

    if job["status"] != "done":
        return jsonify({"error": f"Job is not ready (status: {job['status']})."}), 400

    if not job["compressed_path"] or not os.path.exists(job["compressed_path"]):
        return jsonify({"error": "Compressed file is missing on the server."}), 500

    return send_file(
        job["compressed_path"],
        as_attachment=True,
        download_name=f"middleman-{job_id}.gz",
    )


@app.route("/run-tests", methods=["GET", "POST"])
def run_tests():
    """
    Runs the pytest suite server-side and returns real pass/fail counts.
    This backs the Testing & QA banner (Section 4.3) -- the count shown
    to the user must always come from an actual pytest run, never a
    hardcoded number.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--tb=no", "-q"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    output = result.stdout + result.stderr
    passed, total = _parse_pytest_summary(output)

    return jsonify(
        {
            "passed": passed,
            "total": total,
            "raw_output": output,
        }
    )


def _parse_pytest_summary(output: str):
    """Parses pytest's final summary line (e.g. '5 passed in 0.42s' or
    '3 passed, 2 failed in 0.50s') into (passed, total) counts."""
    passed = 0
    failed = 0
    for line in output.splitlines():
        line = line.strip()
        if " passed" in line or " failed" in line:
            parts = line.replace(",", "").split()
            for i, word in enumerate(parts):
                if word == "passed" and i > 0 and parts[i - 1].isdigit():
                    passed = int(parts[i - 1])
                if word == "failed" and i > 0 and parts[i - 1].isdigit():
                    failed = int(parts[i - 1])
    return passed, passed + failed


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
