import { Trash2, X, Plus } from 'lucide-react'
import type { RefObject } from 'react'
import { Button } from '~/renderer/components/ui/button'
import { GlassCard } from '~/renderer/components/GlassCard'
import type { CategoryCard } from '~/renderer/pages/assets/components/AssetCategoryGrid'
import { AssetCategoryGrid } from '~/renderer/pages/assets/components/AssetCategoryGrid'

interface AssetCategorySectionProps {
  categories: CategoryCard[]
  editingId: string | null
  onAddCategory: () => void
  onEditEnd: () => void
  onNameChange: (id: string, value: string) => void
  onNavigate: (category: CategoryCard) => void
  onDeleteCategory: (id: string) => void
  isDeleteMode: boolean
  setIsDeleteMode: (mode: boolean) => void
  inputRef: RefObject<HTMLInputElement | null>
}

export function AssetCategorySection({
  categories,
  editingId,
  inputRef,
  onAddCategory,
  onEditEnd,
  onNameChange,
  onNavigate,
  onDeleteCategory,
  isDeleteMode,
  setIsDeleteMode,
}: AssetCategorySectionProps) {
  return (
    <div className="pb-10">
      <div className="mb-4 flex items-end justify-between">
        <div>
          <h2 className="text-lg font-semibold text-apple-textMain">资产分类</h2>
          <p className="text-sm text-apple-textSec">
            每个卡片都是一个小账本，点进去看详情。
          </p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsDeleteMode(!isDeleteMode)}
          className={`gap-2 ${
            isDeleteMode
              ? 'bg-apple-bgSecondary text-apple-textMain hover:bg-apple-bgSecondary/80'
              : 'text-apple-textSec hover:text-apple-textMain'
          }`}
        >
          {isDeleteMode ? (
            <>
              <X size={14} />
              退出管理
            </>
          ) : (
            <>
              <Trash2 size={14} />
              管理分类
            </>
          )}
        </Button>
      </div>
      <AssetCategoryGrid
        categories={categories}
        editingId={editingId}
        inputRef={inputRef}
        onNameChange={onNameChange}
        onEditEnd={onEditEnd}
        onNavigate={onNavigate}
        isDeleteMode={isDeleteMode}
        onDeleteCategory={onDeleteCategory}
        extraCard={
          <GlassCard
            className="flex min-h-[120px] cursor-pointer items-center justify-center border border-dashed border-apple-border/70 bg-white/40 p-5 text-apple-textSec transition hover:-translate-y-0.5 hover:border-apple-accent/40 hover:shadow-lg dark:bg-white/5"
            onClick={onAddCategory}
          >
            <div className="flex flex-col items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full border border-dashed border-apple-border/80 bg-white/70 dark:border-white/20 dark:bg-white/10">
                <Plus size={18} />
              </div>
              <span className="text-sm font-medium">新增分类</span>
            </div>
          </GlassCard>
        }
      />
    </div>
  )
}

