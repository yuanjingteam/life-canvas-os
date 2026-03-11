import { useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'
import { Button } from '~/renderer/components/ui/button'
import { cn } from '~/renderer/lib/utils'

export interface ScoreHistoryChartProps {
  data: ScoreHistoryDataPoint[]
  currentScore: number
  isLoading?: boolean
  hasTodayData?: boolean
}

export interface ScoreHistoryDataPoint {
  date: string
  score: number
  timestamp: number
  isCurrent?: boolean
}

export function ScoreHistoryChart({
  data,
  currentScore,
  isLoading = false,
  hasTodayData = false,
}: ScoreHistoryChartProps) {
  // 检测深色模式
  const isDarkMode = document.documentElement.classList.contains('dark')

  // 格式化日期标签
  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))

    if (days === 0) return '今天'
    if (days === 1) return '昨天'
    if (days <= 7) return `${days}天前`
    return `${date.getMonth() + 1}/${date.getDate()}`
  }

  // Tooltip 自定义渲染
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      if (!data) return null
      return (
        <div className="bg-white dark:bg-zinc-800 px-3 py-2 rounded-lg shadow-lg border border-zinc-200 dark:border-zinc-700">
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mb-1">
            {data.isCurrent ? '当前评分' : formatDate(data.timestamp)}
          </p>
          <p className="text-sm font-semibold text-zinc-900 dark:text-white">
            评分：{data.score}
          </p>
        </div>
      )
    }
    return null
  }

  // 准备图表数据：如果今天还没有数据，将 current_score 作为单独的数据点添加
  // 只在有数据的日期显示点，数据点之间直接连接
  const chartData = useMemo(() => {
    if (data.length === 0) return []

    // 如果有当前分数且今天没有数据，添加到末尾
    if (hasTodayData) {
      return data
    }

    // 添加"今天"的当前评分作为最后一个数据点
    return [
      ...data,
      {
        date: '今天',
        score: currentScore,
        timestamp: Date.now(),
        isCurrent: true,
      },
    ]
  }, [data, currentScore, hasTodayData])

  if (isLoading) {
    return (
      <div className="h-[200px] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500" />
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="h-[200px] flex flex-col items-center justify-center text-zinc-400 dark:text-zinc-500">
        <p className="text-sm">暂无历史数据</p>
        <p className="text-xs mt-1">记录偏离事件后将显示评分变化趋势</p>
      </div>
    )
  }

  return (
    <div className="h-[200px] w-full">
      <ResponsiveContainer debounce={50} height="100%" width="100%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="scoreGradient" x1="0" x2="0" y1="0" y2="1">
              <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            stroke={isDarkMode ? 'rgba(255,255,255,0.05)' : '#efeff4'}
            strokeDasharray="3 3"
            vertical={false}
          />
          <XAxis
            axisLine={false}
            dataKey="date"
            tick={{
              fill: isDarkMode ? 'rgba(255,255,255,0.4)' : '#86868b',
              fontSize: 11,
            }}
            tickFormatter={formatDate}
            tickLine={false}
          />
          <YAxis
            axisLine={false}
            domain={[0, 100]}
            tick={{
              fill: isDarkMode ? 'rgba(255,255,255,0.4)' : '#86868b',
              fontSize: 11,
            }}
            tickFormatter={value => value.toString()}
            tickLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            dataKey="score"
            fill="url(#scoreGradient)"
            name="一致性评分"
            stroke="#f97316"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
