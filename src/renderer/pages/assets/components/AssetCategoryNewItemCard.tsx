import { GlassCard } from '~/renderer/components/GlassCard'
import { Button } from '~/renderer/components/ui/button'
import { Input } from '~/renderer/components/ui/input'

interface AssetCategoryNewItemCardProps {
  form: {
    newAmount: string
    newName: string
    onAdd: () => void
    onAmountChange: (value: string) => void
    onNameChange: (value: string) => void
    isValid: boolean
  }
}

export function AssetCategoryNewItemCard({
  form,
}: AssetCategoryNewItemCardProps) {
  return (
    <GlassCard className="p-6">
      <h2 className="text-lg font-semibold text-apple-textMain">新增资产</h2>
      <div className="mt-4 space-y-3">
        <Input
          className="h-9"
          onChange={event => form.onNameChange(event.target.value)}
          placeholder="资产名称"
          value={form.newName}
        />
        <Input
          className="h-9"
          onChange={event => form.onAmountChange(event.target.value)}
          placeholder="金额"
          value={form.newAmount}
        />
        <Button
          className="w-full"
          disabled={!form.isValid}
          onClick={form.onAdd}
        >
          保存
        </Button>
      </div>
    </GlassCard>
  )
}
