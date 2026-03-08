import './SummaryCard.css'

export function SummaryCard({ filename, summary, numPages }) {
  return (
    <section className="summary-card">
      <div className="summary-header">
        <h2>Summary</h2>
        <span className="summary-meta">
          {filename} · {numPages} page{numPages !== 1 ? 's' : ''}
        </span>
      </div>
      <div className="summary-body">
        {summary.split('\n').map((p, i) => (
          <p key={i}>{p}</p>
        ))}
      </div>
    </section>
  )
}
