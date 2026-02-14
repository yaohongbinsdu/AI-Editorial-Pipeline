import { test, expect } from '@playwright/test'

test.describe('RSS Sources Page', () => {
  test('sources page loads and shows table', async ({ page }) => {
    await page.goto('/sources')
    await expect(page.locator('h1')).toContainText('RSS')
    // Table header should be visible
    await expect(page.locator('table')).toBeVisible()
  })

  test('add source form has required fields', async ({ page }) => {
    await page.goto('/sources')
    // Click add button to show form
    const addBtn = page.locator('button', { hasText: /添加|新增|Add/ })
    if (await addBtn.isVisible()) {
      await addBtn.click()
      // Form fields should appear
      await expect(page.locator('input[placeholder*="URL"], input[name="url"]')).toBeVisible()
    }
  })

  test('sources list displays source names', async ({ page }) => {
    await page.goto('/sources')
    await page.waitForLoadState('networkidle')
    // If sources exist, the table should have rows
    const rows = page.locator('table tbody tr')
    const count = await rows.count()
    if (count > 0) {
      // First row should have text content
      const firstRow = rows.first()
      const text = await firstRow.textContent()
      expect(text!.length).toBeGreaterThan(0)
    }
  })
})
