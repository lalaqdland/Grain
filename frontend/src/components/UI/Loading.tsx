'use client'

export default function Loading() {
  return (
    <div className="flex items-center justify-center gap-2">
      <div className="wave-loading">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <span className="text-gray-600">加载中...</span>
    </div>
  )
}

