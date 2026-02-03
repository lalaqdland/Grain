'use client'

export default function EditorPage() {
  return (
    <main className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* 顶部导航 */}
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-bold">Grain 编辑器</h1>
            <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              下载文档
            </button>
          </div>

          {/* 编辑器区域 */}
          <div className="bg-white border border-gray-200 rounded-lg p-8 min-h-[600px]">
            <p className="text-gray-400 text-center py-20">
              请上传 .docx 文档开始编辑
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}

