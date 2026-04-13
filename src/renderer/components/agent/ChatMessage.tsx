/**
 * Chat Message Component
 *
 * 消息气泡组件
 */

import { Bot, User, Copy, Check, Edit, RotateCcw } from 'lucide-react'
import { cn } from '~/renderer/lib/utils'
import { formatTimeCN } from '~/renderer/lib/dateUtils'
import { Button } from '~/renderer/components/ui/button'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number | string
  isError?: boolean
  isStreaming?: boolean // 是否正在流式传输
  actionTaken?: {
    skill: string
    params?: Record<string, unknown>
    result?: Record<string, unknown>
  }
  requiresConfirmation?: boolean
  confirmationId?: string
}

export interface ChatMessageProps {
  message: Message
  /** 是否正在编辑 */
  isEditing?: boolean
  /** 编辑中的文本 */
  editingText?: string
  /** 编辑回调 */
  onEdit?: () => void
  /** 保存编辑回调 */
  onSaveEdit?: () => void
  /** 取消编辑回调 */
  onCancelEdit?: () => void
  /** 复制回调 */
  onCopy?: () => void
  /** 重发回调 */
  onRetry?: () => void
  /** 是否已复制 */
  copied?: boolean
}

export function ChatMessage({
  message,
  isEditing = false,
  editingText = '',
  onEdit,
  onSaveEdit,
  onCancelEdit,
  onCopy,
  onRetry,
  copied = false,
}: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={cn('flex group', isUser ? 'justify-end' : 'justify-start')}>
      {isUser ? (
        /* 用户消息 */
        <div className="max-w-[80%] relative">
          <div
            className={cn(
              'px-4 py-2.5 rounded-2xl',
              'bg-gradient-to-br from-apple-accent to-blue-600',
              'text-white shadow-sm',
              'rounded-br-md'
            )}
          >
            {isEditing ? (
              <textarea
                autoFocus
                className="w-full bg-transparent text-white text-sm outline-none resize-none"
                onBlur={onCancelEdit}
                onChange={e => onSaveEdit?.()}
                onKeyDown={e => {
                  if (e.key === 'Enter' && e.metaKey) {
                    e.preventDefault()
                    onSaveEdit?.()
                  }
                  if (e.key === 'Escape') {
                    e.preventDefault()
                    onCancelEdit?.()
                  }
                }}
                rows={3}
                value={editingText}
              />
            ) : (
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            )}
            <div className="text-[10px] opacity-70 mt-1 text-right">
              {formatTimeCN(message.timestamp)}
            </div>
          </div>

          {/* 消息操作按钮 */}
          {!isEditing && (
            <div className="absolute -top-2 -right-2 flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity bg-apple-bgMain dark:bg-black rounded-lg shadow-sm border border-apple-border dark:border-white/10 p-0.5">
              <Button
                className="h-6 w-6 text-apple-textSec hover:text-apple-accent"
                onClick={onCopy}
                size="icon-xs"
                title="复制"
                variant="ghost"
              >
                {copied ? (
                  <Check className="w-3.5 h-3.5" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </Button>
              <Button
                className="h-6 w-6 text-apple-textSec hover:text-apple-accent"
                onClick={onEdit}
                size="icon-xs"
                title="编辑"
                variant="ghost"
              >
                <Edit className="w-3.5 h-3.5" />
              </Button>
              {message.isError && (
                <Button
                  className="h-6 w-6 text-apple-textSec hover:text-apple-accent"
                  onClick={onRetry}
                  size="icon-xs"
                  title="重试"
                  variant="ghost"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </Button>
              )}
            </div>
          )}
        </div>
      ) : (
        /* Agent 消息 */
        <div className="flex items-start gap-2 max-w-[80%] relative">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-apple-accent to-blue-600 flex items-center justify-center shrink-0">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1 relative">
            <div
              className={cn(
                'px-4 py-2.5 rounded-2xl shadow-sm',
                'bg-apple-bgSidebar dark:bg-white/5',
                'text-apple-textMain dark:text-white',
                'rounded-bl-md',
                message.isError &&
                  'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-900/30',
                message.requiresConfirmation &&
                  'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-900/30'
              )}
            >
              <div className="flex items-center gap-2">
                <p className="text-sm whitespace-pre-wrap flex-1">
                  {isEditing ? (
                    <textarea
                      autoFocus
                      className="w-full bg-transparent text-apple-textMain dark:text-white text-sm outline-none resize-none"
                      onBlur={onCancelEdit}
                      onChange={e => onSaveEdit?.()}
                      onKeyDown={e => {
                        if (e.key === 'Enter' && e.metaKey) {
                          e.preventDefault()
                          onSaveEdit?.()
                        }
                        if (e.key === 'Escape') {
                          e.preventDefault()
                          onCancelEdit?.()
                        }
                      }}
                      rows={3}
                      value={editingText}
                    />
                  ) : (
                    message.content
                  )}
                </p>
                {/* 流式传输指示器 */}
                {message.isStreaming && !isEditing && (
                  <span className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-apple-accent animate-pulse" />
                    <span className="w-1.5 h-1.5 rounded-full bg-apple-accent animate-pulse delay-75" />
                    <span className="w-1.5 h-1.5 rounded-full bg-apple-accent animate-pulse delay-150" />
                  </span>
                )}
              </div>

              {/* 确认提示 */}
              {message.requiresConfirmation && (
                <div className="mt-2 flex items-center gap-2 text-yellow-700 dark:text-yellow-400">
                  <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm font-medium">等待确认...</span>
                </div>
              )}

              {/* 操作信息 */}
              {message.actionTaken && (
                <div className="mt-2 p-2 rounded-lg bg-apple-bgMain dark:bg-white/5 border border-apple-border dark:border-white/10">
                  <div className="text-xs text-apple-textSec dark:text-white/40 space-y-1">
                    <div>技能：{message.actionTaken.skill}</div>
                    {message.actionTaken.params && (
                      <div>
                        参数：
                        {JSON.stringify(message.actionTaken.params, null, 2)}
                      </div>
                    )}
                    {message.actionTaken.result && (
                      <div>
                        结果：
                        {JSON.stringify(message.actionTaken.result, null, 2)}
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="text-[10px] text-apple-textSec dark:text-white/40 mt-1">
                {formatTimeCN(message.timestamp)}
              </div>
            </div>

            {/* 消息操作按钮 */}
            {!isEditing && (
              <div className="absolute -top-2 -right-2 flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity bg-apple-bgMain dark:bg-black rounded-lg shadow-sm border border-apple-border dark:border-white/10 p-0.5">
                <Button
                  className="h-6 w-6 text-apple-textSec hover:text-apple-accent"
                  onClick={onCopy}
                  size="icon-xs"
                  title="复制"
                  variant="ghost"
                >
                  {copied ? (
                    <Check className="w-3.5 h-3.5" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                </Button>
                {message.isError && (
                  <Button
                    className="h-6 w-6 text-apple-textSec hover:text-apple-accent"
                    onClick={onRetry}
                    size="icon-xs"
                    title="重试"
                    variant="ghost"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
