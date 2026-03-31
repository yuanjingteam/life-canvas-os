/**
 * 资产系统 API
 */

import { apiRequest } from './client'

export interface AssetCategorySummary {
  id: number
  name: string
  emoji: string
  color: string
  kind: 'asset' | 'liability'
  total: number
  items_count: number
}

export interface AssetSummary {
  total_assets: number
  total_liabilities: number
  net_assets: number
  categories: AssetCategorySummary[]
}

export interface AssetItem {
  id: number
  category_id: number
  name: string
  amount: number
  note?: string
  created_at: string
  updated_at: string
}

export interface AssetSnapshot {
  id: number
  snapshot_date: string
  total_assets: number
  total_liabilities: number
  net_assets: number
  note?: string
}

export const assetApi = {
  getSummary(): Promise<Response> {
    return apiRequest('/api/assets/summary')
  },

  getSnapshots(params?: { start_date?: string; end_date?: string }): Promise<Response> {
    const query = new URLSearchParams(params as any).toString()
    return apiRequest(`/api/assets/snapshots${query ? `?${query}` : ''}`)
  },

  getCategories(): Promise<Response> {
    return apiRequest('/api/assets/categories')
  },

  createCategory(data: {
    name: string
    emoji?: string
    color?: string
    kind: 'asset' | 'liability'
  }): Promise<Response> {
    return apiRequest('/api/assets/categories', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
  },

  updateCategory(
    id: number,
    data: { name?: string; emoji?: string; color?: string; kind?: 'asset' | 'liability' }
  ): Promise<Response> {
    return apiRequest(`/api/assets/categories/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
  },

  deleteCategory(id: number): Promise<Response> {
    return apiRequest(`/api/assets/categories/${id}`, {
      method: 'DELETE',
    })
  },

  getItems(categoryId: number): Promise<Response> {
    return apiRequest(`/api/assets/categories/${categoryId}/items`)
  },

  createItem(categoryId: number, data: { name: string; amount: number; note?: string }): Promise<Response> {
    return apiRequest(`/api/assets/categories/${categoryId}/items`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
  },

  updateItem(itemId: number, data: { name?: string; amount?: number; note?: string }): Promise<Response> {
    return apiRequest(`/api/assets/items/${itemId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
  },

  deleteItem(itemId: number): Promise<Response> {
    return apiRequest(`/api/assets/items/${itemId}`, {
      method: 'DELETE',
    })
  },
}

