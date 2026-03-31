import { create } from 'zustand'

const useStore = create((set) => ({
  documents: [],
  selectedDocument: null,
  qaHistory: [],
  loading: false,
  error: null,

  setDocuments: (docs) => set({ documents: docs }),
  setSelectedDocument: (doc) => set({ selectedDocument: doc }),
  addQA: (qa) => set((state) => ({ qaHistory: [...state.qaHistory, qa] })),
  clearQA: () => set({ qaHistory: [] }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error })
}))

export default useStore
