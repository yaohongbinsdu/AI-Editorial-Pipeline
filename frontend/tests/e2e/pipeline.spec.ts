import { test, expect } from '@playwright/test'

test.describe('Pipeline Page', () => {
  test('pipeline page loads with status and controls', async ({ page }) => {
    await page.goto('/pipeline')
    await expect(page.locator('h1')).toContainText('流水线')
    // Trigger button should be visible
    await expect(page.locator('button', { hasText: /手动触发/ })).toBeVisible()
    // Refresh button should be visible
    await expect(page.locator('button', { hasText: /刷新/ })).toBeVisible()
  })

  test('pipeline shows step statistics section', async ({ page }) => {
    await page.goto('/pipeline')
    await expect(page.locator('text=24小时步骤统计')).toBeVisible()
  })

  test('pipeline shows run history section', async ({ page }) => {
    await page.goto('/pipeline')
    await expect(page.locator('text=执行记录')).toBeVisible()
  })

  test('trigger button can be clicked', async ({ page }) => {
    await page.goto('/pipeline')
    const triggerBtn = page.locator('button', { hasText: /手动触发/ })
    await expect(triggerBtn).toBeEnabled()
  })
})
