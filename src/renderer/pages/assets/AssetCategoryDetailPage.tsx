import { useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '~/renderer/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '~/renderer/components/ui/dialog'
import { AssetCategoryItemList } from '~/renderer/pages/assets/components/AssetCategoryItemList'
import { AssetCategorySummaryCard } from '~/renderer/pages/assets/components/AssetCategorySummaryCard'
import { useAssetCategoryItems } from '~/renderer/pages/assets/hooks/use-asset-category-items'

export default function AssetCategoryDetailPage() {
  const navigate = useNavigate()
  const { category } = useParams()
  const [itemToDelete, setItemToDelete] = useState<{ id: string; name: string } | null>(null)

  const {
    addNewItem,
    cancelEdit,
    deleteItem,
    draftAmount,
    draftName,
    editingId,
    filteredItems,
    items,
    saveEdit,
    searchQuery,
    setDraftAmount,
    setDraftName,
    setSearchQuery,
    startEdit,
    summary,
  } = useAssetCategoryItems()

  const categoryName = useMemo(() => {
    if (!category) return '分类详情'
    return decodeURIComponent(category)
  }, [category])

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Button
            className="h-9 w-9 shrink-0"
            onClick={() => navigate(-1)}
            size="icon"
            variant="ghost"
          >
            <ArrowLeft size={18} />
          </Button>
          <div>
            <h1 className="text-xl font-semibold text-apple-textMain">
              {categoryName}
            </h1>
            <p className="text-[11px] text-apple-textSec">
              查看该分类下的资产明细。
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4">
        <AssetCategorySummaryCard summary={summary} />
      </div>

      <AssetCategoryItemList
        data={{
          draftAmount,
          draftName,
          editingId,
          filteredItems,
          itemsCount: items.length,
          searchQuery,
        }}
        handlers={{
          onAddNew: addNewItem,
          onCancelEdit: cancelEdit,
          onDeleteItem: (id, name) => setItemToDelete({ id, name }),
          onDraftAmountChange: setDraftAmount,
          onDraftNameChange: setDraftName,
          onSaveEdit: saveEdit,
          onSearchChange: setSearchQuery,
          onStartEdit: startEdit,
        }}
      />

      <Dialog open={!!itemToDelete} onOpenChange={open => !open && setItemToDelete(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除资产项</DialogTitle>
            <DialogDescription>
              确定要删除 “{itemToDelete?.name}” 吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setItemToDelete(null)}>
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={async () => {
                if (itemToDelete) {
                  await deleteItem(itemToDelete.id)
                  setItemToDelete(null)
                }
              }}
            >
              确认删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
