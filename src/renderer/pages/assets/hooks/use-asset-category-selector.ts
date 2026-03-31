import { useMemo, useState } from 'react'
import type { CategoryCard } from '~/renderer/pages/assets/components/AssetCategoryGrid'

export function useAssetCategorySelector(categories: CategoryCard[]) {
  const [categoryQuery, setCategoryQuery] = useState('')
  const [isCategoryOpen, setIsCategoryOpen] = useState(false)
  const normalizedQuery = categoryQuery.trim()
  const hasCategoryMatch =
    normalizedQuery.length > 0 &&
    categories.some(category => category.name.includes(normalizedQuery))
  const createCategoryLabel = normalizedQuery
    ? `新建分类 ${normalizedQuery}`
    : '新建分类'

  const filteredCategories = useMemo(() => {
    if (!normalizedQuery) return categories
    return categories.filter(category => category.name.includes(normalizedQuery))
  }, [categories, normalizedQuery])

  const selectCategory = (name: string) => {
    setCategoryQuery(name)
    setIsCategoryOpen(false)
  }

  const createCategoryFromQuery = (
    onCreate: (name: string) => void
  ) => {
    if (!normalizedQuery) return
    if (categories.some(category => category.name === normalizedQuery)) {
      selectCategory(normalizedQuery)
      return
    }

    onCreate(normalizedQuery)
    setCategoryQuery(normalizedQuery)
    setIsCategoryOpen(false)
  }

  return {
    categories,
    categoryQuery,
    createCategoryLabel,
    createCategoryFromQuery,
    filteredCategories,
    hasCategoryMatch,
    isCategoryOpen,
    normalizedQuery,
    selectCategory,
    setCategoryQuery,
    setIsCategoryOpen,
  }
}

