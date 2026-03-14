/**
 * Confirm Dialog Component
 *
 * 确认对话框，用于高风险操作的二次确认
 */

import { useState } from 'react'
import {
  TriangleAlert,
  ShieldAlert,
  CircleAlert,
  Info,
  X,
} from 'lucide-react'
import { cn } from '~/renderer/lib/utils'
import { Button } from '~/renderer/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from '~/renderer/components/ui/dialog'

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export interface ConfirmDialogProps {
  /** 是否显示 */
  open?: boolean
  /** 风险等级 */
  riskLevel: RiskLevel
  /** 标题 */
  title?: string
  /** 描述 */
  description?: string
  /** 操作内容 */
  operation?: string
  /** 验证码（CRITICAL 等级需要） */
  requireCode?: boolean
  /** 确认按钮文案 */
  confirmText?: string
  /** 取消按钮文案 */
  cancelText?: string
  /** 确认回调 */
  onConfirm?: () => void | Promise<void>
  /** 取消回调 */
  onCancel?: () => void
  /** 关闭回调 */
  onOpenChange?: (open: boolean) => void
}

const RISK_CONFIG: Record<
  RiskLevel,
  {
    icon: React.ElementType
    color: string
    bgColor: string
    borderColor: string
    buttonColor: string
  }
> = {
  LOW: {
    icon: Info,
    color: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-50 dark:bg-blue-900/10',
    borderColor: 'border-blue-200 dark:border-blue-900/30',
    buttonColor: 'bg-apple-accent hover:bg-apple-accent/90',
  },
  MEDIUM: {
    icon: CircleAlert,
    color: 'text-yellow-600 dark:text-yellow-400',
    bgColor: 'bg-yellow-50 dark:bg-yellow-900/10',
    borderColor: 'border-yellow-200 dark:border-yellow-900/30',
    buttonColor: 'bg-apple-accent hover:bg-apple-accent/90',
  },
  HIGH: {
    icon: TriangleAlert,
    color: 'text-orange-600 dark:text-orange-400',
    bgColor: 'bg-orange-50 dark:bg-orange-900/10',
    borderColor: 'border-orange-200 dark:border-orange-900/30',
    buttonColor: 'bg-red-500 hover:bg-red-500/90',
  },
  CRITICAL: {
    icon: ShieldAlert,
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-50 dark:bg-red-900/10',
    borderColor: 'border-red-200 dark:border-red-900/30',
    buttonColor: 'bg-red-600 hover:bg-red-600/90',
  },
}

export function ConfirmDialog({
  open = false,
  riskLevel = 'MEDIUM',
  title,
  description,
  operation,
  requireCode = false,
  confirmText = '确认',
  cancelText = '取消',
  onConfirm,
  onCancel,
  onOpenChange,
}: ConfirmDialogProps) {
  const [verificationCode, setVerificationCode] = useState('')
  const [isConfirming, setIsConfirming] = useState(false)

  const config = RISK_CONFIG[riskLevel]
  const Icon = config.icon

  const handleConfirm = async () => {
    if (requireCode && !verificationCode.trim()) {
      return
    }

    setIsConfirming(true)
    try {
      await onConfirm?.()
      onOpenChange?.(false)
    } finally {
      setIsConfirming(false)
    }
  }

  const handleCancel = () => {
    onCancel?.()
    onOpenChange?.(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div
              className={cn(
                'w-12 h-12 rounded-full flex items-center justify-center',
                config.bgColor
              )}
            >
              <Icon className={cn('w-6 h-6', config.color)} />
            </div>
            <div className="flex-1">
              <DialogTitle className="text-lg">
                {title ||
                  {
                    LOW: '信息',
                    MEDIUM: '确认操作',
                    HIGH: '警告',
                    CRITICAL: '关键操作',
                  }[riskLevel]}
              </DialogTitle>
              <DialogDescription className="text-sm">
                {description ||
                  {
                    LOW: '此操作无需确认',
                    MEDIUM: '请确认以下操作',
                    HIGH: '此操作可能不可撤销',
                    CRITICAL: '此操作影响重大，请谨慎确认',
                  }[riskLevel]}
              </DialogDescription>
            </div>
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={() => onOpenChange?.(false)}
              className="shrink-0"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>

        {/* 操作预览 */}
        {operation && (
          <div
            className={cn(
              'p-4 rounded-xl border',
              config.bgColor,
              config.borderColor
            )}
          >
            <div className="flex items-center gap-2 mb-2">
              <Icon className={cn('w-4 h-4', config.color)} />
              <span className={cn('text-sm font-semibold', config.color)}>
                {
                  {
                    LOW: '操作预览',
                    MEDIUM: '操作预览',
                    HIGH: '警告',
                    CRITICAL: '关键操作',
                  }[riskLevel]
                }
              </span>
            </div>
            <div className="text-sm text-apple-textMain dark:text-white">
              {operation}
            </div>
          </div>
        )}

        {/* 验证码输入（CRITICAL 等级） */}
        {requireCode && (
          <div className="space-y-2">
            <label className="text-sm text-apple-textSec dark:text-white/40">
              请输入验证码继续：<span className="font-mono text-apple-textMain dark:text-white">DELETE</span>
            </label>
            <input
              type="text"
              value={verificationCode}
              onChange={e => setVerificationCode(e.target.value)}
              placeholder="输入验证码"
              className="w-full px-3 py-2 rounded-xl bg-apple-bgSidebar dark:bg-white/5 border border-apple-border dark:border-white/10 text-sm focus:outline-none focus:border-red-500 transition-all text-apple-textMain dark:text-white placeholder:text-apple-textTer"
            />
          </div>
        )}

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={isConfirming}
          >
            {cancelText}
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={isConfirming || (requireCode && !verificationCode.trim())}
            className={config.buttonColor}
          >
            {isConfirming ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                处理中...
              </>
            ) : (
              confirmText
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
