/**
 * api.js
 * Thin wrapper around the MiddleMan backend's HTTP routes.
 *
 * API_BASE_URL comes from an env var so switching from local Flask
 * (http://127.0.0.1:5000) to the deployed Render backend later is a
 * one-line change, not a code change. See .env.example.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'

/**
 * Helper: parses a fetch Response as JSON, throwing a readable Error
 * (using the backend's own {"error": "..."} message when present) if
 * the response was not ok.
 */
async function parseJsonOrThrow(response) {
  let data
  try {
    data = await response.json()
  } catch {
    data = null
  }

  if (!response.ok) {
    const message = data?.error || `Request failed with status ${response.status}`
    throw new Error(message)
  }

  return data
}

/**
 * Sends a URL to /process. Matches app.py: POST /process with a JSON
 * body of { url }.
 */
export async function processUrl(url) {
  const response = await fetch(`${API_BASE_URL}/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  return parseJsonOrThrow(response)
}

/**
 * Sends a File object to /process. Matches app.py: POST /process with
 * multipart/form-data, field name "file".
 */
export async function processFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/process`, {
    method: 'POST',
    body: formData,
  })
  return parseJsonOrThrow(response)
}

/**
 * Returns the direct download URL for a completed job. Used as the
 * href/download target for the "Download compressed file" button —
 * no need to fetch it via JS, the browser can navigate straight to it.
 */
export function getDownloadUrl(jobId) {
  return `${API_BASE_URL}/download/${jobId}`
}

/**
 * Triggers the backend's real pytest run and returns the real
 * pass/fail counts. Backs the Testing & QA banner (Section 4.3) —
 * this must never be a hardcoded number.
 */
export async function runTests() {
  const response = await fetch(`${API_BASE_URL}/run-tests`)
  return parseJsonOrThrow(response)
}
