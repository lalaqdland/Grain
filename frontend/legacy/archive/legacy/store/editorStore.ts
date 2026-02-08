import { create } from 'zustand'
import { Document, Paragraph } from '@/types'

interface EditorState {
  // 文档状态
  document: Document | null
  isLoading: boolean
  error: string | null
  
  // 操作方法
  setDocument: (doc: Document) => void
  updateParagraph: (id: string, text: string) => void
  resetParagraph: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearDocument: () => void
}

export const useEditorStore = create<EditorState>((set) => ({
  // 初始状态
  document: null,
  isLoading: false,
  error: null,
  
  // 设置文档
  setDocument: (doc) => set({ document: doc, error: null }),
  
  // 更新段落
  updateParagraph: (id, text) => set((state) => {
    if (!state.document) return state
    
    const updatedParagraphs = state.document.content.map((para) => {
      if (para.id === id) {
        return {
          ...para,
          text,
          isModified: true,
          originalText: para.originalText || para.text
        }
      }
      return para
    })
    
    return {
      document: {
        ...state.document,
        content: updatedParagraphs
      }
    }
  }),
  
  // 重置段落（撤销修改）
  resetParagraph: (id) => set((state) => {
    if (!state.document) return state
    
    const updatedParagraphs = state.document.content.map((para) => {
      if (para.id === id && para.originalText) {
        return {
          ...para,
          text: para.originalText,
          isModified: false,
          originalText: undefined
        }
      }
      return para
    })
    
    return {
      document: {
        ...state.document,
        content: updatedParagraphs
      }
    }
  }),
  
  // 设置加载状态
  setLoading: (loading) => set({ isLoading: loading }),
  
  // 设置错误
  setError: (error) => set({ error }),
  
  // 清空文档
  clearDocument: () => set({ document: null, error: null })
}))

