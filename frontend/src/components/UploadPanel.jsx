import { useState, useRef } from 'react'
import api from '../api/client'
import useStore from '../store/useStore'

export default function UploadPanel() {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState(null)
  const fileRef = useRef()
  const { documents, setDocuments } = useStore()

  const fetchDocs = async () => {
    const res = await api.get('/documents/')
    setDocuments(res.data)
  }

  const upload = async (file) => {
    if (!file) return
    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
    if (!allowed.includes(file.type) && !file.name.endsWith('.pdf') && !file.name.endsWith('.docx') && !file.name.endsWith('.txt')) {
      setMessage({ type: 'error', text: 'Only PDF, DOCX, and TXT files are supported.' })
      return
    }
    setUploading(true)
    setMessage(null)
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await api.post('/documents/upload', form)
      setMessage({ type: 'success', text: `${res.data.original_name} uploaded — ${res.data.chunk_count} chunks, ${res.data.entity_count} entities extracted.` })
      await fetchDocs()
    } catch (e) {
      setMessage({ type: 'error', text: e.response?.data?.detail || 'Upload failed.' })
    } finally {
      setUploading(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    upload(e.dataTransfer.files[0])
  }

  const deleteDoc = async (id) => {
    await api.delete(`/documents/${id}`)
    await fetchDocs()
  }

  return (
    <div style={{ padding: '24px' }}>
      <h2 style={{ marginBottom: '16px' }}>Upload Document</h2>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current.click()}
        style={{
          border: `2px dashed ${dragging ? '#6366f1' : '#ccc'}`,
          borderRadius: '12px',
          padding: '40px',
          textAlign: 'center',
          cursor: 'pointer',
          background: dragging ? '#eef2ff' : '#fafafa',
          marginBottom: '16px'
        }}
      >
        <input ref={fileRef} type="file" accept=".pdf,.docx,.txt" style={{ display: 'none' }} onChange={(e) => upload(e.target.files[0])} />
        {uploading ? <p>Uploading and processing... this may take a minute.</p> : <p>Drag and drop a PDF, DOCX, or TXT file here, or click to browse.</p>}
      </div>

      {message && (
        <div style={{ padding: '12px 16px', borderRadius: '8px', marginBottom: '16px', background: message.type === 'success' ? '#dcfce7' : '#fee2e2', color: message.type === 'success' ? '#166534' : '#991b1b' }}>
          {message.text}
        </div>
      )}

      {documents.length > 0 && (
        <div>
          <h3 style={{ marginBottom: '12px' }}>Uploaded Documents</h3>
          {documents.map(doc => (
            <div key={doc.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', borderRadius: '8px', border: '1px solid #e5e7eb', marginBottom: '8px', background: '#fff' }}>
              <div>
                <div style={{ fontWeight: 500 }}>{doc.original_name}</div>
                <div style={{ fontSize: '13px', color: '#6b7280' }}>{doc.chunk_count} chunks · {doc.status}</div>
              </div>
              <button onClick={() => deleteDoc(doc.id)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '13px' }}>Delete</button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
