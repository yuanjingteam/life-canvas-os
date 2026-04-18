import { useMemo, useState, useRef, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Pencil, Check, X } from 'lucide-react'
import { Button } from '~/renderer/components/ui/button'
import { Input } from '~/renderer/components/ui/input'
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
  const [itemToDelete, setItemToDelete] = useState<{
    id: string
    name: string
  } | null>(null)

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
    updateCategoryName,
    currentCategory,
  } = useAssetCategoryItems()

  const [isEditingTitle, setIsEditingTitle] = useState(false)
  const [titleDraft, setTitleDraft] = useState('')
  const titleInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (isEditingTitle && titleInputRef.current) {
      titleInputRef.current.focus()
    }
  }, [isEditingTitle])

  const categoryName = useMemo(() => {
    if (!category) return '分类详情'
    return decodeURIComponent(category)
  }, [category])

  useEffect(() => {
    setTitleDraft(categoryName)
  }, [categoryName])

  const handleTitleSave = () => {
    if (titleDraft.trim() && titleDraft !== categoryName) {
      updateCategoryName(titleDraft)
      navigate(`/asset/categories/${encodeURIComponent(titleDraft)}`, {
        replace: true,
      })
    }
    setIsEditingTitle(false)
  }

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
          <div className="group relative flex items-center gap-2">
            {isEditingTitle ? (
              <div className="flex items-center gap-2">
                <Input
                  className="h-8 w-48 bg-white/70 text-lg font-semibold dark:bg-white/10"
                  onBlur={() => setIsEditingTitle(false)}
                  onChange={e => setTitleDraft(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') handleTitleSave()
                    if (e.key === 'Escape') setIsEditingTitle(false)
                  }}
                  ref={titleInputRef}
                  value={titleDraft}
                />
                <Button
                  className="h-8 w-8 text-emerald-500"
                  onClick={handleTitleSave}
                  size="icon"
                  variant="ghost"
                >
                  <Check size={16} />
                </Button>
                <Button
                  className="h-8 w-8 text-rose-500"
                  onClick={() => setIsEditingTitle(false)}
                  size="icon"
                  variant="ghost"
                >
                  <X size={16} />
                </Button>
              </div>
            ) : (
              <>
                <h1 className="text-xl font-semibold text-apple-textMain">
                  {categoryName}
                </h1>
                <Button
                  className="h-8 w-8 opacity-0 transition-opacity group-hover:opacity-100"
                  onClick={() => {
                    setTitleDraft(categoryName)
                    setIsEditingTitle(true)
                  }}
                  size="icon"
                  variant="ghost"
                >
                  <Pencil size={14} className="text-apple-textSec" />
                </Button>
              </>
            )}
          </div>
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

      <Dialog
        onOpenChange={open => !open && setItemToDelete(null)}
        open={!!itemToDelete}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除资产项</DialogTitle>
            <DialogDescription>
              确定要删除 “{itemToDelete?.name}” 吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button onClick={() => setItemToDelete(null)} variant="ghost">
              取消
            </Button>
            <Button
              onClick={async () => {
                if (itemToDelete) {
                  await deleteItem(itemToDelete.id)
                  setItemToDelete(null)
                }
              }}
              variant="destructive"
            >
              确认删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
