import { useState, useEffect, useRef } from 'react'
import api from '../api/client'
import useStore from '../store/useStore'

export default function QAPanel() {
  const { documents, setDocuments, qaHistory, addQA, clearQA } = useStore()
  const [question, setQuestion] = useState('')
  const [selectedDoc, setSelectedDoc] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef()

  useEffect(() => {
    api.get('/documents/').then(r => setDocuments(r.data))
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [qaHistory])

  const ask = async () => {
    if (!question.trim()) return
    setLoading(true)
    try {
      const res = await api.post('/qa/ask', {
        question,
        document_id: selectedDoc ? parseInt(selectedDoc) : null
      })
      addQA({ question, answer: res.data.answer, sources: res.data.sources })
      setQuestion('')
    } catch (e) {
      addQA({ question, answer: e.response?.data?.detail || 'Error getting answer.', sources: [] })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2>Ask a Question</h2>
        {qaHistory.length > 0 && <button onClick={clearQA} style={{ fontSize: '13px', color: '#6b7280', background: 'none', border: 'none', cursor: 'pointer' }}>Clear</button>}
      </div>

      <select value={selectedDoc} onChange={(e) => setSelectedDoc(e.target.value)} style={{ marginBottom: '16px', padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '14px' }}>
        <option value="">All documents</option>
        {documents.map(d => <option key={d.id} value={d.id}>{d.original_name}</option>)}
      </select>

      <div style={{ flex: 1, overflowY: 'auto', marginBottom: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {qaHistory.length === 0 && <p style={{ color: '#9ca3af', textAlign: 'center', marginTop: '40px' }}>Ask a question about your documents.</p>}
        {qaHistory.map((item, i) => (
          <div key={i}>
            <div style={{ background: '#6366f1', color: '#fff', padding: '10px 14px', borderRadius: '12px 12px 4px 12px', alignSelf: 'flex-end', maxWidth: '80%', marginLeft: 'auto', marginBottom: '8px' }}>{item.question}</div>
            <div style={{ background: '#f3f4f6', padding: '12px 14px', borderRadius: '4px 12px 12px 12px', fontSize: '14px', lineHeight: '1.6' }}>
              {item.answer}
              {item.sources?.length > 0 && (
                <div style={{ marginTop: '8px', fontSize: '12px', color: '#9ca3af' }}>
                  Sources: {item.sources.map((s, j) => <span key={j} style={{ marginRight: '8px' }}>{s.filename} {s.page > 0 ? `p.${s.page}` : s.section}</span>)}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div style={{ color: '#9ca3af', fontSize: '14px' }}>Thinking...</div>}
        <div ref={bottomRef} />
      </div>

      <div style={{ display: 'flex', gap: '8px' }}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && ask()}
          placeholder="Ask anything about your documents..."
          style={{ flex: 1, padding: '10px 14px', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '14px' }}
        />
        <button onClick={ask} disabled={loading} style={{ padding: '10px 20px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 500 }}>
          {loading ? '...' : 'Ask'}
        </button>
      </div>
    </div>
  )
}
