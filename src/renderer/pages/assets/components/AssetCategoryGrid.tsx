import React, {
  useState,
  useRef,
  useEffect,
  type ReactNode,
  type RefObject,
} from 'react'
import { ArrowRight, X } from 'lucide-react'
import { GlassCard } from '~/renderer/components/GlassCard'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '~/renderer/components/ui/tooltip'
import { Badge } from '~/renderer/components/ui/badge'
import { Input } from '~/renderer/components/ui/input'

export type CategoryCard = {
  id: string
  name: string
  amount: string
  percent: string
  count: number
  emoji: string
  tone: string
}

interface AssetCategoryGridProps {
  categories: CategoryCard[]
  editingId: string | null
  inputRef: RefObject<HTMLInputElement | null>
  onNameChange: (id: string, value: string) => void
  onEditEnd: () => void
  onNavigate: (category: CategoryCard) => void
  isDeleteMode?: boolean
  onDeleteCategory?: (id: string) => void
  extraCard?: ReactNode
}

function TruncatedName({ name }: { name: string }) {
  const [isOverflowing, setIsOverflowing] = useState(false)
  const textRef = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    const el = textRef.current
    if (el) {
      setIsOverflowing(el.scrollWidth > el.clientWidth)
    }
  }, [name])

  const content = (
    <span className="max-w-[120px] truncate font-semibold" ref={textRef}>
      {name}
    </span>
  )

  if (!isOverflowing) return content

  return (
    <Tooltip>
      <TooltipTrigger asChild>{content}</TooltipTrigger>
      <TooltipContent side="top">
        <p>{name}</p>
      </TooltipContent>
    </Tooltip>
  )
}

export function AssetCategoryGrid({
  categories,
  editingId,
  inputRef,
  onNameChange,
  onEditEnd,
  onNavigate,
  isDeleteMode,
  onDeleteCategory,
  extraCard,
}: AssetCategoryGridProps) {
  return (
    <TooltipProvider>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        {categories.map(category => {
          const isEditing = editingId === category.id

          return (
            <GlassCard
              className={`relative min-h-[120px] cursor-pointer overflow-hidden p-5 transition hover:-translate-y-0.5 hover:border-apple-accent/40 hover:shadow-lg ${
                isDeleteMode ? 'border-red-200/50 hover:border-red-400/50' : ''
              }`}
              key={category.id}
              onClick={() => {
                if (isEditing) return
                if (isDeleteMode) {
                  onDeleteCategory?.(category.id)
                } else {
                  onNavigate(category)
                }
              }}
            >
              <div
                className={`absolute inset-0 bg-gradient-to-br ${category.tone}`}
              />
              <div className="relative h-full">
                <div className="flex flex-wrap items-center gap-2 pr-6 text-apple-textMain">
                  <span className="text-lg shrink-0">{category.emoji}</span>
                  {isEditing ? (
                    <Input
                      className="h-7 w-32 bg-white/70 text-sm dark:bg-white/10"
                      onBlur={onEditEnd}
                      onChange={event =>
                        onNameChange(category.id, event.target.value)
                      }
                      onClick={event => event.stopPropagation()}
                      onKeyDown={event => {
                        if (event.key === 'Enter') {
                          event.currentTarget.blur()
                        }
                      }}
                      placeholder="分类名称"
                      ref={inputRef}
                      value={category.name}
                    />
                  ) : (
                    <TruncatedName name={category.name} />
                  )}
                  <Badge className="shrink-0" variant="secondary">
                    {category.percent}
                  </Badge>
                </div>

                {isDeleteMode ? (
                  <X
                    className="absolute top-0 right-0 text-red-500 transition-colors hover:text-red-700"
                    size={18}
                  />
                ) : (
                  <ArrowRight
                    className="absolute top-0 right-0 text-apple-textSec"
                    size={16}
                  />
                )}

                <div className="mt-5">
                  <p className="text-2xl font-semibold text-apple-textMain">
                    {category.amount}
                  </p>
                  <p className="text-xs text-apple-textSec">
                    资产项 {category.count} 条
                  </p>
                </div>
              </div>
            </GlassCard>
          )
        })}
        {extraCard}
      </div>
    </TooltipProvider>
  )
}
