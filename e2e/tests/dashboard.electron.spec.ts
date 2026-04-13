/**
 * Dashboard E2E 测试
 * 验证仪表盘页面正常加载，各区块数据正确显示
 */
import { test, expect } from '@playwright/test'

test.describe('仪表盘页面', () => {
  test.beforeEach(async ({ page }) => {
    // 访问仪表盘
    await page.goto('/dashboard')
    // 等待页面加载完成
    await page.waitForLoadState('networkidle')
  })

  test('页面标题正确', async ({ page }) => {
    // 验证页面有标题
    const heading = page.locator('h1').first()
    await expect(heading).toBeVisible()
  })

  test('导航菜单可见', async ({ page }) => {
    // 验证主导航存在
    const nav = page.locator('nav').first()
    await expect(nav).toBeVisible()
  })

  test('可以导航到饮食系统', async ({ page }) => {
    // 点击导航到饮食系统
    await page.click('a[href*="fuel"]')
    // 验证 URL 变化
    await expect(page).toHaveURL(/.*\/system\/fuel/)
  })

  test('可以导航到日记', async ({ page }) => {
    await page.click('a[href*="journal"]')
    await expect(page).toHaveURL(/.*\/journal/)
  })

  test('可以导航到时间线', async ({ page }) => {
    await page.click('a[href*="timeline"]')
    await expect(page).toHaveURL(/.*\/timeline/)
  })

  test('可以导航到设置', async ({ page }) => {
    await page.click('a[href*="settings"]')
    await expect(page).toHaveURL(/.*\/settings/)
  })
})
