/**
 * Agent API Hook
 */

import { useCallback } from 'react'
import { apiRequest } from '~/renderer/api/client'

// 会话 ID 存储键
const SESSION_ID_STORAGE_KEY = 'life_canvas_agent_session_id'

// 会话 ID 列表存储键
const SESSION_ID_LIST_STORAGE_KEY = 'life_canvas_agent_session_ids'

// 从 localStorage 获取或创建会话 ID
function getSessionId(): string {
  let sessionId = localStorage.getItem(SESSION_ID_STORAGE_KEY)
  if (!sessionId) {
    sessionId = generateSessionId()
    localStorage.setItem(SESSION_ID_STORAGE_KEY, sessionId)
  }
  return sessionId
}

// 生成新的会话 ID
function generateSessionId(): string {
  return `sess_${Math.random().toString(36).substring(2, 14)}`
}

// 设置会话 ID 到 localStorage
function setSessionId(sessionId: string): void {
  localStorage.setItem(SESSION_ID_STORAGE_KEY, sessionId)
  // 同时保存到会话列表
  saveSessionToHistory(sessionId)
}

// 从 localStorage 清除当前会话 ID
function clearSessionId(): void {
  localStorage.removeItem(SESSION_ID_STORAGE_KEY)
}

// 保存会话 ID 到历史列表
function saveSessionToHistory(sessionId: string): void {
  try {
    const existing = localStorage.getItem(SESSION_ID_LIST_STORAGE_KEY)
    const sessionList: string[] = existing ? JSON.parse(existing) : []
    if (!sessionList.includes(sessionId)) {
      sessionList.unshift(sessionId) // 新会话放到列表开头
      localStorage.setItem(
        SESSION_ID_LIST_STORAGE_KEY,
        JSON.stringify(sessionList)
      )
    }
  } catch (error) {
    console.error('Failed to save session to history:', error)
  }
}

// 获取会话历史列表
function getSessionHistory(): string[] {
  try {
    const existing = localStorage.getItem(SESSION_ID_LIST_STORAGE_KEY)
    return existing ? JSON.parse(existing) : []
  } catch (error) {
    console.error('Failed to get session history:', error)
    return []
  }
}

// 从会话历史列表中移除
function removeSessionFromHistory(sessionId: string): void {
  try {
    const existing = localStorage.getItem(SESSION_ID_LIST_STORAGE_KEY)
    const sessionList: string[] = existing ? JSON.parse(existing) : []
    const filtered = sessionList.filter(id => id !== sessionId)
    localStorage.setItem(SESSION_ID_LIST_STORAGE_KEY, JSON.stringify(filtered))
  } catch (error) {
    console.error('Failed to remove session from history:', error)
  }
}

export interface ChatResponse {
  response: string
  action_taken?: {
    id?: number
    title?: string
    content?: string
    mood?: string
    tags?: string[]
    created_at?: string
    [key: string]: unknown
  }
  requires_confirmation?: boolean
  confirmation_id?: string
  confirmation_message?: string
  session_id?: string
}

export interface ConfirmRequest {
  session_id: string
  confirmation_id: string
  confirmed: boolean
  code?: string
}

/**
 * Agent API Hook
 */
export function useAgentApi() {
  /**
   * 发送聊天请求
   */
  const chat = useCallback(async (message: string): Promise<ChatResponse> => {
    const sessionId = getSessionId()
    const response = await apiRequest('/api/agent/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    })

    const result = await response.json()

    if (response.ok && result.code === 200) {
      return result.data as ChatResponse
    }

    throw new Error(result.message || '发送消息失败')
  }, [])

  /**
   * 发送流式聊天请求
   * 返回一个 AsyncIterator 用于接收流式响应
   */
  const chatStream = useCallback(async function* (message: string, sessionId: string) {
    const response = await apiRequest('/api/agent/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error('流式请求失败')
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法读取响应流')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // 解析 SSE 格式
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留不完整行

        for (const line of lines) {
          const trimmedLine = line.trim()
          if (trimmedLine.startsWith('data: ')) {
            const data = trimmedLine.slice(6)
            if (data === '[DONE]') {
              yield { type: 'done', data: null }
              return
            }
            try {
              const parsed = JSON.parse(data)
              yield parsed
            } catch {
              // JSON 解析失败，跳过
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  }, [])

  // 包装函数，用于在组件中调用
  const chatStreamWrapper = useCallback(async function* (message: string) {
    const sessionId = getSessionId()
    const stream = chatStream(message, sessionId)
    for await (const chunk of stream) {
      yield chunk
    }
  }, [chatStream])

  /**
   * 确认操作
   */
  const confirm = useCallback(
    async (request: ConfirmRequest): Promise<ChatResponse> => {
      const response = await apiRequest('/api/agent/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      })

      const result = await response.json()

      if (response.ok && result.code === 200) {
        return result.data as ChatResponse
      }

      throw new Error(result.message || '确认操作失败')
    },
    []
  )

  /**
   * 获取会话历史
   */
  const getHistory = useCallback(async (sessionId: string, limit = 10) => {
    const response = await apiRequest(
      `/api/agent/history?session_id=${sessionId}&limit=${limit}`,
      {
        method: 'GET',
      }
    )

    const result = await response.json()

    if (response.ok && result.code === 200) {
      return result.data.messages || []
    }

    throw new Error(result.message || '获取历史失败')
  }, [])

  /**
   * 删除会话
   */
  const deleteSession = useCallback(async (sessionId: string) => {
    const response = await apiRequest(`/api/agent/session/${sessionId}`, {
      method: 'DELETE',
    })

    const result = await response.json()

    if (response.ok && result.code === 200) {
      return true
    }

    throw new Error(result.message || '删除会话失败')
  }, [])

  /**
   * 获取会话列表
   */
  const getSessions = useCallback(async () => {
    const response = await apiRequest('/api/agent/sessions', {
      method: 'GET',
    })

    const result = await response.json()

    if (response.ok && result.code === 200) {
      return result.data
    }

    throw new Error(result.message || '获取会话列表失败')
  }, [])

  /**
   * 获取会话详情
   */
  const getSession = useCallback(async (sessionId: string) => {
    const response = await apiRequest(`/api/agent/session/${sessionId}`, {
      method: 'GET',
    })

    const result = await response.json()

    if (response.ok && result.code === 200) {
      return result.data
    }

    throw new Error(result.message || '获取会话详情失败')
  }, [])

  /**
   * 切换会话
   */
  const switchSession = useCallback((sessionId: string) => {
    setSessionId(sessionId)
    return sessionId
  }, [])

  /**
   * 创建新会话 - 总是生成新的 session ID
   */
  const createSession = useCallback(() => {
    const newSessionId = generateSessionId()
    setSessionId(newSessionId)
    return newSessionId
  }, [])

  /**
   * 获取会话历史列表
   */
  const getSessionList = useCallback(() => {
    return getSessionHistory()
  }, [])

  /**
   * 从历史列表中移除会话
   */
  const removeSessionFromList = useCallback((sessionId: string) => {
    removeSessionFromHistory(sessionId)
  }, [])

  return {
    chat,
    chatStream: chatStreamWrapper,
    confirm,
    getHistory,
    deleteSession,
    getSessions,
    getSession,
    switchSession,
    createSession,
    getSessionList,
    removeSessionFromList,
    getCurrentSessionId: getSessionId,
  }
}

// 导出辅助函数
export {
  getSessionId,
  setSessionId,
  clearSessionId,
  generateSessionId,
  getSessionHistory,
  saveSessionToHistory,
}
