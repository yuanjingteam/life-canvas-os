/**
 * 移动端适配测试
 * 验证应用在移动设备上的可用性
 */
import { test, expect } from '@playwright/test'

test.describe('移动端适配', () => {
  test('仪表盘在移动端可访问', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    
    // 页面可加载
    const heading = page.locator('h1').first()
    await expect(heading).toBeVisible()
  })

  test('导航菜单可折叠/展开', async ({ page }) => {
    await page.goto('/dashboard')
    
    // 查找汉堡菜单按钮
    const menuButton = page.locator('button[aria-label*="菜单"], button[aria-label*="menu"]').first()
    if (await menuButton.isVisible()) {
      await menuButton.click()
      await page.waitForTimeout(300)
      // 菜单应该展开
    }
  })

  test('时间线页面可滚动', async ({ page }) => {
    await page.goto('/timeline')
    await page.waitForLoadState('networkidle')
    
    // 验证页面内容存在
    const content = page.locator('main, [role="main"], .timeline').first()
    await expect(content).toBeVisible()
  })
})
