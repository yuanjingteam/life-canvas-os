/**
 * 确认对话框组件
 */
import { useState } from 'react'
import { AlertTriangle, Info, ShieldAlert, type LucideIcon } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '~/renderer/components/ui/dialog'
import { Button } from '~/renderer/components/ui/button'
import { Input } from '~/renderer/components/ui/input'
import type { ConfirmationRequired } from '~/renderer/api/agent'
import { cn } from '~/renderer/lib/utils'

interface ConfirmDialogProps {
  confirmation: ConfirmationRequired
  onConfirm: () => void
  onCancel: (reason?: string) => void
}

type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

const riskIcons: Record<RiskLevel, LucideIcon> = {
  LOW: Info,
  MEDIUM: Info,
  HIGH: AlertTriangle,
  CRITICAL: ShieldAlert,
}

const riskColors: Record<RiskLevel, string> = {
  LOW: 'text-blue-500',
  MEDIUM: 'text-blue-500',
  HIGH: 'text-orange-500',
  CRITICAL: 'text-red-500',
}

export function ConfirmDialog({
  confirmation,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const [reason, setReason] = useState('')
  const [code, setCode] = useState('')

  const riskLevel = confirmation.risk_level as RiskLevel
  const Icon = riskIcons[riskLevel]
  const iconColor = riskColors[riskLevel]

  const handleConfirm = () => {
    if (confirmation.requires_code && code !== 'CONFIRM') {
      return
    }
    onConfirm()
  }

  return (
    <Dialog onOpenChange={open => !open && onCancel()} open>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Icon className={cn('h-5 w-5', iconColor)} />
            操作确认
          </DialogTitle>
          <DialogDescription>{confirmation.message}</DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 操作详情 */}
          <div className="bg-muted rounded-lg p-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">操作</span>
              <span className="font-medium">{confirmation.action.skill}</span>
            </div>
            <div className="mt-1 flex justify-between">
              <span className="text-muted-foreground">风险等级</span>
              <span
                className={cn(
                  'font-medium',
                  confirmation.risk_level === 'HIGH' && 'text-orange-500',
                  confirmation.risk_level === 'CRITICAL' && 'text-red-500'
                )}
              >
                {confirmation.risk_level}
              </span>
            </div>
          </div>

          {/* 验证码输入（高风险操作） */}
          {confirmation.requires_code && (
            <div className="space-y-2">
              <p className="text-sm text-red-600">
                这是高风险操作，请输入 CONFIRM 以确认执行
              </p>
              <Input
                className="uppercase"
                onChange={e => setCode(e.target.value)}
                placeholder="输入 CONFIRM"
                value={code}
              />
            </div>
          )}

          {/* 拒绝原因 */}
          <div className="space-y-2">
            <p className="text-muted-foreground text-sm">
              如果拒绝，可以选择填写原因（可选）
            </p>
            <Input
              onChange={e => setReason(e.target.value)}
              placeholder="拒绝原因（可选）"
              value={reason}
            />
          </div>
        </div>

        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            onClick={() => onCancel(reason || undefined)}
            variant="outline"
          >
            取消
          </Button>
          <Button
            disabled={confirmation.requires_code && code !== 'CONFIRM'}
            onClick={handleConfirm}
            variant={
              confirmation.risk_level === 'CRITICAL' ? 'destructive' : 'default'
            }
          >
            确认执行
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
