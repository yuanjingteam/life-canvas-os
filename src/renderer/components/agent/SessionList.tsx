/**
 * 会话列表组件
 * 显示历史会话，支持选择和删除
 */
import { useState, useEffect, useCallback } from 'react'
import { MessageSquare, Trash2, Plus, Loader2, Calendar } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '~/renderer/lib/utils'
import { Button } from '~/renderer/components/ui/button'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
  TooltipProvider,
} from '~/renderer/components/ui/tooltip'
import type { SessionListItem } from '~/renderer/api/agent'
import { useAgentApi } from '~/renderer/hooks/useAgentApi'

interface SessionListProps {
  onSelectSession: (sessionId: string) => void
  onNewChat: () => void
  currentSessionId: string | null
}

export function SessionList({
  onSelectSession,
  onNewChat,
  currentSessionId,
}: SessionListProps) {
  const [sessions, setSessions] = useState<SessionListItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const { getSessions, deleteSession } = useAgentApi()

  // 加载会话列表
  const loadSessions = useCallback(async () => {
    try {
      setIsLoading(true)
      const response = await getSessions()
      // 直接从 response 取 sessions
      const sessionList = response.sessions || []
      setSessions(sessionList)
    } catch (error) {
      console.error('Load sessions error:', error)
      toast.error('加载会话列表失败')
    } finally {
      setIsLoading(false)
    }
  }, [getSessions])

  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  // 处理删除会话
  const handleDelete = useCallback(
    async (e: React.MouseEvent, sessionId: string) => {
      e.stopPropagation()

      // 防止重复删除
      if (deletingId) return

      setDeletingId(sessionId)
      try {
        await deleteSession(sessionId)
        toast.success('会话已删除')
        // 重新加载列表
        loadSessions()

        // 如果删除的是当前选中的会话，触发新会话
        if (currentSessionId === sessionId) {
          onNewChat()
        }
      } catch (error) {
        console.error('Delete session error:', error)
        toast.error('删除会话失败')
      } finally {
        setDeletingId(null)
      }
    },
    [deleteSession, loadSessions, currentSessionId, onNewChat, deletingId]
  )

  // 格式化时间
  const formatTime = useCallback((dateString: string) => {
    if (!dateString) return ''
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) {
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
      })
    }
    if (days === 1) {
      return '昨天'
    }
    if (days < 7) {
      return `${days}天前`
    }
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
    })
  }, [])

  // 截取消息预览
  const truncateMessage = useCallback(
    (title: string | null, lastMessage: string | null) => {
      // 优先使用标题，其次使用最后一条消息
      const text = title || lastMessage
      if (!text) return '新会话'
      return text.length > 30 ? `${text.substring(0, 30)}...` : text
    },
    []
  )

  return (
    <TooltipProvider>
      <div className="flex h-full flex-col">
        {/* 头部 */}
        <div className="flex items-center justify-between border-b px-4 py-3">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            <span className="text-sm font-medium">会话历史</span>
          </div>
          <Button
            className="h-7 gap-1 text-xs"
            onClick={onNewChat}
            size="sm"
            variant="ghost"
          >
            <Plus className="h-3 w-3" />
            新会话
          </Button>
        </div>

        {/* 会话列表 */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : sessions.length === 0 ? (
            <div className="py-8 text-center text-sm text-muted-foreground">
              <p>暂无会话记录</p>
              <p className="mt-1 text-xs">开始一个新会话吧</p>
            </div>
          ) : (
            <div className="p-2">
              {sessions.map(session => (
                <div
                  className={cn(
                    'group flex items-start justify-between rounded-lg p-2 transition-colors hover:bg-muted/50',
                    currentSessionId === session.session_id && 'bg-muted'
                  )}
                  key={session.session_id}
                  onClick={() => onSelectSession(session.session_id)}
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3 shrink-0 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">
                        {formatTime(session.updated_at)}
                      </span>
                    </div>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <p className="mt-1 truncate text-sm">
                          {truncateMessage(session.title, session.last_message)}
                        </p>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="max-w-xs">
                          {session.title || session.last_message || '新会话'}
                        </p>
                      </TooltipContent>
                    </Tooltip>
                    <p className="text-xs text-muted-foreground">
                      {session.message_count} 条消息
                    </p>
                  </div>
                  <Button
                    className={cn(
                      'h-6 w-6 shrink-0 opacity-0 group-hover:opacity-100',
                      deletingId === session.session_id && 'opacity-100'
                    )}
                    disabled={deletingId === session.session_id}
                    onClick={e => handleDelete(e, session.session_id)}
                    size="icon"
                    variant="ghost"
                  >
                    {deletingId === session.session_id ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      <Trash2 className="h-3 w-3 text-red-500" />
                    )}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </TooltipProvider>
  )
}
