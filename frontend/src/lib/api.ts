import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export type RewriteMode = 'plagiarism' | 'ai_detection'
export type Language = 'zh' | 'en'
export type RewriteUnit = 'sentence' | 'paragraph'
export type RewriteSource = 'deepseek' | 'marian'

export interface ParagraphInfo {
  id: string
  text: string
  style: string
  is_modified: boolean
  original_text?: string | null
}

export interface DocumentInfo {
  id: string
  filename: string
  paragraphs: ParagraphInfo[]
  uploaded_at: string
  total_paragraphs: number
}

export interface DocumentUploadResponse {
  success: boolean
  message: string
  data: DocumentInfo | null
}

export interface RewriteOptionMeta {
  source: RewriteSource
}

export interface RewriteResponse {
  success: boolean
  message: string
  options: string[]
  mode: RewriteMode
  language: Language
  unit: RewriteUnit
  meta?: RewriteOptionMeta[]
}

export interface HealthResponse {
  status: string
  service: string
  version: string
}

export interface ApiInfoResponse {
  api_version: string
  features: {
    plagiarism_fix: boolean
    ai_detection_fix: boolean
    format_preservation: boolean
    sentence_rewrite?: boolean
    marian_optional?: boolean
  }
  supported_formats: string[]
  max_file_size: string
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.message || error.response?.data?.detail || '请求失败'
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

export const api = {
  healthCheck: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/health')
    return response.data
  },

  getApiInfo: async (): Promise<ApiInfoResponse> => {
    const response = await apiClient.get<ApiInfoResponse>('/api/v1/info')
    return response.data
  },

  uploadDocument: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post<DocumentUploadResponse>('/api/v1/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  rewriteText: async (payload: {
    text: string
    mode: RewriteMode
    language: Language
    unit?: RewriteUnit
    option_count?: number
  }): Promise<RewriteResponse> => {
    const response = await apiClient.post<RewriteResponse>('/api/v1/rewrite', payload)
    return response.data
  },

  exportDocument: async (
    docId: string,
    modifications: Record<string, string>
  ): Promise<Blob> => {
    const response = await apiClient.post<Blob>(
      '/api/v1/export',
      {
        doc_id: docId,
        modifications,
      },
      {
        responseType: 'blob',
      }
    )
    return response.data
  },
}

export default apiClient

