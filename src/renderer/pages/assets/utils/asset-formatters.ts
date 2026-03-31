import type { CategoryCard } from '~/renderer/pages/assets/components/AssetCategoryGrid'

export const parseAmount = (value: string) => {
  const normalized = value.replace(/[¥,\s]/g, '')
  const parsed = Number.parseFloat(normalized)
  return Number.isNaN(parsed) ? 0 : parsed
}

export const formatAmount = (value: number) =>
  value.toLocaleString('zh-CN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })

export const formatPercent = (value: number) => `${value.toFixed(1)}%`

export const isLiabilityCategory = (category: CategoryCard) =>
  category.id === 'liability' || category.name.includes('负债')

