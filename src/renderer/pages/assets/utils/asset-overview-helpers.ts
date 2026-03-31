import type { CategoryCard } from '~/renderer/pages/assets/components/AssetCategoryGrid'

export type AssetTotals = {
  assetsValue: number
  liabilitiesValue: number
  netValue: number
  assets: string
  liabilities: string
  net: string
}

export const updateCategoryName = (
  categories: CategoryCard[],
  id: string,
  value: string
) =>
  categories.map(category =>
    category.id === id ? { ...category, name: value } : category
  )

export const findCategoryByName = (
  categories: CategoryCard[],
  name: string
) => categories.find(category => category.name === name)

