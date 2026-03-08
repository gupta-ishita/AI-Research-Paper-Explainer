import { useRef } from 'react'
import './UploadZone.css'

export function UploadZone({ onUpload, uploading, error, disabled }) {
  const inputRef = useRef(null)

  const handleDrop = (e) => {
    e.preventDefault()
    if (disabled || uploading) return
    const file = e.dataTransfer?.files?.[0]
    if (file?.type === 'application/pdf') onUpload(file)
  }

  const handleChange = (e) => {
    const file = e.target?.files?.[0]
    if (file) onUpload(file)
  }

  const handleClick = () => {
    if (disabled || uploading) return
    inputRef.current?.click()
  }

  return (
    <section className="upload-zone">
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        onChange={handleChange}
        className="upload-input"
        aria-hidden
      />
      <div
        className={`upload-box ${uploading ? 'uploading' : ''} ${disabled ? 'disabled' : ''}`}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        {uploading ? (
          <span className="upload-text">Processing…</span>
        ) : disabled ? (
          <span className="upload-text">Paper loaded. Use “Upload another paper” to replace.</span>
        ) : (
          <>
            <span className="upload-icon">📄</span>
            <span className="upload-text">Drop a PDF here or click to upload</span>
          </>
        )}
      </div>
      {error && <p className="upload-error">{error}</p>}
    </section>
  )
}
