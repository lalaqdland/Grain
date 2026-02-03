'use client'

import { useEditorStore } from '@/store/editorStore'
import Paragraph from './Paragraph'

export default function Editor() {
  const { document, updateParagraph, resetParagraph } = useEditorStore()

  if (!document) {
    return null
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* 文档标题 */}
      <div className="mb-6 pb-4 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-800">{document.filename}</h2>
        <p className="text-sm text-gray-500 mt-1">
          共 {document.content.length} 个段落
        </p>
      </div>

      {/* 段落列表 */}
      <div className="space-y-2">
        {document.content.map((paragraph) => (
          <Paragraph
            key={paragraph.id}
            paragraph={paragraph}
            onUpdate={updateParagraph}
            onReset={resetParagraph}
          />
        ))}
      </div>
    </div>
  )
}

