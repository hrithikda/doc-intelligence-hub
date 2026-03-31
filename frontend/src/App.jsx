import { useState, useEffect } from 'react'
import UploadPanel from './components/UploadPanel'
import QAPanel from './components/QAPanel'
import SummaryPanel from './components/SummaryPanel'
import ComparePanel from './components/ComparePanel'
import useStore from './store/useStore'
import api from './api/client'

const TABS = ['Upload', 'Q&A', 'Summary', 'Compare']

export default function App() {
  const [activeTab, setActiveTab] = useState('Upload')
  const { setDocuments } = useStore()

  useEffect(() => {
    api.get('/documents/').then(r => setDocuments(r.data)).catch(() => {})
  }, [])

  const renderPanel = () => {
    if (activeTab === 'Upload') return <UploadPanel />
    if (activeTab === 'Q&A') return <QAPanel />
    if (activeTab === 'Summary') return <SummaryPanel />
    if (activeTab === 'Compare') return <ComparePanel />
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ background: '#fff', borderBottom: '1px solid #e5e7eb', padding: '0 32px', display: 'flex', alignItems: 'center', gap: '32px' }}>
        <div style={{ padding: '16px 0', fontWeight: 700, fontSize: '18px', color: '#6366f1' }}>DocIntel</div>
        <div style={{ display: 'flex', gap: '4px' }}>
          {TABS.map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: '16px 20px',
                background: 'none',
                border: 'none',
                borderBottom: activeTab === tab ? '2px solid #6366f1' : '2px solid transparent',
                color: activeTab === tab ? '#6366f1' : '#6b7280',
                fontWeight: activeTab === tab ? 600 : 400,
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      <div style={{ maxWidth: '900px', margin: '32px auto', background: '#fff', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', minHeight: '600px' }}>
        {renderPanel()}
      </div>
    </div>
  )
}
