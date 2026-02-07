'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import Image from 'next/image'
import { api, RewriteOptionMeta, RewriteUnit } from '@/lib/api'
import { formatFileSize } from '@/lib/utils'

type Mode = 'plagiarism' | 'ai_detection'
type Language = 'zh' | 'en'

interface Paragraph {
  id: string
  text: string
  style: string
  is_modified: boolean
  original_text?: string | null
}

interface DocumentState {
  id: string
  filename: string
  paragraphs: Paragraph[]
  total_paragraphs: number
}

interface SentenceSelection {
  paragraphId: string
  text: string
  startOffset: number
  endOffset: number
  paragraphSnapshot: string
}

interface RewriteOptionSet {
  options: string[]
  meta?: RewriteOptionMeta[]
  unit: RewriteUnit
  sourceText: string
  startOffset?: number
  endOffset?: number
  paragraphSnapshot?: string
}

const MAX_FILE_SIZE = 10485760 // 10MB
const CAPOO_IMAGES = [
  { src: '/images/capoo/capoo-01.webp', alt: 'Capoo 本猫照片 1', width: 3072, height: 4096 },
  { src: '/images/capoo/capoo-02.webp', alt: 'Capoo 本猫照片 2', width: 4096, height: 3072 },
  { src: '/images/capoo/capoo-03.webp', alt: 'Capoo 本猫照片 3', width: 3072, height: 4096 },
  { src: '/images/capoo/capoo-04.webp', alt: 'Capoo 本猫照片 4', width: 3072, height: 4096 },
]

function buildRewriteKey(
  paragraphId: string,
  unit: RewriteUnit,
  selection?: Pick<SentenceSelection, 'startOffset' | 'endOffset'>
): string {
  if (unit === 'sentence' && selection) {
    return `${paragraphId}:${unit}:${selection.startOffset}:${selection.endOffset}`
  }
  return `${paragraphId}:${unit}`
}

function detectLanguage(text: string): Language {
  const zhCount = (text.match(/[\u4e00-\u9fff]/g) || []).length
  const enCount = (text.match(/[a-zA-Z]/g) || []).length
  return enCount > zhCount ? 'en' : 'zh'
}

export default function Home() {
  const [mode, setMode] = useState<Mode>('plagiarism')
  const [document, setDocument] = useState<DocumentState | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hoveredParagraph, setHoveredParagraph] = useState<string | null>(null)
  const [rewritingTarget, setRewritingTarget] = useState<string | null>(null)
  const [rewriteOptions, setRewriteOptions] = useState<Record<string, RewriteOptionSet>>({})
  const [showOptions, setShowOptions] = useState<string | null>(null)
  const [sentenceSelection, setSentenceSelection] = useState<SentenceSelection | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    if (file.size > MAX_FILE_SIZE) {
      setError(`文件太大了！最大支持 ${formatFileSize(MAX_FILE_SIZE)}，您的文件是 ${formatFileSize(file.size)}`)
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await api.uploadDocument(file)
      if (response.success && response.data) {
        setDocument(response.data)
        setRewriteOptions({})
        setShowOptions(null)
        setSentenceSelection(null)
      } else {
        setError('上传失败了，请重试一下')
      }
    } catch (uploadError: any) {
      if (uploadError.code === 'ECONNREFUSED' || uploadError.message?.includes('Network Error')) {
        setError('❌ 无法连接到服务器\n请确保后端服务已启动（运行在 http://localhost:8001）')
      } else if (uploadError.response?.status === 404) {
        setError('❌ 上传接口未找到\n请检查后端服务是否正常运行')
      } else if (uploadError.response?.status === 413) {
        setError('❌ 文件太大了\n请选择小于10MB的文档')
      } else if (uploadError.response?.status === 400) {
        setError(uploadError.response?.data?.detail || '❌ 文件格式不对\n仅支持 .docx 格式的Word文档')
      } else {
        setError(uploadError.response?.data?.detail || `❌ 上传失败\n${uploadError.message || '未知错误，请重试'}`)
      }
    } finally {
      setIsLoading(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: MAX_FILE_SIZE,
    multiple: false,
    noClick: !!document,
  })

  const handleReset = () => {
    setDocument(null)
    setError(null)
    setRewriteOptions({})
    setShowOptions(null)
    setSentenceSelection(null)
  }

  const handleSentenceSelection = (
    paragraphElement: HTMLParagraphElement,
    paragraphId: string,
    paragraphText: string
  ) => {
    const selection = window.getSelection()
    if (!selection || selection.isCollapsed || selection.rangeCount === 0) {
      return
    }

    const range = selection.getRangeAt(0)
    if (!paragraphElement.contains(range.startContainer) || !paragraphElement.contains(range.endContainer)) {
      setError('请选择同一段落中的句子')
      return
    }

    const selectedText = range.toString()
    if (!selectedText.trim()) {
      return
    }

    const startRange = window.document.createRange()
    startRange.selectNodeContents(paragraphElement)
    startRange.setEnd(range.startContainer, range.startOffset)
    const startOffset = startRange.toString().length
    const endOffset = startOffset + selectedText.length

    if (startOffset < 0 || endOffset <= startOffset || endOffset > paragraphText.length) {
      setError('选区无效，请重新选择句子')
      return
    }

    if (paragraphText.slice(startOffset, endOffset) !== selectedText) {
      setError('选区无效，请重新选择句子')
      return
    }

    setSentenceSelection({
      paragraphId,
      text: selectedText,
      startOffset,
      endOffset,
      paragraphSnapshot: paragraphText,
    })
    setError(null)
    setShowOptions(null)
  }

  const requestRewrite = async (params: {
    paragraphId: string
    text: string
    unit: RewriteUnit
    sourceText: string
    rewriteKey?: string
    startOffset?: number
    endOffset?: number
    paragraphSnapshot?: string
  }) => {
    const key = params.rewriteKey || buildRewriteKey(params.paragraphId, params.unit)
    setRewritingTarget(key)
    setError(null)

    try {
      const response = await api.rewriteText({
        text: params.text,
        mode,
        language: detectLanguage(params.text),
        unit: params.unit,
        option_count: 3,
      })

      if (response.success && response.options?.length > 0) {
        setRewriteOptions((prev) => ({
          ...prev,
          [key]: {
            options: response.options,
            meta: response.meta,
            unit: params.unit,
            sourceText: params.sourceText,
            startOffset: params.startOffset,
            endOffset: params.endOffset,
            paragraphSnapshot: params.paragraphSnapshot,
          },
        }))
        setShowOptions(key)
      } else {
        setError('❌ 改写失败，请重试')
      }
    } catch (rewriteError: any) {
      if (rewriteError.code === 'ECONNREFUSED' || rewriteError.message?.includes('Network Error')) {
        setError('❌ 无法连接到服务器\n请确保后端服务已启动（http://localhost:8001）')
      } else if (rewriteError.response?.status === 404) {
        setError('❌ 改写接口未找到\n可能原因：后端服务未正确启动或路由配置错误')
      } else if (rewriteError.response?.status === 400) {
        setError(`❌ 请求参数错误\n${rewriteError.response?.data?.detail || '请检查输入内容'}`)
      } else if (rewriteError.response?.status === 500) {
        setError(`❌ 服务器错误\n${rewriteError.response?.data?.detail || '模型调用失败，请检查服务配置'}`)
      } else {
        setError(`❌ 改写失败\n${rewriteError.response?.data?.detail || rewriteError.message || '未知错误，请重试'}`)
      }
    } finally {
      setRewritingTarget(null)
    }
  }

  const handleRewriteParagraph = (paragraphId: string, text: string) => {
    requestRewrite({
      paragraphId,
      text,
      unit: 'paragraph',
      sourceText: text,
    })
  }

  const handleRewriteSentence = () => {
    if (!sentenceSelection) return
    const rewriteKey = buildRewriteKey(sentenceSelection.paragraphId, 'sentence', sentenceSelection)
    requestRewrite({
      paragraphId: sentenceSelection.paragraphId,
      text: sentenceSelection.text,
      unit: 'sentence',
      sourceText: sentenceSelection.text,
      rewriteKey,
      startOffset: sentenceSelection.startOffset,
      endOffset: sentenceSelection.endOffset,
      paragraphSnapshot: sentenceSelection.paragraphSnapshot,
    })
  }

  const handleSelectOption = (paragraphId: string, optionText: string, key: string) => {
    if (!document) return
    const optionSet = rewriteOptions[key]
    if (!optionSet) return

    let replacementFailed = false

    const updatedParagraphs = document.paragraphs.map((para) => {
      if (para.id !== paragraphId) return para

      const oldText = para.text
      let newText = optionText

      if (optionSet.unit === 'sentence') {
        if (
          typeof optionSet.startOffset !== 'number' ||
          typeof optionSet.endOffset !== 'number' ||
          optionSet.endOffset <= optionSet.startOffset
        ) {
          replacementFailed = true
          return para
        }

        if (optionSet.paragraphSnapshot !== undefined && optionSet.paragraphSnapshot !== oldText) {
          replacementFailed = true
          return para
        }

        const sourceSlice = oldText.slice(optionSet.startOffset, optionSet.endOffset)
        if (sourceSlice !== optionSet.sourceText) {
          replacementFailed = true
          return para
        }

        newText = `${oldText.slice(0, optionSet.startOffset)}${optionText}${oldText.slice(optionSet.endOffset)}`
      }

      return {
        ...para,
        text: newText,
        is_modified: true,
        original_text: para.original_text ?? oldText,
      }
    })

    if (replacementFailed) {
      setError('❌ 句子替换失败：选区已变化，请重新选择后再试')
      return
    }

    setDocument({
      ...document,
      paragraphs: updatedParagraphs,
    })
    setShowOptions(null)
    if (sentenceSelection?.paragraphId === paragraphId) {
      setSentenceSelection(null)
    }
  }

  const handleExport = async () => {
    if (!document) return

    try {
      const modifications = Object.fromEntries(
        document.paragraphs.filter((para) => para.is_modified).map((para) => [para.id, para.text])
      )

      const blob = await api.exportDocument(document.id, modifications)
      const url = window.URL.createObjectURL(new Blob([blob]))
      const link = window.document.createElement('a')
      link.href = url
      link.setAttribute('download', `modified_${document.filename}`)
      window.document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (exportError: any) {
      if (exportError?.response?.status === 400 && exportError.response.data instanceof Blob) {
        try {
          const payloadText = await exportError.response.data.text()
          const payload = JSON.parse(payloadText)
          const failedIds = payload?.detail?.failed_ids || []
          setError(`❌ 导出失败：存在无效段落ID\n${failedIds.join(', ')}`)
          return
        } catch {
          // ignore blob parse failures and use fallback error
        }
      }
      setError(`😢 导出失败，请重试\n${exportError.response?.data?.detail || exportError.message || ''}`)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
      <div className="container mx-auto px-6 py-12 max-w-7xl">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-3 tracking-tight">
            <span className="bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
              Grain
            </span>
          </h1>
          <p className="text-lg text-slate-600">守拙 · The AI Humanizer & Academic Shield</p>
        </div>

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

        {error && (
          <div className="max-w-3xl mx-auto mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl text-red-700 text-sm whitespace-pre-line">
            {error}
          </div>
        )}

        <div className="max-w-5xl mx-auto">
          {!document ? (
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
                    <p className="text-xl text-slate-700 font-medium">正在上传和解析文档...</p>
                    <div className="flex justify-center gap-2">
                      <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                ) : isDragActive ? (
                  <p className="text-xl text-violet-600 font-medium">松开鼠标上传文件</p>
                ) : (
                  <>
                    <div className="space-y-2">
                      <p className="text-xl text-slate-700 font-medium">拖拽 Word 文档到这里</p>
                      <p className="text-sm text-slate-500">或点击选择文件</p>
                    </div>

                    <button
                      type="button"
                      className="mt-4 px-8 py-3 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-xl font-medium hover:shadow-lg transition-all duration-200 hover:scale-105"
                    >
                      选择文件
                    </button>

                    <p className="text-xs text-slate-400 mt-4">仅支持 .docx 格式 · 最大 10MB</p>
                    <p className="text-xs text-slate-500 mt-2 max-w-md mx-auto">
                      💡 为了保证完美的排版格式，请在 Word 中将文件&apos;另存为&apos; .docx 格式后再上传
                    </p>
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-3xl shadow-lg border border-slate-200 overflow-hidden">
              <div className="px-8 py-6 border-b border-slate-200 bg-slate-50">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-800">{document.filename}</h2>
                    <p className="text-sm text-slate-500 mt-1">共 {document.total_paragraphs} 个段落</p>
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

              <div className="p-8 space-y-4 max-h-[600px] overflow-y-auto">
                {document.paragraphs.map((para) => {
                  const paragraphKey = buildRewriteKey(para.id, 'paragraph')
                  const sentenceKey = sentenceSelection?.paragraphId === para.id
                    ? buildRewriteKey(para.id, 'sentence', sentenceSelection)
                    : buildRewriteKey(para.id, 'sentence')
                  const visibleKey = showOptions === paragraphKey || showOptions === sentenceKey ? showOptions : null
                  const activeOptions = visibleKey ? rewriteOptions[visibleKey] : null

                  return (
                    <div
                      key={para.id}
                      onMouseEnter={() => setHoveredParagraph(para.id)}
                      onMouseLeave={() => setHoveredParagraph(null)}
                      className={`
                        group relative pl-6 pr-4 py-4 rounded-xl transition-all duration-200 cursor-pointer
                        ${para.is_modified ? 'bg-green-50' : 'hover:bg-slate-50'}
                      `}
                    >
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

                      <div className="flex items-start justify-between gap-4">
                        <p
                          onMouseUp={(event) => handleSentenceSelection(event.currentTarget, para.id, para.text)}
                          className={`
                            flex-1 leading-relaxed whitespace-pre-wrap select-text
                            ${para.style === 'Title' ? 'text-xl font-bold text-slate-900' : ''}
                            ${para.style === 'Heading 1' ? 'text-lg font-semibold text-slate-800' : ''}
                            ${para.style === 'Normal' ? 'text-slate-700' : ''}
                          `}
                        >
                          {para.text}
                        </p>

                        {hoveredParagraph === para.id && (
                          <div className="flex gap-2">
                            {rewritingTarget !== paragraphKey && (
                              <button
                                onClick={() => handleRewriteParagraph(para.id, para.text)}
                                className={`
                                  px-4 py-2 rounded-lg text-white text-sm font-medium
                                  transition-all duration-200 hover:shadow-md whitespace-nowrap
                                  ${mode === 'plagiarism'
                                    ? 'bg-gradient-to-r from-rose-500 to-pink-500'
                                    : 'bg-gradient-to-r from-amber-500 to-orange-500'
                                  }
                                `}
                              >
                                改段
                              </button>
                            )}

                            {sentenceSelection?.paragraphId === para.id && rewritingTarget !== sentenceKey && (
                              <button
                                onClick={handleRewriteSentence}
                                className="px-4 py-2 rounded-lg text-white text-sm font-medium transition-all duration-200 hover:shadow-md whitespace-nowrap bg-gradient-to-r from-violet-600 to-indigo-600"
                              >
                                改句
                              </button>
                            )}

                            {(rewritingTarget === paragraphKey || rewritingTarget === sentenceKey) && (
                              <div className="flex items-center gap-2 px-4 py-2">
                                <div className="flex gap-1">
                                  <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                  <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                  <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {sentenceSelection?.paragraphId === para.id && (
                        <div className="mt-3 rounded-lg border border-violet-200 bg-violet-50 px-4 py-3">
                          <p className="text-xs text-violet-700 font-medium mb-1">已选中句子（可改写）</p>
                          <p className="text-sm text-violet-900 leading-relaxed">{sentenceSelection.text}</p>
                          <div className="mt-2 flex gap-2">
                            <button
                              onClick={handleRewriteSentence}
                              className="px-3 py-1.5 text-xs rounded-md bg-violet-600 text-white hover:bg-violet-700 transition-colors"
                            >
                              生成句子候选
                            </button>
                            <button
                              onClick={() => setSentenceSelection(null)}
                              className="px-3 py-1.5 text-xs rounded-md bg-white border border-violet-300 text-violet-700 hover:bg-violet-100 transition-colors"
                            >
                              清除选句
                            </button>
                          </div>
                        </div>
                      )}

                      {activeOptions && visibleKey && (
                        <div className="mt-4 space-y-2 animate-in fade-in slide-in-from-top-2 duration-300">
                          <p className="text-xs text-slate-500 font-medium mb-2">
                            选择一个{activeOptions.unit === 'sentence' ? '句子' : '段落'}改写版本：
                          </p>
                          {activeOptions.options.map((option, index) => (
                            <div
                              key={`${visibleKey}-${index}`}
                              onClick={() => handleSelectOption(para.id, option, visibleKey)}
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
                                <p className="flex-1 text-sm text-slate-700 leading-relaxed">{option}</p>
                                {activeOptions.meta?.[index]?.source && (
                                  <span className="text-[10px] uppercase tracking-wide px-2 py-1 rounded bg-slate-100 text-slate-500">
                                    {activeOptions.meta[index].source}
                                  </span>
                                )}
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
                  )
                })}
              </div>
            </div>
          )}
        </div>

        {!document && (
          <div className="mt-16 max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-white rounded-2xl border border-slate-200 hover:shadow-md transition-shadow">
                <div className="text-3xl mb-3">📄</div>
                <h3 className="font-semibold text-slate-800 mb-2">格式神圣</h3>
                <p className="text-sm text-slate-600">
                  XML骨架置换技术
                  <br />
                  确保格式分毫不差
                </p>
              </div>
              <div className="text-center p-6 bg-white rounded-2xl border border-slate-200 hover:shadow-md transition-shadow">
                <div className="text-3xl mb-3">🖥️</div>
                <h3 className="font-semibold text-slate-800 mb-2">外屏协同</h3>
                <p className="text-sm text-slate-600">
                  配合系统分屏
                  <br />
                  专注极致编辑体验
                </p>
              </div>
              <div className="text-center p-6 bg-white rounded-2xl border border-slate-200 hover:shadow-md transition-shadow">
                <div className="text-3xl mb-3">🤖</div>
                <h3 className="font-semibold text-slate-800 mb-2">辅助驾驶</h3>
                <p className="text-sm text-slate-600">
                  支持改句与改段
                  <br />
                  人工选择候选后再替换
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="mt-16 max-w-5xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-slate-800">Capoo 本猫</h2>
            <p className="text-sm text-slate-500 mt-2">四张咖波写真，献给 Grain 用户</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {CAPOO_IMAGES.map((image, index) => (
              <div
                key={image.src}
                className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
              >
                <Image
                  src={image.src}
                  alt={image.alt}
                  width={image.width}
                  height={image.height}
                  className="w-full h-auto object-cover"
                  priority={index === 0}
                  loading={index === 0 ? undefined : 'lazy'}
                />
              </div>
            ))}
          </div>
        </div>

        <p className="text-center mt-12 text-xs text-slate-400">Version 3.1.2 (P0 Offset + E2E) · Made with ❤️</p>
      </div>
    </main>
  )
}
