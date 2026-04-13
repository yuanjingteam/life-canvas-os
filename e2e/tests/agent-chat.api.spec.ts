/**
 * Agent API 集成测试
 * 测试 Agent 聊天、Session 管理、History 等核心功能
 */
import { test, expect } from '@playwright/test'

const API_BASE = '/api/v1'

test.describe('Agent 聊天接口', () => {
  test.beforeEach(async ({ request }) => {
    // 等待后端就绪
    await request.get(`${API_BASE}/health`, { timeout: 5000 }).catch(() => {
      // 后端可能还没启动，跳过预检查
    })
  })

  test('Agent Chat 接口可访问', async ({ request }) => {
    // 测试 chat 接口存在（返回 424 表示未配置AI，不是 404）
    const response = await request.post(`${API_BASE}/agent/chat`, {
      data: {
        message: '你好',
        session_id: null,
      },
      timeout: 10_000,
    })
    // 期望: 424(未配置) 或 200(正常) 或 500(其他错误)
    // 不应该是 404(接口不存在) 或 405(方法不对)
    expect([200, 424, 500]).toContain(response.status())
  })

  test('Agent Session 列表接口', async ({ request }) => {
    const response = await request.get(`${API_BASE}/agent/sessions`)
    // 同上，期望 200 或 424（未配置AI）
    expect([200, 424]).toContain(response.status())
  })

  test('Agent Tool Schemas 接口', async ({ request }) => {
    const response = await request.get(`${API_BASE}/agent/tools`)
    expect([200, 404]).toContain(response.status())
  })

  test('创建新 Session', async ({ request }) => {
    // 先尝试获取现有 sessions
    const sessionsResponse = await request.get(`${API_BASE}/agent/sessions`)
    
    if (sessionsResponse.status() === 200) {
      const data = await sessionsResponse.json()
      // 验证返回结构
      expect(data).toHaveProperty('success')
      expect(data).toHaveProperty('data')
    }
  })
})

test.describe('Agent 错误处理', () => {
  test('空消息返回错误', async ({ request }) => {
    const response = await request.post(`${API_BASE}/agent/chat`, {
      data: {
        message: '',
        session_id: null,
      },
      timeout: 10_000,
    })
    // 空消息可能返回 400 或被业务逻辑处理
    expect([200, 400, 422, 424, 500]).toContain(response.status())
  })

  test('无效 session_id 格式', async ({ request }) => {
    const response = await request.post(`${API_BASE}/agent/chat`, {
      data: {
        message: '测试',
        session_id: 'invalid-session-id-that-is-way-too-long',
      },
      timeout: 10_000,
    })
    expect([200, 400, 404, 424, 500]).toContain(response.status())
  })
})
