"""
资产相关 Skills

实现资产汇总查询、分类查询、资产项创建等功能。
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from .base import BaseSkill, SkillResult, SkillParameter, RiskLevel
from backend.db.session import get_db_context
from backend.models.user import User
from backend.models.asset import AssetCategory, AssetItem
from backend.services.asset_summary_service import AssetSummaryService
from backend.services.asset_item_service import AssetItemService
from backend.schemas.asset import AssetItemCreate
from backend.agent.utils.event_bus import get_event_bus, AgentEvents


class GetAssetSummarySkill(BaseSkill):
    """获取资产汇总 Skill"""

    name = "get_asset_summary"
    description = "获取用户的资产汇总信息，包括总资产、总负债、净资产以及各分类统计"
    trigger_words = ["资产", "财务", "我有多少钱", "负债", "净资产", "资产情况", "资产汇总"]
    risk_level = RiskLevel.LOW

    async def execute(self) -> SkillResult:
        """执行获取资产汇总"""
        try:
            with get_db_context() as db:
                data, status_code = AssetSummaryService.get_summary(db)
                if status_code >= 400:
                    return SkillResult.fail(f"获取资产汇总失败: {data.get('message', '未知错误')}")
                
                # 格式化输出
                summary_text = (
                    f"您的财务概况如下：\n"
                    f"- 总资产: {data['total_assets']:.2f}\n"
                    f"- 总负债: {data['total_liabilities']:.2f}\n"
                    f"- 净资产: {data['net_assets']:.2f}\n\n"
                    f"分类统计：\n"
                )
                
                for cat in data['categories']:
                    summary_text += f"- {cat['emoji']} {cat['name']}: {cat['total']:.2f} ({cat['items_count']}个项目)\n"
                
                return SkillResult.ok(
                    response=summary_text,
                    data=data
                )
        except Exception as e:
            return SkillResult.fail(f"查询资产时发生错误: {str(e)}")


class ListAssetCategoriesSkill(BaseSkill):
    """列出资产分类 Skill"""

    name = "list_asset_categories"
    description = "获取所有的资产和负债分类列表"
    trigger_words = ["资产分类", "负债分类", "哪些分类", "分类列表"]
    risk_level = RiskLevel.LOW

    async def execute(self) -> SkillResult:
        """执行列出分类"""
        try:
            with get_db_context() as db:
                user = db.query(User).first()
                categories = db.query(AssetCategory).filter(AssetCategory.user_id == user.id).all()
                
                if not categories:
                    return SkillResult.ok("您目前还没有创建任何资产分类。")
                
                cat_list = []
                assets = [c for c in categories if c.kind == "asset"]
                liabilities = [c for c in categories if c.kind == "liability"]
                
                message = "您现有的分类如下：\n"
                if assets:
                    message += "\n资产类：\n"
                    for c in assets:
                        message += f"- ID: {c.id} | {c.emoji} {c.name}\n"
                        cat_list.append({"id": c.id, "name": c.name, "kind": "asset"})
                
                if liabilities:
                    message += "\n负债类：\n"
                    for c in liabilities:
                        message += f"- ID: {c.id} | {c.emoji} {c.name}\n"
                        cat_list.append({"id": c.id, "name": c.name, "kind": "liability"})
                
                return SkillResult.ok(response=message, data={"categories": cat_list})
        except Exception as e:
            return SkillResult.fail(f"查询分类时发生错误: {str(e)}")


class CreateAssetItemSkill(BaseSkill):
    """创建资产项 Skill"""

    name = "create_asset_item"
    description = "在指定的分类下新增一项资产或负债（如：在'银行卡'分类下增加'招商银行 5000元'）"
    trigger_words = ["记一笔", "新增资产", "增加负债", "添加资产", "记账", "买入"]
    risk_level = RiskLevel.LOW

    parameters: List[SkillParameter] = [
        SkillParameter(
            name="category_id",
            type="integer",
            description="资产分类ID（可以通过 list_asset_categories 获取）",
            required=True,
        ),
        SkillParameter(
            name="name",
            type="string",
            description="资产名称（如：招商银行、借条）",
            required=True,
        ),
        SkillParameter(
            name="amount",
            type="number",
            description="金额",
            required=True,
        ),
        SkillParameter(
            name="note",
            type="string",
            description="备注信息",
            required=False,
        ),
    ]

    async def execute(
        self,
        category_id: int,
        name: str,
        amount: float,
        note: Optional[str] = None,
    ) -> SkillResult:
        """执行创建资产项"""
        try:
            with get_db_context() as db:
                from backend.schemas.asset import AssetItemCreate
                request = AssetItemCreate(name=name, amount=amount, note=note)
                data, status_code = AssetItemService.create_item(db, category_id, request)
                
                if status_code >= 400:
                    return SkillResult.fail(f"创建资产项失败: {data.get('message', '未知错误')}")
                
                # 触发事件，让前端可以刷新数据
                bus = get_event_bus()
                await bus.emit(AgentEvents.ASSET_CREATED, data)
                
                return SkillResult.ok(
                    response=f"已成功记录：在分类 ID {category_id} 中新增了「{name}」，金额为 {amount:.2f} 元。",
                    data=data
                )
        except Exception as e:
            return SkillResult.fail(f"创建资产项时发生错误: {str(e)}")
