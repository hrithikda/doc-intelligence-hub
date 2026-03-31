import { useState, useEffect } from 'react'
import api from '../api/client'
import useStore from '../store/useStore'

const VERDICT_COLORS = {
  similar: { bg: '#dcfce7', color: '#166534' },
  differs: { bg: '#fef9c3', color: '#854d0e' },
  only_in_a: { bg: '#dbeafe', color: '#1e40af' },
  only_in_b: { bg: '#fce7f3', color: '#9d174d' }
}

export default function ComparePanel() {
  const { documents, setDocuments } = useStore()
  const [docA, setDocA] = useState('')
  const [docB, setDocB] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.get('/documents/').then(r => setDocuments(r.data))
  }, [])

  const compare = async () => {
    if (!docA || !docB || docA === docB) { setError('Select two different documents.'); return }
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.post('/compare/', { document_id_a: parseInt(docA), document_id_b: parseInt(docB) })
      setResult(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Comparison failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '24px' }}>
      <h2 style={{ marginBottom: '16px' }}>Compare Documents</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
        <div>
          <label style={{ fontSize: '13px', color: '#6b7280', display: 'block', marginBottom: '6px' }}>Document A</label>
          <select value={docA} onChange={(e) => setDocA(e.target.value)} style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '14px' }}>
            <option value="">Select document</option>
            {documents.map(d => <option key={d.id} value={d.id}>{d.original_name}</option>)}
          </select>
        </div>
        <div>
          <label style={{ fontSize: '13px', color: '#6b7280', display: 'block', marginBottom: '6px' }}>Document B</label>
          <select value={docB} onChange={(e) => setDocB(e.target.value)} style={{ width: '100%', padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '14px' }}>
            <option value="">Select document</option>
            {documents.map(d => <option key={d.id} value={d.id}>{d.original_name}</option>)}
          </select>
        </div>
      </div>

      <button onClick={compare} disabled={loading} style={{ padding: '10px 24px', background: '#6366f1', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 500, marginBottom: '24px' }}>
        {loading ? 'Comparing...' : 'Compare'}
      </button>

      {error && <div style={{ padding: '12px 16px', borderRadius: '8px', background: '#fee2e2', color: '#991b1b', marginBottom: '16px' }}>{error}</div>}

      {result && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 80px', gap: '0', borderRadius: '8px', overflow: 'hidden', border: '1px solid #e5e7eb' }}>
            {['Topic', result.filename_a, result.filename_b, 'Verdict'].map((h, i) => (
              <div key={i} style={{ padding: '10px 12px', background: '#f9fafb', fontWeight: 600, fontSize: '13px', borderBottom: '1px solid #e5e7eb' }}>{h}</div>
            ))}
            {result.comparisons.map((row, i) => (
              <>
                <div key={`t${i}`} style={{ padding: '10px 12px', fontSize: '13px', borderBottom: '1px solid #f3f4f6', fontWeight: 500 }}>{row.topic}</div>
                <div key={`a${i}`} style={{ padding: '10px 12px', fontSize: '13px', borderBottom: '1px solid #f3f4f6', color: '#374151' }}>{row.doc_a}</div>
                <div key={`b${i}`} style={{ padding: '10px 12px', fontSize: '13px', borderBottom: '1px solid #f3f4f6', color: '#374151' }}>{row.doc_b}</div>
                <div key={`v${i}`} style={{ padding: '10px 12px', borderBottom: '1px solid #f3f4f6' }}>
                  <span style={{ padding: '2px 8px', borderRadius: '999px', fontSize: '11px', fontWeight: 600, ...VERDICT_COLORS[row.verdict] }}>{row.verdict}</span>
                </div>
              </>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
