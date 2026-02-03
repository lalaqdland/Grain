'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { api } from '@/lib/api'
import { formatFileSize } from '@/lib/utils'

type Mode = 'plagiarism' | 'ai_detection'

interface Document {
  id: string
  filename: string
  paragraphs: Array<{
    id: string
    text: string
    style: string
    is_modified: boolean
  }>
  total_paragraphs: number
}

const MAX_FILE_SIZE = 10485760 // 10MB

export default function Home() {
  const [mode, setMode] = useState<Mode>('plagiarism')
  const [document, setDocument] = useState<Document | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hoveredParagraph, setHoveredParagraph] = useState<string | null>(null)
  const [rewritingParagraph, setRewritingParagraph] = useState<string | null>(null)
  const [rewriteOptions, setRewriteOptions] = useState<{[key: string]: string[]}>({})
  const [showOptions, setShowOptions] = useState<string | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    
    // 验证文件大小
    if (file.size > MAX_FILE_SIZE) {
      setError(`文件太大了！最大支持 ${formatFileSize(MAX_FILE_SIZE)}，您的文件是 ${formatFileSize(file.size)}`)
      return
    }

    // 开始上传
    setIsLoading(true)
    setError(null)

    try {
      const response = await api.uploadDocument(file)
      
      if (response.success && response.data) {
        setDocument(response.data)
        setError(null)
      } else {
        setError('上传失败了，请重试一下')
      }
    } catch (error: any) {
      console.error('Upload error:', error)
      
      // 更友好的错误提示
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        setError('❌ 无法连接到服务器\n请确保后端服务已启动（运行在 http://localhost:8001）')
      } else if (error.response?.status === 404) {
        setError('❌ 上传接口未找到\n请检查后端服务是否正常运行')
      } else if (error.response?.status === 413) {
        setError('❌ 文件太大了\n请选择小于10MB的文档')
      } else if (error.response?.status === 400) {
        setError(error.response?.data?.detail || '❌ 文件格式不对\n仅支持 .docx 格式的Word文档')
      } else {
        setError(error.response?.data?.detail || `❌ 上传失败\n${error.message || '未知错误，请重试'}`)
      }
    } finally {
      setIsLoading(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: MAX_FILE_SIZE,
    multiple: false,
    noClick: !!document // 上传后禁用点击
  })

  const handleReset = () => {
    setDocument(null)
    setError(null)
    setRewriteOptions({})
    setShowOptions(null)
  }

  const handleRewrite = async (paragraphId: string, text: string) => {
    setRewritingParagraph(paragraphId)
    setError(null)

    try {
      const response = await api.rewriteText({
        text,
        mode,
        language: 'zh' // 默认中文，可以根据文本自动检测
      })

      if (response.success && response.options) {
        setRewriteOptions(prev => ({
          ...prev,
          [paragraphId]: response.options
        }))
        setShowOptions(paragraphId)
      } else {
        setError('❌ 改写失败，请重试')
      }
    } catch (error: any) {
      console.error('Rewrite error:', error)
      
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        setError('❌ 无法连接到服务器\n请确保后端服务已启动（http://localhost:8001）')
      } else if (error.response?.status === 404) {
        setError('❌ 改写接口未找到\n可能原因：后端服务未正确启动或路由配置错误')
      } else if (error.response?.status === 400) {
        setError('❌ 请求参数错误\n' + (error.response?.data?.detail || '请检查输入内容'))
      } else if (error.response?.status === 500) {
        setError('❌ 服务器错误\n' + (error.response?.data?.detail || 'DeepSeek API调用失败，请检查API Key配置'))
      } else {
        setError(`❌ 改写失败\n${error.response?.data?.detail || error.message || '未知错误，请重试'}`)
      }
    } finally {
      setRewritingParagraph(null)
    }
  }

  const handleSelectOption = (paragraphId: string, optionText: string) => {
    if (!document) return

    // 更新文档中的段落
    const updatedParagraphs = document.paragraphs.map(para => {
      if (para.id === paragraphId) {
        return {
          ...para,
          text: optionText,
          is_modified: true
        }
      }
      return para
    })

    setDocument({
      ...document,
      paragraphs: updatedParagraphs
    })

    // 清除选项显示
    setShowOptions(null)
  }

  const handleExport = async () => {
    if (!document) return

    try {
      const blob = await api.exportDocument(document.id)
      
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([blob]))
      const link = window.document.createElement('a')
      link.href = url
      link.setAttribute('download', `modified_${document.filename}`)
      window.document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error: any) {
      console.error('Export error:', error)
      setError('😢 导出失败，请重试')
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      <div className="container mx-auto px-6 py-12 max-w-7xl">
        
        {/* 顶部标题 */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-3 tracking-tight">
            <span className="bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
              Grain
            </span>
          </h1>
          <p className="text-lg text-slate-600">守拙 · The AI Humanizer & Academic Shield</p>
        </div>

        {/* 模式选择 Tab */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-white rounded-2xl p-1.5 shadow-sm border border-slate-200">
            <button
              onClick={() => setMode('plagiarism')}
              className={`
                px-8 py-3 rounded-xl font-medium transition-all duration-200
                ${mode === 'plagiarism'
                  ? 'bg-gradient-to-r from-rose-500 to-pink-500 text-white shadow-md'
                  : 'text-slate-600 hover:text-slate-900'
                }
              `}
            >
              <span className="mr-2">🔴</span>
              降重模式
            </button>
            <button
              onClick={() => setMode('ai_detection')}
              className={`
                px-8 py-3 rounded-xl font-medium transition-all duration-200
                ${mode === 'ai_detection'
                  ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-md'
                  : 'text-slate-600 hover:text-slate-900'
                }
              `}
            >
              <span className="mr-2">🟠</span>
              降AI模式
            </button>
          </div>
        </div>

        {/* 模式说明 */}
        <div className="text-center mb-10">
          {mode === 'plagiarism' ? (
            <p className="text-slate-600 text-sm">
              针对知网、Turnitin标红段落，通过学术化扩写和结构重组降低查重率
            </p>
          ) : (
            <p className="text-slate-600 text-sm">
              针对GPTZero、Turnitin AI检测，通过熵增和人性化改写让文本更自然
            </p>
          )}
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="max-w-3xl mx-auto mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl text-red-700 text-sm whitespace-pre-line">
            {error}
          </div>
        )}

        {/* 主内容区域 */}
        <div className="max-w-5xl mx-auto">
          {!document ? (
            /* 上传区域 */
            <div
              {...getRootProps()}
              className={`
                border-2 border-dashed rounded-3xl p-16 text-center cursor-pointer
                transition-all duration-300 bg-white
                ${isDragActive 
                  ? 'border-violet-400 bg-violet-50 scale-[1.02]' 
                  : 'border-slate-300 hover:border-violet-300 hover:shadow-lg'
                }
              `}
            >
              <input {...getInputProps()} />
              
              <div className="flex flex-col items-center gap-6">
                <div className="text-7xl">
                  {isLoading ? '⏳' : isDragActive ? '📥' : '📄'}
                </div>
                
                {isLoading ? (
                  <div className="space-y-3">
                    <p className="text-xl text-slate-700 font-medium">
                      正在上传和解析文档...
                    </p>
                    <div className="flex justify-center gap-2">
                      <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                ) : isDragActive ? (
                  <p className="text-xl text-violet-600 font-medium">
                    松开鼠标上传文件
                  </p>
                ) : (
                  <>
                    <div className="space-y-2">
                      <p className="text-xl text-slate-700 font-medium">
                        拖拽 Word 文档到这里
                      </p>
                      <p className="text-sm text-slate-500">
                        或点击选择文件
                      </p>
                    </div>
                    
                    <button
                      type="button"
                      className="mt-4 px-8 py-3 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg transition-all duration-200 hover:scale-105"
                    >
                      选择文件
                    </button>
                    
                    <p className="text-xs text-slate-400 mt-4">
                      仅支持 .docx 格式 · 最大 10MB
                    </p>
                    <p className="text-xs text-slate-500 mt-2 max-w-md mx-auto">
                      💡 为了保证完美的排版格式，请在 Word 中将文件'另存为' .docx 格式后再上传
                    </p>
                  </>
                )}
              </div>
            </div>
          ) : (
            /* 文档编辑区域 */
            <div className="bg-white rounded-3xl shadow-lg border border-slate-200 overflow-hidden">
              {/* 文档头部 */}
              <div className="px-8 py-6 border-b border-slate-200 bg-slate-50">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-800">{document.filename}</h2>
                    <p className="text-sm text-slate-500 mt-1">
                      共 {document.total_paragraphs} 个段落
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={handleReset}
                      className="px-5 py-2.5 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-colors text-sm font-medium"
                    >
                      重新上传
                    </button>
                    <button 
                      onClick={handleExport}
                      className="px-5 py-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all text-sm font-medium"
                    >
                      导出文档
                    </button>
                  </div>
                </div>
              </div>

              {/* 段落列表 */}
              <div className="p-8 space-y-4 max-h-[600px] overflow-y-auto">
                {document.paragraphs.map((para) => (
                  <div
                    key={para.id}
                    onMouseEnter={() => setHoveredParagraph(para.id)}
                    onMouseLeave={() => setHoveredParagraph(null)}
                    className={`
                      group relative pl-6 pr-4 py-4 rounded-xl transition-all duration-200 cursor-pointer
                      ${para.is_modified ? 'bg-green-50' : 'hover:bg-slate-50'}
                    `}
                  >
                    {/* 左侧指示条 */}
                    <div className={`
                      absolute left-0 top-0 bottom-0 w-1 rounded-full transition-all duration-200
                      ${para.is_modified 
                        ? 'bg-gradient-to-b from-green-500 to-emerald-500'
                        : hoveredParagraph === para.id 
                          ? mode === 'plagiarism' 
                            ? 'bg-gradient-to-b from-rose-500 to-pink-500' 
                            : 'bg-gradient-to-b from-amber-500 to-orange-500'
                          : 'bg-slate-200'
                      }
                    `} />
                    
                    {/* 段落内容 */}
                    <div className="flex items-start justify-between gap-4">
                      <p className={`
                        flex-1 leading-relaxed
                        ${para.style === 'Title' ? 'text-xl font-bold text-slate-900' : ''}
                        ${para.style === 'Heading 1' ? 'text-lg font-semibold text-slate-800' : ''}
                        ${para.style === 'Normal' ? 'text-slate-700' : ''}
                      `}>
                        {para.text}
                      </p>
                      
                      {/* 操作按钮 */}
                      {hoveredParagraph === para.id && rewritingParagraph !== para.id && (
                        <button 
                          onClick={() => handleRewrite(para.id, para.text)}
                          className={`
                            px-4 py-2 rounded-lg text-white text-sm font-medium
                            transition-all duration-200 hover:shadow-md whitespace-nowrap
                            ${mode === 'plagiarism'
                              ? 'bg-gradient-to-r from-rose-500 to-pink-500'
                              : 'bg-gradient-to-r from-amber-500 to-orange-500'
                            }
                          `}
                        >
                          {mode === 'plagiarism' ? '降重' : '降AI'}
                        </button>
                      )}
                      
                      {/* 加载中 */}
                      {rewritingParagraph === para.id && (
                        <div className="flex items-center gap-2 px-4 py-2">
                          <div className="flex gap-1">
                            <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {/* 改写选项气泡 */}
                    {showOptions === para.id && rewriteOptions[para.id] && (
                      <div className="mt-4 space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                        <p className="text-xs text-slate-500 font-medium mb-2">选择一个改写版本：</p>
                        {rewriteOptions[para.id].map((option, index) => (
                          <div
                            key={index}
                            onClick={() => handleSelectOption(para.id, option)}
                            className={`
                              p-4 rounded-lg border-2 cursor-pointer transition-all duration-200
                              hover:shadow-md hover:scale-[1.01]
                              ${mode === 'plagiarism'
                                ? 'border-rose-200 bg-rose-50 hover:border-rose-400'
                                : 'border-amber-200 bg-amber-50 hover:border-amber-400'
                              }
                            `}
                          >
                            <div className="flex items-start gap-2">
                              <span className={`
                                text-xs font-bold mt-0.5
                                ${mode === 'plagiarism' ? 'text-rose-600' : 'text-amber-600'}
                              `}>
                                {index + 1}
                              </span>
                              <p className="flex-1 text-sm text-slate-700 leading-relaxed">
                                {option}
                              </p>
                            </div>
                          </div>
                        ))}
                        <button
                          onClick={() => setShowOptions(null)}
                          className="w-full mt-2 px-4 py-2 text-sm text-slate-600 hover:text-slate-800 transition-colors"
                        >
                          取消
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* 底部特性说明 */}
        {!document && (
          <div className="mt-16 max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-white rounded-2xl border border-slate-200 hover:shadow-md transition-shadow">
                <div className="text-3xl mb-3">📄</div>
                <h3 className="font-semibold text-slate-800 mb-2">格式神圣</h3>
                <p className="text-sm text-slate-600">
                  XML骨架置换技术<br/>确保格式分毫不差
                </p>
              </div>
              <div className="text-center p-6 bg-white rounded-2xl border border-slate-200 hover:shadow-md transition-shadow">
                <div className="text-3xl mb-3">🖥️</div>
                <h3 className="font-semibold text-slate-800 mb-2">外屏协同</h3>
                <p className="text-sm text-slate-600">
                  配合系统分屏<br/>专注极致编辑体验
                </p>
              </div>
              <div className="text-center p-6 bg-white rounded-2xl border border-slate-200 hover:shadow-md transition-shadow">
                <div className="text-3xl mb-3">🤖</div>
                <h3 className="font-semibold text-slate-800 mb-2">双模引擎</h3>
                <p className="text-sm text-slate-600">
                  降重与降AI两套算法<br/>一键切换
                </p>
              </div>
            </div>
          </div>
        )}

        {/* 版本信息 */}
        <p className="text-center mt-12 text-xs text-slate-400">
          Version 3.1.0 (Local MVP) · Made with ❤️
        </p>
      </div>
    </main>
  )
}
