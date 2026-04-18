import { Wallet } from 'lucide-react'
import { GlassCard } from '~/renderer/components/GlassCard'
import { AnimatedAmount } from './AnimatedAmount'

interface AssetSummaryCardProps {
  totals: {
    assets: string
    liabilities: string
    net: string
  }
}

export function AssetSummaryCard({ totals }: AssetSummaryCardProps) {
  return (
    <GlassCard className="relative overflow-hidden p-6">
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-200/60 via-white/40 to-white/80 dark:from-emerald-500/20 dark:via-white/10 dark:to-white/5" />
      <div className="relative space-y-4">
        <div className="flex items-center gap-2 text-apple-textMain">
          <Wallet size={18} />
          <span className="font-semibold">总资产</span>
        </div>
        <div className="text-4xl font-semibold text-apple-textMain">
          <AnimatedAmount amount={totals.assets} />
        </div>
        <div className="flex flex-wrap gap-3">
          <div className="min-w-[140px] rounded-full border border-white/60 bg-white/70 px-4 py-2 text-sm shadow-sm dark:border-white/10 dark:bg-white/10">
            <p className="text-xs text-apple-textSec">总负债</p>
            <div className="text-base font-semibold text-apple-textMain">
              <AnimatedAmount amount={totals.liabilities} />
            </div>
          </div>
          <div className="min-w-[140px] rounded-full border border-white/60 bg-white/70 px-4 py-2 text-sm shadow-sm dark:border-white/10 dark:bg-white/10">
            <p className="text-xs text-apple-textSec">净资产</p>
            <div className="text-base font-semibold text-apple-textMain">
              <AnimatedAmount amount={totals.net} />
            </div>
          </div>
        </div>
      </div>
    </GlassCard>
  )
}
