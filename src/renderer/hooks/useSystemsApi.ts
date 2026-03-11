/**
 * 八大系统 API 业务逻辑层
 */

import { useCallback } from 'react'
import { toast } from 'sonner'
import { systemsApi } from '~/renderer/api/systems'
import type { DimensionType } from '~/shared/types'

export interface SystemScoreData {
  type: DimensionType
  score: number
}

export function useSystemsApi() {
  /**
   * 获取八大系统评分
   */
  const getSystemsScores = useCallback(async (): Promise<{
    scores: Record<DimensionType, number>
    averageScore: number
  }> => {
    const response = await systemsApi.getScores()

    if (!response.ok) {
      const error = await response.json()
      toast.error('获取系统评分失败', {
        description: error.detail?.message || '请稍后重试',
      })
      throw error
    }

    const result = await response.json()
    const data = result.data

    // 转换为维度评分映射
    const scores = {} as Record<DimensionType, number>
    data.systems.forEach((item: { type: string; score: number }) => {
      scores[item.type as DimensionType] = item.score
    })

    return {
      scores,
      averageScore: data.average_score,
    }
  }, [])

  return {
    getSystemsScores,
  }
}
