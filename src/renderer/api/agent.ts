/**
 * Agent API 类型定义
 */

export interface ActionInfoSchema {
  skill: string
  action: string
  params: Record<string, unknown>
  risk_level: string
}

export interface ConfirmationRequired {
  confirmation_id: string
  action: ActionInfoSchema
  message: string
  risk_level: string
  requires_code: boolean
}

export interface AgentChatResponse {
  session_id: string
  message: string
  actions: ActionInfoSchema[]
  confirmation_required: ConfirmationRequired | null
  error: string | null
  timestamp: string
}

export interface AgentHistoryResponse {
  session_id: string
  messages: Array<{
    role: string
    content: string
    created_at: string // 后端返回 created_at
    timestamp?: string // 兼容字段
  }>
  created_at: string
  updated_at: string
}

export interface SkillSchema {
  name: string
  description: string
  risk_level: string
  parameters: {
    type: string
    properties: Record<string, unknown>
    required: string[]
  }
  keywords: string[]
  examples: string[]
}

// 请求类型
export interface AgentChatRequest {
  message: string
  session_id?: string
  stream?: boolean
}

export interface AgentConfirmRequest {
  session_id: string
  confirmation_id: string
  confirmed: boolean
  user_reason?: string
}

// 会话列表项
export interface SessionListItem {
  session_id: string
  title: string | null
  message_count: number
  created_at: string
  updated_at: string
  last_message: string | null
  pinned: number // 0: 未固定, 1: 已固定
}

// 会话列表响应
export interface SessionListResponse {
  sessions: SessionListItem[]
  total: number
}
