import { execFileSync } from 'node:child_process'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import { expect, test } from '@playwright/test'

function createDocxFile(filePath: string, paragraphText: string): void {
  const script = `
from docx import Document
import sys

doc = Document()
doc.add_paragraph(sys.argv[2])
doc.save(sys.argv[1])
`
  execFileSync('python', ['-c', script, filePath, paragraphText], { stdio: 'ignore' })
}

test('sentence rewrite uses precise offset and export payload matches page content', async ({ page }) => {
  const repeatedSentence = 'Repeat sentence.'
  const paragraphText = `${repeatedSentence} Keep context. ${repeatedSentence}`
  const rewrittenSentence = 'Humanized rewritten sentence.'
  const expectedParagraph = `${repeatedSentence} Keep context. ${rewrittenSentence}`

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'grain-e2e-'))
  const docPath = path.join(tempDir, 'repeat-offset.docx')
  createDocxFile(docPath, paragraphText)

  let rewriteRequestBody: Record<string, unknown> | undefined

  try {
    await page.route('**/api/v1/rewrite', async (route) => {
      rewriteRequestBody = (route.request().postDataJSON() as Record<string, unknown>) || {}
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: 'mocked',
          options: [rewrittenSentence, 'fallback-option-2', 'fallback-option-3'],
          mode: 'plagiarism',
          language: 'en',
          unit: 'sentence',
          meta: [{ source: 'deepseek' }, { source: 'deepseek' }, { source: 'deepseek' }],
        }),
      })
    })

    await page.goto('/')
    await page.locator('input[type="file"]').setInputFiles(docPath)

    await expect(page.getByText('共 1 个段落')).toBeVisible()
    const paragraph = page.locator('div.group').first().locator('p').first()
    await expect(paragraph).toBeVisible()
    await expect(paragraph).toHaveText(paragraphText)

    await paragraph.evaluate((node, sentence) => {
      const textNode = node.firstChild
      if (!textNode || textNode.nodeType !== Node.TEXT_NODE) {
        throw new Error('paragraph text node missing')
      }

      const fullText = node.textContent || ''
      const first = fullText.indexOf(sentence)
      const second = fullText.indexOf(sentence, first + sentence.length)
      if (second < 0) {
        throw new Error('second sentence occurrence not found')
      }

      const range = document.createRange()
      range.setStart(textNode, second)
      range.setEnd(textNode, second + sentence.length)

      const selection = window.getSelection()
      if (!selection) {
        throw new Error('window selection unavailable')
      }

      selection.removeAllRanges()
      selection.addRange(range)
      node.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
    }, repeatedSentence)

    await expect(page.getByText('已选中句子（可改写）')).toBeVisible()
    await page.getByRole('button', { name: '生成句子候选' }).click()
    await expect(page.getByText(rewrittenSentence)).toBeVisible()
    await page.getByText(rewrittenSentence).click()

    expect(rewriteRequestBody).toBeDefined()
    expect(rewriteRequestBody?.unit).toBe('sentence')
    expect(rewriteRequestBody?.text).toBe(repeatedSentence)
    expect(rewriteRequestBody?.option_count).toBe(3)

    await expect(paragraph).toHaveText(expectedParagraph)

    const [download, exportRequest] = await Promise.all([
      page.waitForEvent('download'),
      page.waitForRequest(
        (request) => request.url().includes('/api/v1/export') && request.method() === 'POST'
      ),
      page.getByRole('button', { name: '导出文档' }).click(),
    ])

    const payload = exportRequest.postDataJSON() as {
      doc_id: string
      modifications: Record<string, string>
    }

    expect(payload.doc_id.startsWith('doc_')).toBeTruthy()
    const modifiedValues = Object.values(payload.modifications)
    expect(modifiedValues).toEqual([expectedParagraph])
    expect(download.suggestedFilename()).toContain('modified_')
    expect(await download.path()).toBeTruthy()
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true })
  }
})
