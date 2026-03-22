"""
饮食系统技能
处理饮食基准、偏离事件、统计信息

设计说明：
- 简单CRUD操作：使用 DatabaseTool
- 复杂业务逻辑：直接调用 DietService（如评分联动更新、基准解析）
- 上下文引用：使用 BaseSkill.get_context_entity_id()

使用 Tools：
- DatabaseTool: 数据 CRUD（偏离记录查询、更新）
- DateTimeTool: 日期解析
- ContextTool: 上下文存取
- DietService: 复杂业务逻辑（基准更新、评分联动）
"""
from typing import Any, Dict, List, Optional
from datetime import datetime

from backend.agent.skills.base import BaseSkill, RiskLevel, SkillResult, SkillParameter
from backend.agent.skills.registry import register_skill
from backend.agent.utils.logger import get_logger

logger = get_logger("diet")

# 餐食类型枚举值（用于参数约束）
MEAL_TYPE_ENUMS = ["breakfast", "lunch", "dinner", "taste"]


@register_skill
class GetDietBaselineSkill(BaseSkill):
    """获取饮食基准技能"""

    @property
    def name(self) -> str:
        return "get_diet_baseline"

    @property
    def description(self) -> str:
        return "获取用户设置的饮食基准（早餐、午餐、晚餐、口味）"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW

    @property
    def parameters(self) -> List[SkillParameter]:
        return []

    @property
    def keywords(self) -> List[str]:
        return ["饮食基准", "我的基准", "早餐基准", "午餐基准", "晚餐基准", "口味偏好"]

    @property
    def examples(self) -> List[str]:
        return ["我的饮食基准是什么？", "查看早餐基准", "我的口味偏好有哪些？"]

    async def execute(self, **kwargs) -> SkillResult:
        """执行获取饮食基准"""
        # 使用 DietService（保留复杂业务逻辑）
        from backend.services.diet_service import DietService

        result, status_code = DietService.get_fuel_baseline(self.db_session)

        if status_code != 200:
            return SkillResult(
                success=False,
                message=result.get("message", "获取饮食基准失败")
            )

        baseline = result.get("data", {})
        breakfast = baseline.get("breakfast", [])
        lunch = baseline.get("lunch", [])
        dinner = baseline.get("dinner", [])
        taste = baseline.get("taste", [])

        # 构建友好消息
        msg_parts = []
        if breakfast:
            items = [f"{i.get('name', '')}({i.get('amount', '')})" for i in breakfast]
            msg_parts.append(f"早餐: {', '.join(items)}")
        if lunch:
            items = [f"{i.get('name', '')}({i.get('amount', '')})" for i in lunch]
            msg_parts.append(f"午餐: {', '.join(items)}")
        if dinner:
            items = [f"{i.get('name', '')}({i.get('amount', '')})" for i in dinner]
            msg_parts.append(f"晚餐: {', '.join(items)}")
        if taste:
            msg_parts.append(f"口味偏好: {', '.join(taste)}")

        if msg_parts:
            message = "您的饮食基准:\n" + "\n".join(msg_parts)
        else:
            message = "您还没有设置饮食基准"

        return SkillResult(
            success=True,
            message=message,
            data=baseline,
            risk_level=self.risk_level
        )


@register_skill
class UpdateDietBaselineSkill(BaseSkill):
    """更新饮食基准技能"""

    @property
    def name(self) -> str:
        return "update_diet_baseline"

    @property
    def description(self) -> str:
        return "更新饮食基准（早餐、午餐、晚餐或口味）"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.MEDIUM

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="meal_type",
                type="string",
                description="餐食类型: breakfast, lunch, dinner, taste",
                required=True,
                enum=MEAL_TYPE_ENUMS
            ),
            SkillParameter(
                name="items",
                type="array",
                description="餐食项列表（JSON格式），口味时为字符串数组",
                required=True
            )
        ]

    @property
    def keywords(self) -> List[str]:
        return ["更新基准", "修改基准", "设置早餐", "设置午餐", "设置晚餐", "添加口味", "修改口味"]

    @property
    def examples(self) -> List[str]:
        return [
            "把早餐基准改成牛奶面包",
            "添加一个口味偏好：清淡",
            "设置午餐基准"
        ]

    async def execute(self, **kwargs) -> SkillResult:
        """执行更新饮食基准"""
        from backend.services.diet_service import DietService
        from backend.schemas.system import FuelBaselineUpdate, MealItem

        meal_type = kwargs.get("meal_type", "")
        items = kwargs.get("items", [])

        # 业务逻辑验证
        if not meal_type:
            return SkillResult(
                success=False,
                message="请指定要更新的餐食类型（breakfast/lunch/dinner/taste）"
            )

        if not items:
            return SkillResult(
                success=False,
                message="请提供要设置的内容"
            )

        # 构建更新请求
        update_data = {}

        if meal_type == "taste":
            update_data["taste"] = items if isinstance(items, list) else [items]
        else:
            meal_items = []
            for item in items:
                if isinstance(item, dict):
                    meal_items.append(MealItem(
                        name=item.get("name", ""),
                        amount=item.get("amount", "适量"),
                        calories=item.get("calories")
                    ))
                elif isinstance(item, str):
                    meal_items.append(MealItem(
                        name=item,
                        amount="适量"
                    ))

            if meal_type == "breakfast":
                update_data["breakfast"] = meal_items
            elif meal_type == "lunch":
                update_data["lunch"] = meal_items
            elif meal_type == "dinner":
                update_data["dinner"] = meal_items
            else:
                return SkillResult(
                    success=False,
                    message=f"未知的餐食类型: {meal_type}"
                )

        # 使用 DietService（保留复杂业务逻辑）
        update_request = FuelBaselineUpdate(**update_data)
        result, status_code = DietService.update_fuel_baseline(
            self.db_session, update_request
        )

        if status_code != 200:
            return SkillResult(
                success=False,
                message=result.get("message", "更新饮食基准失败")
            )

        return SkillResult(
            success=True,
            message=f"已更新{meal_type}基准",
            data=result.get("data"),
            risk_level=self.risk_level
        )


@register_skill
class CreateMealDeviationSkill(BaseSkill):
    """记录饮食偏离技能"""

    @property
    def name(self) -> str:
        return "create_meal_deviation"

    @property
    def description(self) -> str:
        return "记录一次饮食偏离事件（如吃了不健康的食物）"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="description",
                type="string",
                description="偏离描述，如：喝了奶茶、吃了炸鸡",
                required=True
            )
        ]

    @property
    def keywords(self) -> List[str]:
        return ["记录偏离", "饮食偏离", "吃了", "喝了", "奶茶", "炸鸡", "零食", "垃圾食品"]

    @property
    def examples(self) -> List[str]:
        return [
            "今天喝了奶茶，记录一下",
            "记录一次饮食偏离：吃炸鸡",
            "我吃了零食，帮我记录"
        ]

    async def execute(self, **kwargs) -> SkillResult:
        """执行记录饮食偏离"""
        from backend.services.diet_service import DietService
        from backend.schemas.system import MealDeviationCreate

        description = kwargs.get("description", "")

        # 业务逻辑验证
        if not description:
            return SkillResult(
                success=False,
                message="请描述偏离内容"
            )

        # 使用 DietService 创建偏离事件（会触发评分更新）
        request = MealDeviationCreate(description=description)
        result, status_code = DietService.create_meal_deviation(self.db_session, request)

        if status_code != 201:
            return SkillResult(
                success=False,
                message=result.get("message", "记录偏离失败")
            )

        deviation_data = result  # 已经是 dict 格式

        # 使用 ctx 工具记录上下文
        if self.ctx and deviation_data:
            self.ctx.set_sync("last_deviation_id", deviation_data.get("id"))

        return SkillResult(
            success=True,
            message=f"已记录饮食偏离: {description}",
            data=deviation_data,
            risk_level=self.risk_level
        )


@register_skill
class GetMealDeviationsSkill(BaseSkill):
    """查询饮食偏离记录技能"""

    @property
    def name(self) -> str:
        return "get_meal_deviations"

    @property
    def description(self) -> str:
        return "查询饮食偏离记录列表"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="date_expression",
                type="string",
                description="自然语言日期表达式（如：最近一周、本月）",
                required=False
            ),
            SkillParameter(
                name="start_date",
                type="string",
                description="开始日期（YYYY-MM-DD）",
                required=False
            ),
            SkillParameter(
                name="end_date",
                type="string",
                description="结束日期（YYYY-MM-DD）",
                required=False
            ),
            SkillParameter(
                name="limit",
                type="integer",
                description="返回数量限制",
                required=False,
                default=10
            )
        ]

    @property
    def keywords(self) -> List[str]:
        return ["偏离记录", "偏离历史", "最近偏离", "本月偏离", "查看偏离"]

    @property
    def examples(self) -> List[str]:
        return [
            "最近的饮食偏离有哪些？",
            "查看本月偏离记录",
            "最近一周的偏离记录"
        ]

    async def execute(self, **kwargs) -> SkillResult:
        """执行查询偏离记录"""
        date_expression = kwargs.get("date_expression")
        limit = kwargs.get("limit", 10)
        filters = {}

        # 使用 datetime 工具解析日期表达式
        if date_expression:
            dt_result = await self.datetime.execute(
                expression=date_expression,
                format="range"
            )
            if dt_result.success:
                filters["start_date"] = dt_result.data.get("start_date")
                filters["end_date"] = dt_result.data.get("end_date")
        else:
            if kwargs.get("start_date"):
                filters["start_date"] = kwargs["start_date"]
            if kwargs.get("end_date"):
                filters["end_date"] = kwargs["end_date"]

        # 使用 db 工具查询
        result = await self.db.query("deviation", filters, limit)

        if not result.success:
            return SkillResult(
                success=False,
                message=result.error or "查询失败"
            )

        items = result.data or []

        if not items:
            return SkillResult(
                success=True,
                message="暂无偏离记录，继续保持！",
                data={"items": []},
                risk_level=self.risk_level
            )

        # 构建友好消息
        lines = [f"找到 {len(items)} 条偏离记录:"]
        for item in items[:5]:
            occurred = item.get("occurred_at", "")
            if isinstance(occurred, str) and occurred:
                date_str = occurred[:10]
            else:
                date_str = ""
            desc = item.get("description", "")
            lines.append(f"- {date_str}: {desc}")

        if len(items) > 5:
            lines.append(f"... 还有 {len(items) - 5} 条")

        return SkillResult(
            success=True,
            message="\n".join(lines),
            data={"items": items},
            risk_level=self.risk_level
        )


@register_skill
class UpdateMealDeviationSkill(BaseSkill):
    """更新偏离记录技能"""

    @property
    def name(self) -> str:
        return "update_meal_deviation"

    @property
    def description(self) -> str:
        return "更新偏离记录的描述"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.MEDIUM

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="deviation_id",
                type="integer",
                description="偏离记录ID（可省略，使用最近的记录）",
                required=False
            ),
            SkillParameter(
                name="description",
                type="string",
                description="新的描述内容",
                required=True
            )
        ]

    @property
    def keywords(self) -> List[str]:
        return ["修改偏离", "更新偏离", "编辑偏离记录"]

    @property
    def examples(self) -> List[str]:
        return [
            "修改刚才那条偏离记录",
            "更新偏离描述"
        ]

    async def execute(self, **kwargs) -> SkillResult:
        """执行更新偏离记录"""
        description = kwargs.get("description", "")

        # 使用 get_context_entity_id 获取偏离记录ID
        deviation_id = self.get_context_entity_id(
            "last_deviation_id", kwargs.get("deviation_id")
        )

        if not deviation_id:
            return SkillResult(
                success=False,
                message="请指定要修改的偏离记录"
            )

        if not description:
            return SkillResult(
                success=False,
                message="请提供新的描述内容"
            )

        # 使用 db 工具更新
        result = await self.db.update("deviation", deviation_id, {"description": description})

        if not result.success:
            return SkillResult(
                success=False,
                message=result.error or "更新失败"
            )

        return SkillResult(
            success=True,
            message="偏离记录已更新",
            data=result.data,
            risk_level=self.risk_level
        )


@register_skill
class DeleteMealDeviationSkill(BaseSkill):
    """删除偏离记录技能"""

    @property
    def name(self) -> str:
        return "delete_meal_deviation"

    @property
    def description(self) -> str:
        return "删除一条饮食偏离记录（需要确认）"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.HIGH

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="deviation_id",
                type="integer",
                description="偏离记录ID（可省略，使用最近的记录）",
                required=False
            )
        ]

    @property
    def keywords(self) -> List[str]:
        return ["删除偏离", "移除偏离", "删掉偏离"]

    @property
    def examples(self) -> List[str]:
        return [
            "删掉刚才那条偏离记录",
            "删除最近的偏离记录"
        ]

    def check_confirmation_required(self, **kwargs) -> bool:
        """删除操作始终需要确认"""
        return True

    async def execute(self, **kwargs) -> SkillResult:
        """执行删除偏离记录"""
        from backend.services.diet_service import DietService

        # 使用 get_context_entity_id 获取偏离记录ID
        deviation_id = self.get_context_entity_id(
            "last_deviation_id", kwargs.get("deviation_id")
        )

        if not deviation_id:
            return SkillResult(
                success=False,
                message="请指定要删除的偏离记录"
            )

        # 使用 DietService 删除偏离事件（会触发评分更新）
        result, status_code = DietService.delete_meal_deviation(self.db_session, deviation_id)

        if status_code != 200:
            return SkillResult(
                success=False,
                message=result.get("message", "删除失败")
            )

        return SkillResult(
            success=True,
            message=f"已删除偏离记录",
            data=result,
            risk_level=self.risk_level
        )


@register_skill
class GetDietStatisticsSkill(BaseSkill):
    """获取饮食统计技能"""

    @property
    def name(self) -> str:
        return "get_diet_statistics"

    @property
    def description(self) -> str:
        return "获取饮食统计信息（偏离次数、一致性分数等）"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW

    @property
    def parameters(self) -> List[SkillParameter]:
        return []

    @property
    def keywords(self) -> List[str]:
        return ["饮食统计", "统计信息", "我的饮食", "饮食报告", "一致性分数"]

    @property
    def examples(self) -> List[str]:
        return [
            "我的饮食统计怎么样？",
            "查看饮食统计",
            "我的饮食一致性分数是多少？"
        ]

    async def execute(self, **kwargs) -> SkillResult:
        """执行获取饮食统计"""
        from backend.services.diet_service import DietService

        result, status_code = DietService.get_fuel_statistics(self.db_session)

        if status_code != 200:
            return SkillResult(
                success=False,
                message=result.get("message", "获取饮食统计失败")
            )

        data = result.get("data", {})
        total = data.get("total_deviations", 0)
        monthly = data.get("monthly_deviations", 0)

        # 获取系统评分信息
        system_result = await self.db.query("system", {"system_type": "FUEL"})
        consistency = 100
        if system_result.success and system_result.data:
            details = system_result.data[0].get("details", {})
            consistency = details.get("consistency", 100) if details else 100

        lines = [
            "饮食统计:",
            f"- 总偏离次数: {total} 次",
            f"- 本月偏离: {monthly} 次",
            f"- 一致性分数: {consistency} 分"
        ]

        # 添加建议
        if consistency >= 90:
            lines.append("\n太棒了！您的饮食习惯非常健康！")
        elif consistency >= 70:
            lines.append("\n不错，继续保持健康饮食！")
        else:
            lines.append("\n建议：尝试减少不健康食物的摄入，提高饮食一致性。")

        return SkillResult(
            success=True,
            message="\n".join(lines),
            data={"consistency": consistency, **data},
            risk_level=self.risk_level
        )


@register_skill
class GetDietScoreHistorySkill(BaseSkill):
    """获取饮食评分历史技能"""

    @property
    def name(self) -> str:
        return "get_diet_score_history"

    @property
    def description(self) -> str:
        return "获取饮食评分变化历史"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="days",
                type="integer",
                description="查询天数范围（默认30天）",
                required=False,
                default=30
            )
        ]

    @property
    def keywords(self) -> List[str]:
        return ["评分历史", "评分变化", "饮食评分历史", "历史趋势"]

    @property
    def examples(self) -> List[str]:
        return [
            "查看饮食评分历史",
            "最近一个月的评分变化",
            "我的饮食评分趋势"
        ]

    async def execute(self, **kwargs) -> SkillResult:
        """执行获取评分历史"""
        from backend.services.diet_service import DietService

        days = kwargs.get("days", 30)

        result, status_code = DietService.get_score_history(
            self.db_session, days=days
        )

        if status_code != 200:
            return SkillResult(
                success=False,
                message=result.get("message", "获取评分历史失败")
            )

        data = result.get("data", {})
        current_score = data.get("current_score", 0)
        history = data.get("history", [])

        lines = [
            f"饮食系统当前评分: {current_score} 分",
            f"查询范围: 最近 {days} 天",
        ]

        if history:
            lines.append(f"评分变化记录 ({len(history)} 条):")
            for log in history[:5]:
                created = log.get("created_at", "")
                old = log.get("old_score", 0)
                new = log.get("new_score", 0)
                reason = log.get("change_reason", "")
                change = new - old
                sign = "+" if change >= 0 else ""
                lines.append(f"- {created[:10]}: {old} -> {new} ({sign}{change}) {reason}")
        else:
            lines.append("暂无评分变化记录")

        return SkillResult(
            success=True,
            message="\n".join(lines),
            data=data,
            risk_level=self.risk_level
        )