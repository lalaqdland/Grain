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

test('paragraph rewrite shows options and applies selected option to export', async ({ page }) => {
  const originalText = 'This is the original paragraph text.'
  const rewrittenText = 'This is the rewritten paragraph version.'

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'grain-e2e-'))
  const docPath = path.join(tempDir, 'paragraph-rewrite.docx')
  createDocxFile(docPath, originalText)

  try {
    await page.route('**/api/v1/rewrite', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: 'mocked',
          options: [rewrittenText, 'fallback-option-2', 'fallback-option-3'],
          mode: 'plagiarism',
          language: 'en',
          unit: 'paragraph',
          meta: [{ source: 'deepseek' }, { source: 'deepseek' }, { source: 'deepseek' }],
        }),
      })
    })

    await page.goto('/')
    await page.locator('input[type="file"]').setInputFiles(docPath)

    await expect(page.getByText('共 1 个段落')).toBeVisible()

    // Hover to reveal paragraph rewrite button
    const paragraphContainer = page.locator('div.group').first()
    await paragraphContainer.hover()

    // Click "改段" button
    const rewriteButton = page.getByRole('button', { name: '改段' })
    await expect(rewriteButton).toBeVisible()
    await rewriteButton.click()

    // Options should appear
    await expect(page.getByText(rewrittenText)).toBeVisible()
    await expect(page.getByText('选择一个段落改写版本：')).toBeVisible()

    // Select the first option
    await page.getByText(rewrittenText).click()

    // Paragraph should be updated
    await expect(paragraphContainer.locator('p').first()).toHaveText(rewrittenText)

    // Trigger export and verify payload
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
    expect(modifiedValues).toEqual([rewrittenText])
    expect(download.suggestedFilename()).toContain('modified_')
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true })
  }
})

test('export with invalid paragraph ID shows descriptive error message', async ({ page }) => {
  const originalText = 'Valid paragraph text.'

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'grain-e2e-'))
  const docPath = path.join(tempDir, 'invalid-export.docx')
  createDocxFile(docPath, originalText)

  try {
    await page.route('**/api/v1/export', async (route) => {
      // Return 400 with invalid paragraph ID
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: {
            message: '部分段落ID不存在，导出已中止',
            failed_ids: ['para_nonexistent_123'],
            applied_ids: [],
          },
        }),
      })
    })

    await page.goto('/')
    await page.locator('input[type="file"]').setInputFiles(docPath)

    await expect(page.getByText('共 1 个段落')).toBeVisible()

    // Trigger export (should fail due to invalid ID)
    await page.getByRole('button', { name: '导出文档' }).click()

    // Error message should mention the invalid IDs
    await expect(page.getByText(/para_nonexistent_123/)).toBeVisible({ timeout: 5000 })
    await expect(page.getByText(/无效段落ID|不存在/).or(page.getByText(/failed_ids/))).toBeVisible({ timeout: 5000 })
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true })
  }
})
