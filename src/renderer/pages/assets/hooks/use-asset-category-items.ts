import { useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { assetApi } from '~/renderer/api/asset'
import {
  formatAmount,
  formatPercent,
  parseAmount,
} from '~/renderer/pages/assets/utils/asset-formatters'

export type AssetItem = {
  id: string
  name: string
  amount: string
  updatedAt: string
}

export function useAssetCategoryItems() {
  const { category } = useParams()
  const queryClient = useQueryClient()
  const [editingId, setEditingId] = useState<string | null>(null)
  const [draftName, setDraftName] = useState('')
  const [draftAmount, setDraftAmount] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  // 1. 获取所有分类以匹配当前 categoryName 的 ID
  const { data: summary } = useQuery({
    queryKey: ['assets', 'summary'],
    queryFn: async () => {
      const res = await assetApi.getSummary()
      if (!res.ok) throw new Error('获取资产汇总失败')
      const result = await res.json()
      return result.data
    },
  })

  const currentCategory = useMemo(() => {
    if (!category || !summary?.categories) return null
    const decodedName = decodeURIComponent(category)
    return summary.categories.find((c: any) => c.name === decodedName)
  }, [category, summary])

  const categoryId = currentCategory?.id

  // 2. 获取该分类下的资产项
  const { data: items = [], isLoading } = useQuery({
    queryKey: ['assets', 'category-items', categoryId],
    queryFn: async () => {
      if (!categoryId) return []
      const res = await assetApi.getItems(categoryId)
      if (!res.ok) throw new Error('获取资产项失败')
      const result = await res.json()
      return (result.data?.items || []).map((item: any) => ({
        id: String(item.id),
        name: item.name,
        amount: formatAmount(item.amount),
        updatedAt: new Date(item.updated_at).toLocaleString(),
      }))
    },
    enabled: !!categoryId,
  })

  // 3. Mutation: 更新资产项
  const updateItemMutation = useMutation({
    mutationFn: ({ itemId, data }: { itemId: number; data: any }) =>
      assetApi.updateItem(itemId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets', 'summary'] })
      queryClient.invalidateQueries({
        queryKey: ['assets', 'category-items', categoryId],
      })
      toast.success('资产已更新')
      setEditingId(null)
    },
  })

  // 4. Mutation: 删除资产项
  const deleteItemMutation = useMutation({
    mutationFn: (itemId: number) => assetApi.deleteItem(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets', 'summary'] })
      queryClient.invalidateQueries({
        queryKey: ['assets', 'category-items', categoryId],
      })
      toast.success('资产已删除')
    },
  })

  // 5. Mutation: 新增资产项 (用于详情页内的快捷添加)
  const createItemMutation = useMutation({
    mutationFn: (data: { name: string; amount: number }) =>
      assetApi.createItem(categoryId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets', 'summary'] })
      queryClient.invalidateQueries({
        queryKey: ['assets', 'category-items', categoryId],
      })
      toast.success('资产已添加')
      setEditingId(null)
    },
  })

  const startEdit = (item: AssetItem) => {
    setEditingId(item.id)
    setDraftName(item.name)
    setDraftAmount(item.amount)
  }

  const cancelEdit = () => {
    if (editingId?.startsWith('new-')) {
      // 如果是新添加但未保存的，直接移除
      setEditingId(null)
    } else {
      setEditingId(null)
      setDraftName('')
      setDraftAmount('')
    }
  }

  const saveEdit = () => {
    if (!editingId) return
    const nameValue = draftName.trim()
    const amountValue = parseAmount(draftAmount)
    if (!nameValue || amountValue < 0) return

    if (editingId.startsWith('new-')) {
      createItemMutation.mutate({ name: nameValue, amount: amountValue })
    } else {
      updateItemMutation.mutate({
        itemId: Number(editingId),
        data: { name: nameValue, amount: amountValue },
      })
    }
  }

  const addNewItem = () => {
    const tempId = `new-${Date.now()}`
    setSearchQuery('') // 清除搜索，确保能看到新项
    setEditingId(tempId)
    setDraftName('')
    setDraftAmount('0')

    // 立即在缓存中插入一个空项（可选，或者让 UI 处理）
    // 这里我们通过 editingId 控制 UI 显示一个输入框
  }

  const filteredItems = useMemo(() => {
    let result = [...items]
    // 如果正在新增（tempId），在顶部插入一个虚拟项
    if (editingId?.startsWith('new-')) {
      result = [
        {
          id: editingId,
          name: draftName,
          amount: draftAmount,
          updatedAt: '刚刚',
        },
        ...result,
      ]
    }

    const query = searchQuery.trim().toLowerCase()
    if (!query) return result
    return result.filter((item) => item.name.toLowerCase().includes(query))
  }, [items, searchQuery, editingId, draftName, draftAmount])

  const categorySummary = useMemo(() => {
    if (!currentCategory) {
      return { total: '0', count: 0, percent: '0%' }
    }
    const totalAssets = summary?.total_assets || 0
    const percent = totalAssets > 0 ? (currentCategory.total / totalAssets) * 100 : 0

    return {
      total: formatAmount(currentCategory.total),
      count: currentCategory.items_count,
      percent: formatPercent(percent),
    }
  }, [currentCategory, summary])

  return {
    addNewItem,
    cancelEdit,
    deleteItem: (id: string) => deleteItemMutation.mutate(Number(id)),
    draftAmount,
    draftName,
    editingId,
    filteredItems,
    isLoading,
    items,
    saveEdit,
    searchQuery,
    setDraftAmount,
    setDraftName,
    setSearchQuery,
    startEdit,
    summary: categorySummary,
  }
}

