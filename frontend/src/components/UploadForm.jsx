import { useState } from 'react'
import './UploadForm.css'

/**
 * UploadForm
 * Lets the user submit either a URL or a file to be processed.
 * Layout-only for now — onSubmit is called with { mode, url, file }
 * and the parent (App.jsx) will wire this to the /process backend call.
 */
export default function UploadForm({ onSubmit, disabled }) {
  const [mode, setMode] = useState('url') // 'url' | 'file'
  const [url, setUrl] = useState('')
  const [file, setFile] = useState(null)

  function handleSubmit(e) {
    e.preventDefault()
    if (disabled) return
    onSubmit({ mode, url, file })
  }

  const canSubmit = mode === 'url' ? url.trim().length > 0 : file !== null

  return (
    <form className="upload-form" onSubmit={handleSubmit}>
      <div className="upload-form__tabs" role="tablist" aria-label="Input method">
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'url'}
          className={`upload-form__tab ${mode === 'url' ? 'is-active' : ''}`}
          onClick={() => setMode('url')}
        >
          URL
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === 'file'}
          className={`upload-form__tab ${mode === 'file' ? 'is-active' : ''}`}
          onClick={() => setMode('file')}
        >
          File
        </button>
      </div>

      {mode === 'url' ? (
        <div className="upload-form__field">
          <label htmlFor="source-url">Source URL</label>
          <input
            id="source-url"
            type="url"
            inputMode="url"
            placeholder="https://example.com/large-file.zip"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={disabled}
            autoComplete="off"
          />
        </div>
      ) : (
        <div className="upload-form__field">
          <label htmlFor="source-file">File to compress</label>
          <div className="upload-form__dropzone">
            <input
              id="source-file"
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              disabled={disabled}
            />
            <span className="upload-form__dropzone-text">
              {file ? file.name : 'Choose a file, or drag it here'}
            </span>
          </div>
        </div>
      )}

      <button
        type="submit"
        className="upload-form__submit"
        disabled={disabled || !canSubmit}
      >
        {disabled ? 'Processing…' : 'Send to server'}
      </button>
    </form>
  )
}
