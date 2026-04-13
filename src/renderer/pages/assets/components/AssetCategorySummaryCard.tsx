import { GlassCard } from '~/renderer/components/GlassCard'

interface AssetCategorySummaryCardProps {
  summary: {
    total: string
    percent: string
    count: number
  }
}

export function AssetCategorySummaryCard({
  summary,
}: AssetCategorySummaryCardProps) {
  return (
    <GlassCard className="p-6">
      <h2 className="text-lg font-semibold text-apple-textMain">分类概览</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-xl border border-white/40 bg-white/60 p-4 dark:border-white/10 dark:bg-white/5">
          <p className="text-xs text-apple-textSec">总金额</p>
          <p className="text-lg font-semibold text-apple-textMain">
            ¥{summary.total}
          </p>
        </div>
        <div className="rounded-xl border border-white/40 bg-white/60 p-4 dark:border-white/10 dark:bg-white/5">
          <p className="text-xs text-apple-textSec">占比</p>
          <p className="text-lg font-semibold text-apple-textMain">
            {summary.percent}
          </p>
        </div>
        <div className="rounded-xl border border-white/40 bg-white/60 p-4 dark:border-white/10 dark:bg-white/5">
          <p className="text-xs text-apple-textSec">条目数</p>
          <p className="text-lg font-semibold text-apple-textMain">
            {summary.count}
          </p>
        </div>
      </div>
    </GlassCard>
  )
}
