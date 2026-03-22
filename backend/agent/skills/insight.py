"""
洞察技能
生成和查询 AI 洞察

使用 Tools：
- DatabaseTool: 数据查询
- InsightService: AI 服务（保留，因为这是复杂的业务逻辑）
"""
from typing import List

from backend.agent.skills.base import BaseSkill, RiskLevel, SkillResult, SkillParameter
from backend.agent.skills.registry import register_skill
from backend.agent.utils.logger import get_logger

logger = get_logger("insight")


@register_skill
class GenerateInsightSkill(BaseSkill):
    """生成洞察技能"""

    @property
    def name(self) -> str:
        return "generate_insight"

    @property
    def description(self) -> str:
        return "基于当前系统评分生成 AI 洞察建议"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.MEDIUM

    @property
    def parameters(self) -> List[SkillParameter]:
        return []

    @property
    def keywords(self) -> List[str]:
        return ["洞察", "生成洞察", "AI 洞察", "建议", "分析", "给我建议"]

    @property
    def examples(self) -> List[str]:
        return ["帮我生成洞察", "给我一些建议", "分析一下我的情况"]

    async def execute(self, **kwargs) -> SkillResult:
        """执行生成洞察"""
        # 使用 db 工具查询用户
        user_result = await self.db.query("user")
        if not user_result.success or not user_result.data:
            return SkillResult(
                success=False,
                message="用户不存在"
            )

        user = user_result.data
        if not user.get("ai_config") or not user["ai_config"].get("provider"):
            return SkillResult(
                success=False,
                message="请先在设置中配置 AI 服务"
            )

        # 调用洞察服务（保留，因为这是复杂的业务逻辑）
        from backend.schemas.insight import InsightGenerateRequest
        from backend.services.insight_service import InsightService

        request = InsightGenerateRequest()
        result, status_code = await InsightService.generate_insight(
            self.db_session, request
        )

        if status_code != 200:
            error_msg = result.get("message", "生成洞察失败")
            if result.get("_limit_reached"):
                return SkillResult(
                    success=True,
                    message=result.get("_message", "今日次数已达上限"),
                    data=result,
                    risk_level=self.risk_level
                )
            return SkillResult(
                success=False,
                message=error_msg
            )

        return SkillResult(
            success=True,
            message="洞察已生成",
            data=result,
            risk_level=self.risk_level
        )


@register_skill
class QueryInsightsSkill(BaseSkill):
    """查询洞察历史技能"""

    @property
    def name(self) -> str:
        return "query_insights"

    @property
    def description(self) -> str:
        return "查询历史洞察记录"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="limit",
                type="integer",
                description="返回数量限制",
                required=False,
                default=5
            )
        ]

    @property
    def keywords(self) -> List[str]:
        return ["洞察历史", "历史洞察", "之前的洞察", "洞察记录"]

    @property
    def examples(self) -> List[str]:
        return ["查看之前的洞察", "最近的洞察历史"]

    async def execute(self, **kwargs) -> SkillResult:
        """执行查询洞察"""
        limit = kwargs.get("limit", 5)

        # 使用 db 工具查询
        result = await self.db.query("insight", {}, limit)

        if not result.success:
            return SkillResult(
                success=False,
                message=result.error or "查询失败"
            )

        items = result.data or []

        if not items:
            return SkillResult(
                success=True,
                message="暂无洞察记录",
                data=[]
            )

        return SkillResult(
            success=True,
            message=f"找到 {len(items)} 条洞察记录",
            data=items,
            risk_level=self.risk_level
        )