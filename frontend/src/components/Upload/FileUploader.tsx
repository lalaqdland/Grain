'use client'

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { api } from '@/lib/api'
import { useEditorStore } from '@/store/editorStore'
import { formatFileSize } from '@/lib/utils'

const MAX_FILE_SIZE = 10485760 // 10MB

export default function FileUploader() {
  const { setDocument, setLoading, setError } = useEditorStore()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    
    // 验证文件大小
    if (file.size > MAX_FILE_SIZE) {
      setError(`文件过大，最大支持 ${formatFileSize(MAX_FILE_SIZE)}`)
      return
    }

    // 开始上传
    setLoading(true)
    setError(null)

    try {
      const response = await api.uploadDocument(file)
      
      if (response.success && response.data) {
        const content = response.data.paragraphs.map((paragraph) => ({
          id: paragraph.id,
          text: paragraph.text,
          style: paragraph.style,
          isModified: paragraph.is_modified,
          originalText: paragraph.original_text ?? undefined,
        }))

        // 转换数据格式
        const document = {
          id: response.data.id,
          filename: response.data.filename,
          content,
          uploadedAt: response.data.uploaded_at
        }
        
        setDocument(document)
      } else {
        setError(response.message || '上传失败')
      }
    } catch (error: any) {
      console.error('Upload error:', error)
      setError(error.response?.data?.detail || '上传失败，请重试')
    } finally {
      setLoading(false)
    }
  }, [setDocument, setLoading, setError])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: MAX_FILE_SIZE,
    multiple: false
  })

  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
        transition-all duration-200
        ${isDragActive 
          ? 'border-blue-500 bg-blue-50' 
          : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        }
      `}
    >
      <input {...getInputProps()} />
      
      <div className="flex flex-col items-center gap-4">
        <div className="text-5xl">📄</div>
        
        {isDragActive ? (
          <p className="text-lg text-blue-600 font-medium">
            松开鼠标上传文件
          </p>
        ) : (
          <>
            <p className="text-lg text-gray-700 font-medium">
              拖拽 .docx 文件到此处，或点击选择文件
            </p>
            <p className="text-sm text-gray-500">
              支持格式：.docx | 最大文件大小：10MB
            </p>
          </>
        )}
        
        <button
          type="button"
          className="mt-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          选择文件
        </button>
      </div>
    </div>
  )
}

