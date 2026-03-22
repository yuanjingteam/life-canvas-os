/**
 * 聊天消息组件
 * Apple 风格设计
 */
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Bot, User, AlertCircle } from 'lucide-react'
import { cn } from '~/renderer/lib/utils'
import type { ActionInfoSchema } from '~/renderer/api/agent'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  actions?: ActionInfoSchema[]
  error?: boolean
}

interface ChatMessageProps {
  message: Message
  className?: string
}

export function ChatMessage({ message, className }: ChatMessageProps) {
  const isUser = message.role === 'user'

  // 格式化时间戳
  const formatTime = (timestamp: string) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div
      className={cn(
        'flex gap-3 max-w-[85%]',
        isUser ? 'self-end flex-row-reverse' : 'self-start',
        'animate-slide-up',
        className
      )}
    >
      {/* 头像 */}
      <div
        className={cn(
          'flex h-10 w-10 shrink-0 items-center justify-center rounded-full self-start',
          isUser
            ? 'bg-linear-to-br from-[#007aff] to-[#5ac8fa]'
            : 'bg-[#f6f6f7] dark:bg-[#2c2c2e]',
          message.error && 'bg-red-100 dark:bg-red-900/30'
        )}
      >
        {message.error ? (
          <AlertCircle className="h-6 w-6 text-red-500" />
        ) : isUser ? (
          <User className="h-6 w-6 text-white" />
        ) : (
          <Bot className="h-6 w-6 text-[#007aff]" />
        )}
      </div>

      {/* 消息内容 */}
      <div className="flex flex-col gap-1">
        {/* 时间戳 - 显示在消息外部 */}
        {message.timestamp && (
          <div
            className={cn(
              'text-xs px-1',
              isUser
                ? 'text-right text-[#98989f] dark:text-[rgba(255,255,255,0.4)]'
                : 'text-[#98989f] dark:text-[rgba(255,255,255,0.4)]'
            )}
          >
            {formatTime(message.timestamp)}
          </div>
        )}

        <div
          className={cn(
            'px-4 py-3 rounded-2xl',
            isUser
              ? 'bg-[#007aff] text-white rounded-tr-sm'
              : 'bg-[#f6f6f7] dark:bg-[#2c2c2e] text-[#1d1d1f] dark:text-white rounded-tl-sm',
            message.error &&
              'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400'
          )}
        >
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap leading-relaxed wrap-break-word">
              {message.content}
            </p>
          ) : (
            <div className="text-sm prose prose-sm dark:prose-invert max-w-none wrap-break-word">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            </div>
          )}

          {/* 操作信息 */}
          {message.actions && message.actions.length > 0 && (
            <div className="mt-2 pt-2 border-t border-black/5 dark:border-white/10">
              {message.actions.map((action, index) => (
                <div
                  className="text-xs text-[#98989f] dark:text-[rgba(255,255,255,0.4)]"
                  key={index}
                >
                  <span className="font-medium">{action.skill}</span>
                  {action.params && Object.keys(action.params).length > 0 && (
                    <span className="ml-1 opacity-70">
                      ({Object.keys(action.params).join(', ')})
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
