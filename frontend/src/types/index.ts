/**
 * 前端通用类型定义
 */

export type RewriteMode = 'plagiarism' | 'ai_detection'
export type Language = 'zh' | 'en'
export type RewriteUnit = 'sentence' | 'paragraph'

export interface Paragraph {
  id: string
  text: string
  style: string
  is_modified: boolean
  original_text?: string | null
}

export interface GrainDocument {
  id: string
  filename: string
  paragraphs: Paragraph[]
  total_paragraphs: number
}

