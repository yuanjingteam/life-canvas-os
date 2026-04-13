import { TrendingUp } from 'lucide-react'
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { GlassCard } from '~/renderer/components/GlassCard'
import { formatAmount } from '~/renderer/pages/assets/utils/asset-formatters'

interface NetAssetTrendCardProps {
  trend: { date: string; value: number }[]
  maxValue?: number
}

export function NetAssetTrendCard({ trend }: NetAssetTrendCardProps) {
  return (
    <GlassCard className="flex flex-col p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-apple-textMain">
          <TrendingUp className="text-emerald-500" size={16} />
          <span className="font-medium text-sm">净资产趋势（最近12月）</span>
        </div>
      </div>

      <div className="h-40 w-full overflow-hidden">
        <ResponsiveContainer height="100%" width="100%">
          <AreaChart
            data={trend}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorValue" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              axisLine={false}
              dataKey="date"
              minTickGap={20}
              tick={{ fontSize: 10, fill: '#888' }}
              tickLine={false}
            />
            <YAxis domain={['auto', 'auto']} hide />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="rounded-lg border border-apple-border bg-white/90 p-2 text-[10px] shadow-sm backdrop-blur-md dark:bg-black/80">
                      <p className="font-medium text-apple-textMain">
                        {payload[0].payload.date}
                      </p>
                      <p className="text-emerald-500 font-semibold">
                        ¥{formatAmount(payload[0].value as number)}
                      </p>
                    </div>
                  )
                }
                return null
              }}
            />
            <Area
              animationDuration={1500}
              dataKey="value"
              fill="url(#colorValue)"
              fillOpacity={1}
              stroke="#10b981"
              strokeWidth={2}
              type="monotone"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <p className="text-[10px] text-apple-textSec text-center">
        数据自动按月快照生成，反映个人财富增长轨迹。
      </p>
    </GlassCard>
  )
}
