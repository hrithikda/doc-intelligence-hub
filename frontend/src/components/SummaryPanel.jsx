import { useState, useEffect } from 'react'
import api from '../api/client'
import useStore from '../store/useStore'

export default function SummaryPanel() {
  const { documents, setDocuments } = useStore()
  const [selectedDoc, setSelectedDoc] = useState('')
  const [summary, setSummary] = useState(null)
  const [entities, setEntities] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.get('/documents/').then(r => setDocuments(r.data))
  }, [])

  const load = async (id) => {
    setSelectedDoc(id)
    if (!id) { setSummary(null); setEntities([]); return }
    setLoading(true)
    try {
      const [s, e] = await Promise.all([
        api.get(`/analysis/summary/${id}`),
        api.get(`/analysis/entities/${id}`)
      ])
      setSummary(s.data)
      setEntities(e.data)
    } catch (e) {
      setSummary(null)
      setEntities([])
    } finally {
      setLoading(false)
    }
  }

  const grouped = entities.reduce((acc, e) => {
    acc[e.entity_type] = acc[e.entity_type] || []
    acc[e.entity_type].push(e)
    return acc
  }, {})

  const fields = ['purpose', 'parties', 'key_dates', 'obligations', 'risks']
  const labels = { purpose: 'Purpose', parties: 'Parties', key_dates: 'Key Dates', obligations: 'Obligations', risks: 'Risks' }

  return (
    <div style={{ padding: '24px' }}>
      <h2 style={{ marginBottom: '16px' }}>Document Summary</h2>

      <select value={selectedDoc} onChange={(e) => load(e.target.value)} style={{ marginBottom: '24px', padding: '8px 12px', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '14px', width: '100%' }}>
        <option value="">Select a document</option>
        {documents.map(d => <option key={d.id} value={d.id}>{d.original_name}</option>)}
      </select>

      {loading && <p style={{ color: '#9ca3af' }}>Loading...</p>}

      {summary && (
        <div style={{ marginBottom: '32px' }}>
          <h3 style={{ marginBottom: '12px' }}>Structured Summary</h3>
          {fields.map(f => summary[f] && (
            <div key={f} style={{ marginBottom: '12px', padding: '12px 16px', borderRadius: '8px', background: '#f9fafb', border: '1px solid #e5e7eb' }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#6366f1', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{labels[f]}</div>
              <div style={{ fontSize: '14px', lineHeight: '1.6' }}>{summary[f]}</div>
            </div>
          ))}
        </div>
      )}

      {entities.length > 0 && (
        <div>
          <h3 style={{ marginBottom: '12px' }}>Extracted Entities</h3>
          {Object.entries(grouped).map(([type, items]) => (
            <div key={type} style={{ marginBottom: '16px' }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{type.replace('_', ' ')}</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {items.map((e, i) => (
                  <span key={i} title={e.context} style={{ padding: '4px 10px', borderRadius: '999px', background: '#eef2ff', color: '#4338ca', fontSize: '13px' }}>{e.value}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
