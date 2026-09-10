# MiddleMan

**We do the downloading. You get the smaller file.**

MiddleMan is a tool for slow or limited internet connections. Instead of downloading a large file directly onto your device over a bad connection, you send MiddleMan a URL (or upload a file). A cloud server — which has a fast, reliable connection — does the actual downloading, compresses the file to reduce its size, then sends you back the smaller version. Your device only has to receive the compressed file, saving time and bandwidth.

> Think of it like a middleman who does the heavy lifting on a fast connection, then hands you a lighter package to carry home over your slow one.

Submitted also as **"Cloud-Based Adaptive Content Compression and Delivery System"**

---

## How it works

1. You submit a URL or upload a file through the web app.
2. The cloud server fetches the full content using its own fast connection.
3. The server compresses the content.
4. The compressed result is sent back to you.
5. You download the smaller file.

Two network legs are involved — the server fetching the source content, and the server delivering the compressed result to you — and the whole point of the project is measuring the bandwidth saved on that second, user-facing leg.

## Why each subject is genuinely represented

| Subject | What it is in this project |
|---|---|
| **Cloud Computing** | The fetch-and-compress work runs entirely on a remote cloud server, not on your device. |
| **Networking** | Two distinct network legs (server → source, server → user), with the bandwidth savings on the user-facing leg measured and shown. |
| **Testing & QA** | A pytest suite covering valid/invalid URLs, unreachable sources, compression correctness, and oversized files. |

The app also surfaces this directly in the UI: as each real step completes, a banner appears naming which subject that step demonstrates — similar to how a payment app shows a sequence of confirmation screens as a transaction moves through its stages.

**Honest scope note:** the networking component here is a standard request-response pattern used twice, with a genuine bandwidth-saving rationale — not custom protocol design or peer discovery. It's real, but intentionally not deep, in favor of building something that works end-to-end.

## Tech stack

- **Frontend:** React (via Vite)
- **Backend:** Python + Flask
- **Storage:** SQLite
- **Testing:** pytest
- **Hosting:** Render (Web Service for the API, Static Site for the frontend)

## Project structure

```
MiddleMan/
├── frontend/     # React app (Vite)
├── backend/      # Flask API, compression logic, tests
└── README.md
```

## Running it locally

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

**Backend**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

The frontend expects the backend API to be reachable — see `frontend/.env` (or the relevant config) for the API base URL when running both locally.

---
