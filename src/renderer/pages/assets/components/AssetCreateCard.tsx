import { Plus, Loader2 } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { GlassCard } from '~/renderer/components/GlassCard'
import { Button } from '~/renderer/components/ui/button'
import { Input } from '~/renderer/components/ui/input'
import type { CategoryCard } from '~/renderer/pages/assets/components/AssetCategoryGrid'
import { useAssetCategorySelector } from '~/renderer/pages/assets/hooks/use-asset-category-selector'
import { parseAmount } from '~/renderer/pages/assets/utils/asset-formatters'

interface AssetCreateCardProps {
  categories: CategoryCard[]
  onAddAsset: (
    name: string,
    categoryName: string,
    amount: number
  ) => Promise<boolean>
  onCreateCategory: (name: string) => void
}

export function AssetCreateCard({
  categories,
  onAddAsset,
  onCreateCategory,
}: AssetCreateCardProps) {
  const [assetName, setAssetName] = useState('')
  const [assetAmount, setAssetAmount] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const {
    categoryQuery,
    createCategoryFromQuery,
    createCategoryLabel,
    filteredCategories,
    hasCategoryMatch,
    isCategoryOpen,
    normalizedQuery,
    selectCategory,
    setCategoryQuery,
    setIsCategoryOpen,
  } = useAssetCategorySelector(categories)

  // 点击外部关闭下拉菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsCategoryOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [setIsCategoryOpen])

  const isAssetFormValid =
    assetName.trim().length > 0 &&
    normalizedQuery.length > 0 &&
    parseAmount(assetAmount) > 0 &&
    !isSubmitting

  const handleAddAsset = async () => {
    const nameValue = assetName.trim()
    const amountValue = parseAmount(assetAmount)
    if (!nameValue || !normalizedQuery || amountValue <= 0) return

    setIsSubmitting(true)
    try {
      const success = await onAddAsset(nameValue, normalizedQuery, amountValue)
      if (success) {
        setAssetName('')
        setAssetAmount('')
        setCategoryQuery('')
        setIsCategoryOpen(false)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <GlassCard className="relative w-[320px] flex-none p-6">
      {/* 背景渐变 */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-amber-200/40 via-white/40 to-white/80 dark:from-amber-500/10 dark:via-white/5 dark:to-white/0" />

      <div className="relative flex h-full flex-col gap-5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100/80 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400">
            <Plus size={20} />
          </div>
          <div>
            <h3 className="text-base font-bold text-apple-textMain">
              新增资产
            </h3>
            <p className="text-[10px] text-apple-textSec">
              记录每一笔财富的增长
            </p>
          </div>
        </div>

        <div className="flex flex-1 flex-col justify-between gap-4">
          <div className="space-y-4">
            {/* 资产名称 */}
            <div className="space-y-1.5">
              <label className="ml-1 text-[11px] font-medium text-apple-textSec">
                资产名称
              </label>
              <Input
                className="h-10 bg-white/70 text-sm shadow-sm dark:bg-white/10"
                onChange={event => setAssetName(event.target.value)}
                placeholder="例如：招商银行储蓄卡"
                value={assetName}
              />
            </div>

            {/* 当前金额 */}
            <div className="space-y-1.5">
              <label className="ml-1 text-[11px] font-medium text-apple-textSec">
                当前金额
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-apple-textSec">
                  ¥
                </span>
                <Input
                  className="h-10 bg-white/70 pl-7 text-sm shadow-sm dark:bg-white/10"
                  onChange={event => setAssetAmount(event.target.value)}
                  placeholder="0.00"
                  value={assetAmount}
                />
              </div>
            </div>

            {/* 所属分类 */}
            <div className="space-y-1.5" ref={containerRef}>
              <label className="ml-1 text-[11px] font-medium text-apple-textSec">
                所属分类
              </label>
              <div className="relative">
                <Input
                  className="h-10 bg-white/70 text-sm shadow-sm dark:bg-white/10"
                  onChange={event => {
                    setCategoryQuery(event.target.value)
                    setIsCategoryOpen(true)
                  }}
                  onFocus={() => setIsCategoryOpen(true)}
                  placeholder="搜索或创建分类"
                  value={categoryQuery}
                />
                {isCategoryOpen ? (
                  <div className="absolute left-0 right-0 top-[46px] z-20 rounded-xl border border-white/60 bg-white/95 p-2 shadow-xl backdrop-blur-md dark:border-white/10 dark:bg-apple-dark/90">
                    {normalizedQuery ? (
                      <button
                        className="flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm text-apple-textMain transition hover:bg-apple-accent/10"
                        onClick={() =>
                          createCategoryFromQuery(onCreateCategory)
                        }
                        type="button"
                      >
                        <span className="flex items-center gap-2">
                          <span className="text-apple-accent font-medium">
                            +
                          </span>
                          {createCategoryLabel}
                        </span>
                        <span className="text-[10px] bg-apple-accent/10 text-apple-accent px-1.5 py-0.5 rounded">
                          新增
                        </span>
                      </button>
                    ) : null}
                    <div className="mt-1 max-h-40 overflow-y-auto pb-2 scrollbar-thin scrollbar-thumb-apple-border">
                      {filteredCategories.length > 0 ? (
                        filteredCategories.map(category => (
                          <button
                            className="flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm text-apple-textMain transition hover:bg-apple-accent/10 group"
                            key={category.id}
                            onClick={() => selectCategory(category.name)}
                            type="button"
                          >
                            <span className="flex items-center gap-2">
                              <span className="text-base group-hover:scale-110 transition-transform">
                                {category.emoji}
                              </span>
                              {category.name}
                            </span>
                            <span className="text-[10px] text-apple-textSec opacity-0 group-hover:opacity-100 transition-opacity">
                              {category.amount}
                            </span>
                          </button>
                        ))
                      ) : hasCategoryMatch ? null : (
                        <div className="px-3 py-2 text-[11px] text-apple-textSec text-center italic">
                          暂无可选分类
                        </div>
                      )}
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          </div>

          <Button
            className="h-11 w-full text-sm font-semibold shadow-md transition-all active:scale-[0.98]"
            disabled={!isAssetFormValid}
            onClick={handleAddAsset}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                保存中...
              </>
            ) : (
              '保存资产'
            )}
          </Button>
        </div>
      </div>
    </GlassCard>
  )
}
