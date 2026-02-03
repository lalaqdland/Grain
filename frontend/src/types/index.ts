/**
 * TypeScript类型定义
 */

// 段落类型
export interface Paragraph {
  id: string
  text: string
  style: string
  isModified: boolean
  originalText?: string
}

// 文档类型
export interface Document {
  id: string
  filename: string
  content: Paragraph[]
  uploadedAt: string
}

// 改写模式
export type RewriteMode = 'plagiarism' | 'ai_detection'

// 语言类型
export type Language = 'zh' | 'en'

// 改写请求
export interface RewriteRequest {
  text: string
  mode: RewriteMode
  language: Language
}

// 改写响应
export interface RewriteResponse {
  options: string[]
  mode: RewriteMode
  language: Language
}

// API响应
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

