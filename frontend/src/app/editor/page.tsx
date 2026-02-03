'use client'

import { useEditorStore } from '@/store/editorStore'
import FileUploader from '@/components/Upload/FileUploader'
import Editor from '@/components/Editor/Editor'
import Link from 'next/link'

export default function EditorPage() {
  const { document, isLoading, error, clearDocument } = useEditorStore()

  return (
    <main className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* 顶部导航 */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-blue-600 hover:text-blue-700">
                ← 返回首页
              </Link>
              <h1 className="text-2xl font-bold">Grain 编辑器</h1>
            </div>
            
            {document && (
              <div className="flex gap-2">
                <button 
                  onClick={clearDocument}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  重新上传
                </button>
                <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  下载文档
                </button>
              </div>
            )}
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              ❌ {error}
            </div>
          )}

          {/* 加载状态 */}
          {isLoading && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg text-blue-700 text-center">
              <div className="wave-loading inline-flex">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="ml-3">正在上传和解析文档...</span>
            </div>
          )}

          {/* 编辑器区域 */}
          <div className="bg-white border border-gray-200 rounded-lg p-8 min-h-[600px]">
            {!document && !isLoading ? (
              <FileUploader />
            ) : (
              <Editor />
            )}
          </div>
        </div>
      </div>
    </main>
  )
}

