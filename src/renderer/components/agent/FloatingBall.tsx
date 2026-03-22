/**
 * 悬浮球组件
 * Agent 入口点，点击展开聊天面板
 */
import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { cn } from '~/renderer/lib/utils'
import { ChatPanel } from './ChatPanel'
import { useAiApi } from '~/renderer/hooks/useAiApi'

interface FloatingBallProps {
  className?: string
}

// Line-style Sparkle Icon SVG
const SparkleIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    height="28"
    stroke="currentColor"
    strokeLinecap="round"
    strokeLinejoin="round"
    strokeWidth="1.8"
    viewBox="0 0 24 24"
    width="28"
  >
    <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z" />
    <line x1="12" x2="12" y1="1" y2="3" />
    <line x1="23" x2="21" y1="12" y2="12" />
    <line x1="12" x2="12" y1="21" y2="23" />
    <line x1="3" x2="1" y1="12" y2="12" />
  </svg>
)

// Line-style Close Icon SVG
const CloseIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    height="28"
    stroke="currentColor"
    strokeLinecap="round"
    strokeLinejoin="round"
    strokeWidth="2"
    viewBox="0 0 24 24"
    width="28"
  >
    <line x1="18" x2="6" y1="6" y2="18" />
    <line x1="6" x2="18" y1="6" y2="18" />
  </svg>
)

export function FloatingBall({ className }: FloatingBallProps) {
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const [aiConfigured, setAiConfigured] = useState<boolean | null>(null)
  const { getAIConfig } = useAiApi()

  // 导航到设置页面
  const navigateToSettings = useCallback(() => {
    navigate('/settings')
  }, [navigate])

  // 点击打开聊天时检查 AI 配置
  const handleToggle = useCallback(async () => {
    if (!isOpen) {
      // 打开聊天面板前检查 AI 配置
      let configured = aiConfigured
      if (aiConfigured === null) {
        try {
          const config = await getAIConfig()
          configured = !!config
          setAiConfigured(configured)
        } catch {
          configured = false
          setAiConfigured(false)
        }
      }

      if (!configured) {
        // AI 未配置，显示提示
        toast.warning('请先配置 AI 服务', {
          description: '点击前往设置页面配置',
          action: {
            label: '去设置',
            onClick: navigateToSettings,
          },
        })
        return
      }
    }

    setIsOpen(prev => !prev)
  }, [isOpen, aiConfigured, getAIConfig, navigateToSettings])

  return (
    <div className={cn('fixed bottom-8 right-8 z-50', className)}>
      {/* 聊天面板 */}
      {isOpen && <ChatPanel />}

      {/* 悬浮球按钮 - 使用浅蓝色主题 */}
      <button
        aria-label={isOpen ? '关闭 AI 助手' : '打开 AI 助手'}
        className={cn(
          'flex h-[60px] w-[60px] items-center justify-center rounded-full',
          'bg-linear-to-br from-[#5ac8fa] to-[#34aadc] text-white',
          'shadow-[0_4px_16px_rgba(90,200,250,0.35)]',
          'transition-all duration-200',
          'hover:scale-110 hover:shadow-[0_6px_24px_rgba(90,200,250,0.45)]',
          'active:scale-95'
        )}
        onClick={handleToggle}
        type="button"
      >
        {isOpen ? (
          <CloseIcon className="h-7 w-7" />
        ) : (
          <SparkleIcon className="h-7 w-7" />
        )}
      </button>
    </div>
  )
}
