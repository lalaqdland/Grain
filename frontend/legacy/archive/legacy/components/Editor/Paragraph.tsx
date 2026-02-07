'use client'

import { Paragraph as ParagraphType } from '@/types'

interface ParagraphProps {
  paragraph: ParagraphType
  onUpdate?: (id: string, text: string) => void
  onReset?: (id: string) => void
}

export default function Paragraph({ paragraph, onUpdate, onReset }: ParagraphProps) {
  return (
    <div className="paragraph-container relative group mb-4">
      {/* 悬停指示条 */}
      <div className="hover-indicator"></div>
      
      {/* 段落内容 */}
      <div
        className={`
          p-4 rounded-lg transition-all duration-200
          ${paragraph.isModified ? 'paragraph-highlight' : 'hover:bg-gray-50'}
        `}
      >
        <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
          {paragraph.text}
        </p>
        
        {/* 撤销按钮 */}
        {paragraph.isModified && onReset && (
          <button
            onClick={() => onReset(paragraph.id)}
            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity
                     px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm text-gray-700"
            title="撤销修改"
          >
            ↩ 撤销
          </button>
        )}
      </div>
    </div>
  )
}

