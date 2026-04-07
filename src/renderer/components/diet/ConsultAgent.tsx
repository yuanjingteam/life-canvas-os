/**
 * 咨询 AI 助手组件
 * 提供一个按钮，点击后自动打开 AI 助手并发送预设消息
 */
import React from 'react'
import { Sparkles } from 'lucide-react'
import { Button } from '~/renderer/components/ui/button'
import { cn } from '~/renderer/lib/utils'

interface ConsultAgentProps {
  message: string
  label?: string
  className?: string
  variant?: 'default' | 'outline' | 'ghost' | 'secondary' | 'glass'
}

export function ConsultAgent({
  message,
  label = '咨询 AI 营养师',
  className,
  variant = 'glass',
}: ConsultAgentProps) {
  const handleConsult = () => {
    // 1. 打开 Agent 面板
    window.dispatchEvent(new CustomEvent('agent-toggle', { detail: { open: true } }))
    
    // 2. 发送预设消息
    // 给一点延迟确保面板已加载
    setTimeout(() => {
      window.dispatchEvent(new CustomEvent('agent-send-message', { detail: { message } }))
    }, 300)
  }

  return (
    <Button
      onClick={handleConsult}
      variant={variant as any}
      className={cn('gap-2 group', className)}
    >
      <Sparkles className="w-4 h-4 text-orange-500 group-hover:animate-pulse" />
      {label}
    </Button>
  )
}
