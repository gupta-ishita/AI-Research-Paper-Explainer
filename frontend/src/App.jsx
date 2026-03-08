import { useState } from 'react'
import { uploadPdf, askQuestion } from './api'
import { UploadZone } from './components/UploadZone'
import { SummaryCard } from './components/SummaryCard'
import { QASection } from './components/QASection'
import './App.css'

export default function App() {
  const [paper, setPaper] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState(null)

  const handleUpload = async (file) => {
    setUploadError(null)
    setUploading(true)
    try {
      const data = await uploadPdf(file)
      setPaper({
        paperId: data.paper_id,
        filename: data.filename,
        summary: data.summary,
        numPages: data.num_pages,
      })
    } catch (e) {
      setUploadError(e.message)
    } finally {
      setUploading(false)
    }
  }

  const handleAsk = async (question) => {
    if (!paper) return null
    return askQuestion(paper.paperId, question)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>AI Research Paper Explainer</h1>
        <p>Upload a PDF, get a summary, and ask anything about the paper.</p>
      </header>

      <main className="main">
        <UploadZone
          onUpload={handleUpload}
          uploading={uploading}
          error={uploadError}
          disabled={!!paper}
        />

        {paper && (
          <>
            <div className="paper-actions">
              <button type="button" className="btn-secondary" onClick={() => setPaper(null)}>
                Upload another paper
              </button>
            </div>
            <SummaryCard
              filename={paper.filename}
              summary={paper.summary}
              numPages={paper.numPages}
            />
            <QASection onAsk={handleAsk} />
          </>
        )}
      </main>
    </div>
  )
}
