/**
 * Agent Floating Ball Component
 *
 * 悬浮球入口，固定在右下角，点击展开聊天面板
 */

import { useState, useRef } from 'react'
import { Sparkles, X } from 'lucide-react'
import { ChatPanel } from './ChatPanel'
import { cn } from '~/renderer/lib/utils'

export interface FloatingBallProps {
  /** 是否显示 */
  visible?: boolean
  /** 关闭回调 */
  onClose?: () => void
}

export function FloatingBall({ visible = true, onClose }: FloatingBallProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isHovering, setIsHovering] = useState(false)
  const ballRef = useRef<HTMLDivElement>(null)

  const handleToggle = () => {
    if (isExpanded) {
      setIsExpanded(false)
      onClose?.()
    } else {
      setIsExpanded(true)
    }
  }

  const handleClose = () => {
    setIsExpanded(false)
    onClose?.()
  }

  if (!visible) return null

  return (
    <div ref={ballRef} className="fixed bottom-6 right-6 z-50">
      {/* 聊天面板 */}
      {isExpanded && (
        <div className="absolute bottom-16 right-0 animate-in zoom-in-95 duration-300">
          <ChatPanel onClose={handleClose} />
        </div>
      )}

      {/* 悬浮球 */}
      <button
        className={cn(
          'relative w-14 h-14 rounded-full bg-gradient-to-br from-apple-accent to-blue-600',
          'flex items-center justify-center',
          'shadow-apple-lg hover:shadow-glow-accent',
          'transition-all duration-300',
          'hover:scale-110 active:scale-95',
          'group',
          isExpanded && 'rotate-90'
        )}
        onClick={handleToggle}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
        aria-label={isExpanded ? '关闭助手' : '打开助手'}
      >
        {/* 脉动光晕效果 */}
        <span className="absolute inset-0 rounded-full bg-apple-accent/30 animate-ping" />
        <span className="absolute -inset-1 rounded-full bg-apple-accent/20 animate-pulse" />

        {/* 图标 */}
        <Sparkles
          className={cn(
            'w-7 h-7 text-white relative z-10',
            'transition-transform duration-300',
            isHovering && 'scale-110'
          )}
        />

        {/* 关闭图标（展开时显示） */}
        {isExpanded && (
          <X className="absolute w-6 h-6 text-white z-10 animate-in fade-in duration-200" />
        )}
      </button>
    </div>
  )
}
