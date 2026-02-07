import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

type RewriteMode = 'plagiarism' | 'ai_detection'
type Language = 'zh' | 'en'

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

export interface RewriteResponse {
  success: boolean
  message: string
  options: string[]
  mode: RewriteMode
  language: Language
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
  }
  supported_formats: string[]
  max_file_size: string
}

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.message || '请求失败'
    console.error('API Error:', message)
    return Promise.reject(error)
  }
)

// API方法
export const api = {
  // 健康检查
  healthCheck: async (): Promise<HealthResponse> => {
    const { data } = await apiClient.get<HealthResponse>('/health')
    return data
  },
  
  // 获取API信息
  getApiInfo: async (): Promise<ApiInfoResponse> => {
    const { data } = await apiClient.get<ApiInfoResponse>('/api/v1/info')
    return data
  },
  
  // 上传文档
  uploadDocument: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await apiClient.post<DocumentUploadResponse>('/api/v1/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return data
  },
  
  // 改写文本
  rewriteText: async (payload: {
    text: string
    mode: RewriteMode
    language: Language
  }): Promise<RewriteResponse> => {
    const { data } = await apiClient.post<RewriteResponse>('/api/v1/rewrite', payload)
    return data
  },
  
  // 导出文档
  exportDocument: async (documentId: string): Promise<Blob> => {
    const { data } = await apiClient.get<Blob>(`/api/v1/export/${documentId}`, {
      responseType: 'blob',
    })
    return data
  },
}

export default apiClient

