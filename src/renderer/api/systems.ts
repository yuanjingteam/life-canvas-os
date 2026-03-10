/**
 * 八大系统 API 客户端
 */
import { apiRequest } from './client'

export interface SystemScore {
  type: string
  score: number
}

export interface SystemsScoresResponse {
  systems: SystemScore[]
  average_score: number
  total_systems: number
}

export const systemsApi = {
  /**
   * 获取八大系统评分摘要
   */
  getScores(): Promise<Response> {
    return apiRequest('/api/systems/scores')
  },
}
