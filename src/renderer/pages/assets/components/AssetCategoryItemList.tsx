import { Check, Pencil, Plus, Trash2, X } from 'lucide-react'
import { GlassCard } from '~/renderer/components/GlassCard'
import { Button } from '~/renderer/components/ui/button'
import { Input } from '~/renderer/components/ui/input'
import type { AssetItem } from '~/renderer/pages/assets/hooks/use-asset-category-items'
import { formatAmount, parseAmount } from '~/renderer/pages/assets/utils/asset-formatters'

interface AssetCategoryItemListProps {
  data: {
    draftAmount: string
    draftName: string
    editingId: string | null
    filteredItems: AssetItem[]
    itemsCount: number
    searchQuery: string
  }
  handlers: {
    onAddNew: () => void
    onCancelEdit: () => void
    onDeleteItem: (id: string, name: string) => void
    onDraftAmountChange: (value: string) => void
    onDraftNameChange: (value: string) => void
    onSaveEdit: () => void
    onSearchChange: (value: string) => void
    onStartEdit: (item: AssetItem) => void
  }
}

export function AssetCategoryItemList({
  data,
  handlers,
}: AssetCategoryItemListProps) {
  return (
    <GlassCard className="p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-apple-textMain">资产项</h2>
        <div className="flex items-center gap-2">
          <Input
            className="h-9 w-full max-w-[220px] bg-white/70 text-sm dark:bg-white/10"
            placeholder="搜索资产"
            value={data.searchQuery}
            onChange={event => handlers.onSearchChange(event.target.value)}
          />
          <Button
            className="h-9 w-9 shrink-0 shadow-sm"
            onClick={handlers.onAddNew}
            size="icon"
          >
            <Plus size={18} />
          </Button>
        </div>
      </div>
      <div className="mt-4 space-y-3">
        {data.filteredItems.length === 0 ? (
          <div className="rounded-xl border border-dashed border-white/50 bg-white/40 p-6 text-center text-sm text-apple-textSec dark:border-white/10 dark:bg-white/5">
            {data.itemsCount === 0
              ? '还没有资产条目，点击上方的加号新增一笔。'
              : '没有匹配的资产。'}
          </div>
        ) : (
          data.filteredItems.map(item => {
            const isEditing = data.editingId === item.id

            return (
              <div
                className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/40 bg-white/60 px-4 py-3 dark:border-white/10 dark:bg-white/5"
                key={item.id}
              >
                <div className="min-w-[180px] flex-1">
                  {isEditing ? (
                    <Input
                      className="h-8 max-w-[220px] bg-white/80 text-sm dark:bg-white/10"
                      value={data.draftName}
                      onChange={event =>
                        handlers.onDraftNameChange(event.target.value)
                      }
                    />
                  ) : (
                    <p className="font-medium text-apple-textMain">{item.name}</p>
                  )}
                  <p
                    className={`text-xs text-apple-textSec ${
                      isEditing ? 'opacity-0' : ''
                    }`}
                    aria-hidden={isEditing}
                  >
                    最近更新：{item.updatedAt}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  {isEditing ? (
                    <>
                      <Input
                        className="h-8 w-[120px] bg-white/80 text-sm dark:bg-white/10"
                        value={data.draftAmount}
                        onChange={event =>
                          handlers.onDraftAmountChange(event.target.value)
                        }
                      />
                      <Button
                        size="icon"
                        variant="ghost"
                        className="text-rose-500 hover:text-rose-600"
                        onClick={handlers.onCancelEdit}
                      >
                        <X size={16} />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        className="text-emerald-500 hover:text-emerald-600"
                        onClick={handlers.onSaveEdit}
                      >
                        <Check size={16} />
                      </Button>
                    </>
                  ) : (
                    <>
                      <span className="text-sm font-semibold text-apple-textMain">
                        ¥{formatAmount(parseAmount(item.amount))}
                      </span>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => handlers.onStartEdit(item)}
                      >
                        <Pencil size={16} />
                      </Button>
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => handlers.onDeleteItem(item.id, item.name)}
                      >
                        <Trash2 size={16} />
                      </Button>
                    </>
                  )}
                </div>
              </div>
            )
          })
        )}
      </div>
    </GlassCard>
  )
}

