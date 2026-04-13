import { useNavigate } from 'react-router-dom'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '~/renderer/components/ui/dialog'
import { Button } from '~/renderer/components/ui/button'
import { AssetCreateCard } from '~/renderer/pages/assets/components/AssetCreateCard'
import { AssetCategorySection } from '~/renderer/pages/assets/components/AssetCategorySection'
import { AssetSummaryCard } from '~/renderer/pages/assets/components/AssetSummaryCard'
import { NetAssetTrendCard } from '~/renderer/pages/assets/components/NetAssetTrendCard'
import { useAssetCategoriesState } from '~/renderer/pages/assets/hooks/use-asset-categories-state'

export default function AssetOverviewPage() {
  const navigate = useNavigate()
  const {
    createCategoryFromName,
    displayCategories,
    editingId,
    handleAddCategory,
    handleNameChange,
    inputRef,
    maxTrendValue,
    trendData,
    setEditingId,
    totals,
    handleAddAsset,
    isLoading,
    isDeleteMode,
    setIsDeleteMode,
    handleDeleteCategory,
    deletingCategoryId,
    setDeletingCategoryId,
    confirmDeleteCategory,
  } = useAssetCategoriesState()

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-apple-accent border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-apple-textMain">
            资产系统
          </h1>
          <p className="text-sm text-apple-textSec">
            给自己留一份资产小账本，随时掌握余额与变化。
          </p>
        </div>
      </div>

      <div className="flex gap-4 pb-1">
        <div className="flex min-w-[520px] flex-1 flex-col gap-4">
          <AssetSummaryCard totals={totals} />
          <NetAssetTrendCard trend={trendData} />
        </div>
        <AssetCreateCard
          categories={displayCategories}
          onAddAsset={handleAddAsset}
          onCreateCategory={createCategoryFromName}
        />
      </div>

      <AssetCategorySection
        categories={displayCategories}
        editingId={editingId}
        inputRef={inputRef}
        isDeleteMode={isDeleteMode}
        onAddCategory={handleAddCategory}
        onDeleteCategory={handleDeleteCategory}
        onEditEnd={() => setEditingId(null)}
        onNameChange={handleNameChange}
        onNavigate={category =>
          navigate(`/asset/categories/${encodeURIComponent(category.name)}`)
        }
        setIsDeleteMode={setIsDeleteMode}
      />

      <Dialog
        onOpenChange={open => !open && setDeletingCategoryId(null)}
        open={!!deletingCategoryId}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>删除分类</DialogTitle>
            <DialogDescription>
              确定要删除分类 "
              {displayCategories.find(c => c.id === deletingCategoryId)?.name}"
              及其所有资产项吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button onClick={() => setDeletingCategoryId(null)} variant="ghost">
              取消
            </Button>
            <Button onClick={confirmDeleteCategory} variant="destructive">
              确认删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
