import { useState } from 'react'
import './QASection.css'

export function QASection({ onAsk }) {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    const q = question.trim()
    if (!q || loading) return
    setError(null)
    setAnswer(null)
    setLoading(true)
    try {
      const res = await onAsk(q)
      setAnswer(res.answer)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="qa-section">
      <h2>Ask about the paper</h2>
      <form className="qa-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. What is the main finding?"
          className="qa-input"
          disabled={loading}
          maxLength={500}
        />
        <button type="submit" className="qa-submit" disabled={loading || !question.trim()}>
          {loading ? '…' : 'Ask'}
        </button>
      </form>
      {error && <p className="qa-error">{error}</p>}
      {answer && (
        <div className="qa-answer">
          <strong>Answer</strong>
          <p>{answer}</p>
        </div>
      )}
    </section>
  )
}
