/**
 * Agent API Hook
 * 处理 Agent 聊天、确认等操作
 */
import { useState, useCallback, useEffect, useRef } from 'react'
import type {
  AgentChatResponse,
  AgentConfirmRequest,
  SessionListResponse,
} from '~/renderer/api/agent'

// 判断是否为开发模式
const isDev = import.meta.env.DEV

/**
 * 错误类型枚举
 */
export enum AgentErrorType {
  AI_NOT_CONFIGURED = 'AI_NOT_CONFIGURED', // AI 未配置
  API_ERROR = 'API_ERROR', // API 调用错误
  NETWORK_ERROR = 'NETWORK_ERROR', // 网络错误
  UNKNOWN = 'UNKNOWN', // 未知错误
}

/**
 * 错误信息接口
 */
export interface AgentError {
  type: AgentErrorType
  message: string
  hint?: string // 用户提示（如 "请先在设置中配置 AI 服务"）
  statusCode?: number
}

/**
 * 创建 AgentError
 */
function createAgentError(
  type: AgentErrorType,
  message: string,
  hint?: string,
  statusCode?: number
): AgentError {
  return { type, message, hint, statusCode }
}

interface StreamEvent {
  type: 'stream_start' | 'stream_chunk' | 'stream_end'
  session_id: string
  content?: string
  result?: AgentChatResponse
  error?: string
}

// localStorage key for persisting session ID
const SESSION_ID_KEY = 'agent_session_id'

/**
 * 获取保存的 sessionId
 */
function getSavedSessionId(): string {
  if (typeof window === 'undefined') return ''
  return localStorage.getItem(SESSION_ID_KEY) || ''
}

/**
 * 保存 sessionId 到 localStorage
 */
function saveSessionId(sessionId: string): void {
  if (typeof window === 'undefined') return
  if (sessionId) {
    localStorage.setItem(SESSION_ID_KEY, sessionId)
  } else {
    localStorage.removeItem(SESSION_ID_KEY)
  }
}

export function useAgentApi() {
  const [sessionId, setSessionId] = useState<string>(getSavedSessionId)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isAborted, setIsAborted] = useState(false)

  // AbortController for canceling ongoing requests
  const abortControllerRef = useRef<AbortController | null>(null)

  // IPC 事件监听器清理
  const listenersRef = useRef<Array<() => void>>([])

  // 持久化 sessionId 到 localStorage
  useEffect(() => {
    saveSessionId(sessionId)
  }, [sessionId])

  // 清理监听器
  useEffect(() => {
    return () => {
      for (const cleanup of listenersRef.current) {
        cleanup()
      }
    }
  }, [])

  /**
   * 发送消息
   */
  const sendMessage = useCallback(
    async (
      message: string,
      currentSessionId?: string,
      stream: boolean = true
    ): Promise<AgentChatResponse | ReadableStream<Uint8Array>> => {
      // 创建新的 AbortController
      abortControllerRef.current = new AbortController()
      setIsAborted(false)
      setIsLoading(true)
      setError(null)

      try {
        if (isDev) {
          // 开发模式：HTTP 请求
          // 根据 stream 参数选择正确的接口
          const endpoint = stream ? '/api/agent/chat/stream' : '/api/agent/chat'
          let response: Response
          try {
            response = await fetch(`http://localhost:8000${endpoint}`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                message,
                session_id: currentSessionId,
                stream,
              }),
              signal: abortControllerRef.current.signal,
            })
          } catch (networkError) {
            // 检查是否是被取消的请求
            if (
              abortControllerRef.current?.signal.aborted ||
              (networkError instanceof Error &&
                networkError.name === 'AbortError')
            ) {
              throw createAgentError(
                AgentErrorType.API_ERROR,
                '已取消请求',
                '用户取消了请求'
              )
            }
            // 网络错误（无法连接到服务器）
            throw createAgentError(
              AgentErrorType.NETWORK_ERROR,
              '网络连接失败',
              '请检查网络连接或确认后端服务已启动'
            )
          }

          if (!response.ok) {
            let errorData: any
            try {
              errorData = await response.json()
            } catch {
              errorData = {}
            }
            const detail = errorData.detail || errorData

            // 根据状态码处理
            if (response.status === 424) {
              // AI 未配置
              throw createAgentError(
                AgentErrorType.AI_NOT_CONFIGURED,
                detail.message || 'AI 服务未配置',
                detail.data?.hint || '请先在设置中配置 AI 服务',
                424
              )
            }

            if (response.status >= 500) {
              throw createAgentError(
                AgentErrorType.API_ERROR,
                detail.message || '服务器内部错误',
                detail.data?.hint || detail.message || '请稍后重试',
                response.status
              )
            }

            throw createAgentError(
              AgentErrorType.API_ERROR,
              detail.message || '请求失败',
              undefined,
              response.status
            )
          }

          if (stream && response.body) {
            return response.body
          }

          const data: AgentChatResponse = await response.json()

          // 检查响应体中的 error 字段
          if (data.error) {
            throw createAgentError(
              AgentErrorType.API_ERROR,
              data.message || data.error,
              data.message || data.error,
              response.status
            )
          }

          if (!currentSessionId) {
            setSessionId(data.session_id)
          }
          return data
        }
        // 生产模式：IPC 调用
        if (stream) {
          // 流式请求：使用 agent_chat_stream action
          // 注意：流式响应通过 IPC 事件接收，需要使用 useAgentStreamListener
          const result = await window.App.request('agent_chat_stream', {
            message,
            session_id: currentSessionId,
          })

          if (result.error) {
            if (result.code === 424 || result.error?.includes?.('未配置')) {
              throw createAgentError(
                AgentErrorType.AI_NOT_CONFIGURED,
                'AI 服务未配置',
                '请先在设置中配置 AI 服务',
                424
              )
            }
            throw createAgentError(
              AgentErrorType.API_ERROR,
              result.error || result.message || '请求失败'
            )
          }

          // 流式模式返回空对象，实际数据通过事件接收
          return {} as AgentChatResponse
        }

        // 非流式请求
        const result = await window.App.request('agent_chat', {
          message,
          session_id: currentSessionId,
        })

        if (result.error) {
          if (result.code === 424 || result.error?.includes?.('未配置')) {
            throw createAgentError(
              AgentErrorType.AI_NOT_CONFIGURED,
              result.message || 'AI 服务未配置',
              result.data?.hint || '请先在设置中配置 AI 服务',
              424
            )
          }
          throw createAgentError(
            AgentErrorType.API_ERROR,
            result.error || result.message || '请求失败',
            result.data?.hint || result.message
          )
        }

        const data: AgentChatResponse = result
        if (!currentSessionId) {
          setSessionId(data.session_id)
        }
        return data
      } catch (err) {
        // 检查是否是用户取消的请求
        if (
          abortControllerRef.current?.signal.aborted ||
          (err instanceof Error && err.name === 'AbortError')
        ) {
          setIsAborted(true)
          setIsLoading(false)
          // 不抛出错误，静默处理
          return {} as AgentChatResponse
        }

        // 如果已经是 AgentError，直接抛出
        if (
          err &&
          typeof err === 'object' &&
          'type' in err &&
          Object.values(AgentErrorType).includes((err as AgentError).type)
        ) {
          const agentError = err as AgentError
          setError(agentError.message)
          throw err
        }

        // 未知错误
        const errorMessage = err instanceof Error ? err.message : '未知错误'
        setError(errorMessage)
        throw createAgentError(AgentErrorType.UNKNOWN, errorMessage)
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  /**
   * 中断正在进行的请求
   */
  const abort = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setIsAborted(true)
      setIsLoading(false)
    }
  }, [])

  /**
   * 确认操作
   */
  const confirmAction = useCallback(
    async (
      currentSessionId: string,
      confirmationId: string,
      confirmed: boolean,
      userReason?: string
    ): Promise<AgentChatResponse> => {
      setIsLoading(true)
      setError(null)

      try {
        if (isDev) {
          let response: Response
          try {
            response = await fetch('http://localhost:8000/api/agent/confirm', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                session_id: currentSessionId,
                confirmation_id: confirmationId,
                confirmed,
                user_reason: userReason,
              } as AgentConfirmRequest),
            })
          } catch (networkError) {
            throw createAgentError(
              AgentErrorType.NETWORK_ERROR,
              '网络连接失败',
              '请检查网络连接或确认后端服务已启动'
            )
          }

          if (!response.ok) {
            let errorData: any
            try {
              errorData = await response.json()
            } catch {
              errorData = {}
            }
            const detail = errorData.detail || errorData

            if (response.status === 424) {
              throw createAgentError(
                AgentErrorType.AI_NOT_CONFIGURED,
                detail.message || 'AI 服务未配置',
                detail.data?.hint || '请先在设置中配置 AI 服务',
                424
              )
            }

            throw createAgentError(
              AgentErrorType.API_ERROR,
              detail.message || '确认失败',
              undefined,
              response.status
            )
          }

          return await response.json()
        }
        const result = await window.App.request('agent_confirm', {
          session_id: currentSessionId,
          confirmation_id: confirmationId,
          confirmed,
          user_reason: userReason,
        })

        if (result.error) {
          if (result.code === 424 || result.error?.includes?.('未配置')) {
            throw createAgentError(
              AgentErrorType.AI_NOT_CONFIGURED,
              result.message || 'AI 服务未配置',
              result.data?.hint || '请先在设置中配置 AI 服务',
              424
            )
          }
          throw createAgentError(
            AgentErrorType.API_ERROR,
            result.error || result.message || '确认失败'
          )
        }

        return result
      } catch (err) {
        if (
          err &&
          typeof err === 'object' &&
          'type' in err &&
          Object.values(AgentErrorType).includes((err as AgentError).type)
        ) {
          const agentError = err as AgentError
          setError(agentError.message)
          throw err
        }

        const errorMessage = err instanceof Error ? err.message : '未知错误'
        setError(errorMessage)
        throw createAgentError(AgentErrorType.UNKNOWN, errorMessage)
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  /**
   * 获取会话历史
   */
  const getHistory = useCallback(
    async (targetSessionId: string) => {
      setIsLoading(true)
      setError(null)

      try {
        if (isDev) {
          const response = await fetch(
            `http://localhost:8000/api/agent/history/${targetSessionId}`
          )

          if (response.status === 404) {
            // 会话不存在，清除无效的 sessionId
            setSessionId('')
            saveSessionId('')
            throw new Error('会话不存在或已过期')
          }

          if (!response.ok) {
            throw new Error('获取历史失败')
          }

          return await response.json()
        }
        const result = await window.App.request('agent_history', {
          session_id: targetSessionId,
        })

        // 检查是否是会话不存在的错误 (code: 404)
        if (result.code === 404 || result.error?.includes('会话不存在')) {
          // 会话不存在，清除无效的 sessionId
          setSessionId('')
          saveSessionId('')
          throw new Error('会话不存在或已过期')
        }

        if (result.error) {
          throw new Error(result.error)
        }

        return result
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '未知错误'
        setError(errorMessage)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [setSessionId, saveSessionId]
  )

  /**
   * 获取会话列表
   */
  const getSessions = useCallback(async (): Promise<SessionListResponse> => {
    setIsLoading(true)
    setError(null)

    try {
      if (isDev) {
        const response = await fetch('http://localhost:8000/api/agent/sessions')

        if (!response.ok) {
          throw new Error('获取会话列表失败')
        }

        return await response.json()
      }
      const result = await window.App.request('agent_sessions', {})

      if (result.error) {
        throw new Error(result.error)
      }

      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '未知错误'
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * 删除会话
   */
  const deleteSession = useCallback(async (targetSessionId: string) => {
    setIsLoading(true)
    setError(null)

    try {
      if (isDev) {
        const response = await fetch(
          `http://localhost:8000/api/agent/sessions/${targetSessionId}`,
          { method: 'DELETE' }
        )

        if (!response.ok) {
          throw new Error('删除会话失败')
        }

        return await response.json()
      }
      const result = await window.App.request('agent_delete_session', {
        session_id: targetSessionId,
      })

      if (result.error) {
        throw new Error(result.error)
      }

      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '未知错误'
      setError(errorMessage)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * 切换会话固定状态
   */
  const togglePinSession = useCallback(
    async (targetSessionId: string, pinned: number) => {
      setIsLoading(true)
      setError(null)

      try {
        if (isDev) {
          const response = await fetch(
            `http://localhost:8000/api/agent/sessions/${targetSessionId}/pin?pinned=${pinned}`,
            { method: 'PATCH' }
          )

          if (!response.ok) {
            throw new Error('操作失败')
          }

          return await response.json()
        }
        const result = await window.App.request('agent_toggle_pin', {
          session_id: targetSessionId,
          pinned,
        })

        if (result.error) {
          throw new Error(result.error)
        }

        return result
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '未知错误'
        setError(errorMessage)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  /**
   * 获取可用技能列表
   */
  const getSkills = useCallback(async () => {
    try {
      if (isDev) {
        const response = await fetch('http://localhost:8000/api/agent/skills')
        if (!response.ok) {
          throw new Error('获取技能列表失败')
        }
        const data = await response.json()
        return data.data
      }
      const result = await window.App.request('agent_skills', {})
      return result.skills
    } catch (err) {
      console.error('Get skills error:', err)
      return []
    }
  }, [])

  /**
   * 清除会话 (开始新会话)
   */
  const clearSession = useCallback(() => {
    setSessionId('')
    saveSessionId('')
  }, [])

  // 允许外部设置 sessionId（例如从流式响应中获取）
  const updateSessionId = useCallback((newSessionId: string) => {
    setSessionId(newSessionId)
  }, [])

  return {
    sessionId,
    updateSessionId,
    clearSession,
    isLoading,
    error,
    sendMessage,
    confirmAction,
    getHistory,
    getSessions,
    deleteSession,
    togglePinSession,
    getSkills,
    abort,
    isAborted,
  }
}

/**
 * 使用 IPC 流式事件监听器
 * 这是一个独立的 Hook，需要在组件顶层调用
 */
export function useAgentStreamListener(
  onStart: (sessionId: string) => void,
  onChunk: (content: string) => void,
  onEnd: (result: AgentChatResponse) => void
) {
  const isDevelopment = import.meta.env.DEV

  useEffect(() => {
    if (isDevelopment) return // 开发模式不需要 IPC 监听

    // 监听流式开始
    const handleStart = (_event: unknown, data: StreamEvent) => {
      onStart(data.session_id)
    }

    // 监听内容块
    const handleChunk = (_event: unknown, data: StreamEvent) => {
      if (data.content) {
        onChunk(data.content)
      }
    }

    // 监听流式结束
    const handleEnd = (_event: unknown, data: StreamEvent) => {
      if (data.result) {
        onEnd(data.result)
      }
    }

    // 注册监听器
    window.electron.on('agent-stream-start', handleStart)
    window.electron.on('agent-stream-chunk', handleChunk)
    window.electron.on('agent-stream-end', handleEnd)

    // 清理函数
    return () => {
      window.electron.removeListener('agent-stream-start', handleStart)
      window.electron.removeListener('agent-stream-chunk', handleChunk)
      window.electron.removeListener('agent-stream-end', handleEnd)
    }
  }, [onStart, onChunk, onEnd, isDevelopment])
}
