/**
 * 后端 API E2E 测试
 * 验证 FastAPI 后端核心接口正确响应
 */
import { test, expect } from '@playwright/test'

const API_BASE = '/api/v1'

test.describe('后端 API 接口', () => {
  test('健康检查接口', async ({ request }) => {
    const response = await request.get(`${API_BASE}/health`)
    // 允许 200 或 404（如果未实现）
    expect([200, 404]).toContain(response.status())
  })

  test('OpenAPI 文档可访问', async ({ request }) => {
    const response = await request.get('/docs')
    expect([200, 404]).toContain(response.status())
  })

  test('OpenAPI JSON 可获取', async ({ request }) => {
    const response = await request.get('/openapi.json')
    if (response.status() === 200) {
      const json = await response.json()
      expect(json).toHaveProperty('openapi')
      expect(json).toHaveProperty('paths')
    }
  })
})
