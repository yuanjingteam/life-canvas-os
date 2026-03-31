import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { assetApi } from '~/renderer/api/asset'
import type { CategoryCard } from '~/renderer/pages/assets/components/AssetCategoryGrid'
import {
  NEW_CATEGORY_EMOJIS,
} from '~/renderer/pages/assets/data/asset-overview-data'
import {
  formatAmount,
  formatPercent,
} from '~/renderer/pages/assets/utils/asset-formatters'

export function useAssetCategoriesState() {
  const queryClient = useQueryClient()
  const [editingId, setEditingId] = useState<string | null>(null)
  const [isDeleteMode, setIsDeleteMode] = useState(false)
  const inputRef = useRef<HTMLInputElement | null>(null)
  const newIndexRef = useRef(0)

  // 1. 获取汇总数据
  const { data: summary, isLoading } = useQuery({
    queryKey: ['assets', 'summary'],
    queryFn: async () => {
      const res = await assetApi.getSummary()
      if (!res.ok) throw new Error('获取资产汇总失败')
      const result = await res.json()
      return result.data
    },
  })

  // 2. 获取快照数据（用于趋势图）
  const { data: snapshots } = useQuery({
    queryKey: ['assets', 'snapshots'],
    queryFn: async () => {
      const res = await assetApi.getSnapshots()
      if (!res.ok) throw new Error('获取快照失败')
      const result = await res.json()
      return result.data.items || []
    },
  })

  // 3. 各种变更 Mutation
  const createCategoryMutation = useMutation({
    mutationFn: (data: any) => assetApi.createCategory(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['assets'] }),
  })

  const updateCategoryMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      assetApi.updateCategory(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['assets'] }),
  })

  const createItemMutation = useMutation({
    mutationFn: ({ categoryId, data }: { categoryId: number; data: any }) =>
      assetApi.createItem(categoryId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] })
      // 同时失效资产项列表缓存，确保详情页能刷新
      queryClient.invalidateQueries({ queryKey: ['assets', 'category-items'] })
      toast.success('资产已添加')
    },
  })

  useEffect(() => {
    if (editingId && inputRef.current) {
      inputRef.current.focus()
      inputRef.current.select()
    }
  }, [editingId])

  // 映射后端颜色到前端渐变
  const getTone = (color: string) => {
    const toneMap: Record<string, string> = {
      amber: 'from-amber-200/70 via-amber-100/40 to-white/70 dark:from-amber-500/20 dark:via-amber-400/10 dark:to-white/5',
      sky: 'from-sky-200/70 via-sky-100/40 to-white/70 dark:from-sky-500/20 dark:via-sky-400/10 dark:to-white/5',
      emerald: 'from-emerald-200/70 via-emerald-100/40 to-white/70 dark:from-emerald-500/20 dark:via-emerald-400/10 dark:to-white/5',
      orange: 'from-orange-200/70 via-orange-100/40 to-white/70 dark:from-orange-500/20 dark:via-orange-400/10 dark:to-white/5',
      indigo: 'from-indigo-200/70 via-indigo-100/40 to-white/70 dark:from-indigo-500/20 dark:via-indigo-400/10 dark:to-white/5',
      rose: 'from-rose-200/70 via-rose-100/40 to-white/70 dark:from-rose-500/20 dark:via-rose-400/10 dark:to-white/5',
      violet: 'from-violet-200/70 via-violet-100/40 to-white/70 dark:from-violet-500/20 dark:via-violet-400/10 dark:to-white/5',
      slate: 'from-slate-200/70 via-slate-100/40 to-white/70 dark:from-slate-500/20 dark:via-slate-400/10 dark:to-white/5',
      teal: 'from-teal-200/70 via-teal-100/40 to-white/70 dark:from-teal-500/20 dark:via-teal-400/10 dark:to-white/5',
      cyan: 'from-cyan-200/70 via-cyan-100/40 to-white/70 dark:from-cyan-500/20 dark:via-cyan-400/10 dark:to-white/5',
      pink: 'from-pink-200/70 via-pink-100/40 to-white/70 dark:from-pink-500/20 dark:via-pink-400/10 dark:to-white/5',
      lime: 'from-lime-200/70 via-lime-100/40 to-white/70 dark:from-lime-500/20 dark:via-lime-400/10 dark:to-white/5',
    }
    return toneMap[color] || toneMap.amber
  }

  // 格式化后的分类列表
  const displayCategories: CategoryCard[] = useMemo(() => {
    if (!summary?.categories) return []
    const totalAssets = summary.total_assets
    const totalLiabilities = summary.total_liabilities

    return summary.categories.map((cat: any) => {
      const base = totalAssets
      const percent = base > 0 ? (cat.total / base) * 100 : 0
      return {
        id: String(cat.id),
        name: cat.name,
        amount: formatAmount(cat.total),
        percent: formatPercent(percent),
        count: cat.items_count,
        emoji: cat.emoji,
        tone: getTone(cat.color),
      }
    })
  }, [summary])

  const totals = useMemo(() => {
    return {
      assetsValue: summary?.total_assets || 0,
      liabilitiesValue: summary?.total_liabilities || 0,
      netValue: summary?.net_assets || 0,
      assets: formatAmount(summary?.total_assets || 0),
      liabilities: formatAmount(summary?.total_liabilities || 0),
      net: formatAmount(summary?.net_assets || 0),
    }
  }, [summary])

  const trendData = useMemo(() => {
    if (!snapshots || snapshots.length === 0) return []
    // 返回包含日期和数值的对象数组，供图表使用
    return snapshots.slice(0, 12).reverse().map((s: any) => ({
      date: new Date(s.snapshot_date).toLocaleDateString(undefined, { month: 'short' }),
      value: s.net_assets
    }))
  }, [snapshots])

  const handleAddCategory = () => {
    const nextIndex = newIndexRef.current
    newIndexRef.current = (nextIndex + 1) % NEW_CATEGORY_EMOJIS.length
    const colors = ['teal', 'cyan', 'pink', 'lime']
    createCategoryMutation.mutate({
      name: `新分类${displayCategories.length + 1}`,
      emoji: NEW_CATEGORY_EMOJIS[nextIndex],
      color: colors[nextIndex] || 'amber',
      kind: 'asset',
    })
  }

  const handleNameChange = (id: string, value: string) => {
    updateCategoryMutation.mutate({
      id: Number(id),
      data: { name: value },
    })
  }

  const createCategoryFromName = (name: string) => {
    const nextIndex = newIndexRef.current
    newIndexRef.current = (nextIndex + 1) % NEW_CATEGORY_EMOJIS.length
    const colors = ['teal', 'cyan', 'pink', 'lime']
    createCategoryMutation.mutate({
      name,
      emoji: NEW_CATEGORY_EMOJIS[nextIndex],
      color: colors[nextIndex] || 'amber',
      kind: 'asset',
    })
  }

  const handleAddAsset = async (name: string, categoryName: string, amount: number) => {
    let cat = summary?.categories.find((c: any) => c.name === categoryName)
    if (!cat) {
      // 自动创建分类时，补全所有字段以避免 422
      const res = await assetApi.createCategory({
        name: categoryName,
        emoji: '💼',
        color: 'amber',
        kind: categoryName.includes('负债') ? 'liability' : 'asset',
      })
      if (res.ok) {
        const result = await res.json()
        cat = result.data
      }
    }
    if (cat) {
      createItemMutation.mutate({
        categoryId: Number(cat.id),
        data: { name, amount: Number(amount) },
      })
    }
  }

  const [deletingCategoryId, setDeletingCategoryId] = useState<string | null>(null)

  const deleteCategoryMutation = useMutation({
    mutationFn: (id: string) => assetApi.deleteCategory(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets', 'summary'] })
      queryClient.invalidateQueries({ queryKey: ['assets', 'categories'] })
      setDeletingCategoryId(null)
      toast.success('分类已删除')
    },
  })

  const confirmDeleteCategory = () => {
    if (deletingCategoryId) {
      deleteCategoryMutation.mutate(deletingCategoryId)
    }
  }

  return {
    categories: displayCategories,
    createCategoryFromName,
    displayCategories,
    editingId,
    handleAddCategory,
    handleNameChange,
    handleDeleteCategory: (id: string) => setDeletingCategoryId(id),
    deletingCategoryId,
    setDeletingCategoryId,
    confirmDeleteCategory,
    isDeleteMode,
    setIsDeleteMode,
    inputRef,
    maxTrendValue: 0,
    trendData,
    setEditingId,
    totals,
    handleAddAsset,
    isLoading,
  }
}
