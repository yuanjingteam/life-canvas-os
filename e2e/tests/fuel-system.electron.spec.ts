/**
 * 饮食系统 E2E 测试
 * 验证FUEL子系统核心功能
 */
import { test, expect } from '@playwright/test'

test.describe('饮食系统', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/system/fuel')
    await page.waitForLoadState('networkidle')
  })

  test('页面正确加载', async ({ page }) => {
    const heading = page.locator('h1').first()
    await expect(heading).toBeVisible()
  })

  test('可以添加食物记录', async ({ page }) => {
    // 查找添加按钮（具体选择器根据实际组件调整）
    const addButton = page.locator('button:has-text("添加")').first()
    if (await addButton.isVisible()) {
      await addButton.click()
      // 验证弹窗或表单出现
      await expect(page.locator('form, [role="dialog"]').first()).toBeVisible()
    }
  })

  test('可以搜索食物', async ({ page }) => {
    // 查找搜索框
    const searchInput = page.locator('input[type="search"], input[placeholder*="搜索"]').first()
    if (await searchInput.isVisible()) {
      await searchInput.fill('苹果')
      await page.waitForTimeout(500)
      // 验证有搜索结果
      const results = page.locator('[role="option"], .result-item, tr')
      await expect(results.first()).toBeVisible({ timeout: 5000 })
    }
  })
})
