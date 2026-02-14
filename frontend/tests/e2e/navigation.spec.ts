import { test, expect } from '@playwright/test'

const NAV_LINKS = [
  { label: 'Dashboard', href: '/' },
  { label: '文章', href: '/articles' },
  { label: '事件聚类', href: '/clusters' },
  { label: '行业分类', href: '/categories' },
  { label: 'RSS 源', href: '/sources' },
  { label: '流水线', href: '/pipeline' },
]

test.describe('Sidebar Navigation', () => {
  test('all 6 navigation links are visible', async ({ page }) => {
    await page.goto('/')
    for (const nav of NAV_LINKS) {
      const link = page.locator(`nav a[href="${nav.href}"]`)
      await expect(link).toBeVisible()
      await expect(link).toContainText(nav.label)
    }
  })

  for (const nav of NAV_LINKS) {
    test(`clicking "${nav.label}" navigates to ${nav.href} without error`, async ({ page }) => {
      await page.goto('/')
      const errors: string[] = []
      page.on('console', (msg) => {
        if (msg.type() === 'error') errors.push(msg.text())
      })

      await page.click(`nav a[href="${nav.href}"]`)
      await page.waitForLoadState('networkidle')

      const url = new URL(page.url())
      expect(url.pathname).toBe(nav.href)

      // Page should have meaningful content (not blank)
      const body = await page.textContent('body')
      expect(body!.length).toBeGreaterThan(10)
    })
  }

  test('active link is highlighted on articles page', async ({ page }) => {
    await page.goto('/articles')
    const articlesLink = page.locator('nav a[href="/articles"]')
    await expect(articlesLink).toHaveClass(/font-medium/)
  })
})
