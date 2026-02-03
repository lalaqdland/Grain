import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

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
  healthCheck: () => apiClient.get('/health'),
  
  // 获取API信息
  getApiInfo: () => apiClient.get('/api/v1/info'),
  
  // 上传文档
  uploadDocument: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/api/v1/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  
  // 改写文本
  rewriteText: (data: {
    text: string
    mode: 'plagiarism' | 'ai_detection'
    language: 'zh' | 'en'
  }) => apiClient.post('/api/v1/rewrite', data),
  
  // 导出文档
  exportDocument: (documentId: string) => 
    apiClient.get(`/api/v1/export/${documentId}`, {
      responseType: 'blob',
    }),
}

export default apiClient

