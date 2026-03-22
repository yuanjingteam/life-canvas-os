"""
日记技能
处理日记的创建、查询、更新、删除

设计说明：
- 简单CRUD操作：使用 DatabaseTool
- 上下文引用：使用 BaseSkill.get_context_entity_id()

使用 Tools：
- DatabaseTool: 数据 CRUD
- DateTimeTool: 日期解析
- ContextTool: 上下文存取
"""
from typing import Any, Dict, List, Optional

from backend.agent.skills.base import BaseSkill, RiskLevel, SkillResult, SkillParameter
from backend.agent.skills.registry import register_skill
from backend.agent.utils.logger import get_logger

logger = get_logger("journal")

# 心情枚举值（用于参数约束，与前端保持一致）
MOOD_ENUMS = ["great", "good", "neutral", "bad", "terrible"]

# 中文心情到英文枚举的映射（支持用户用中文描述心情）
MOOD_CN_TO_EN = {
    # great - 很棒
    "很棒": "great",
    "超棒": "great",
    "太棒了": "great",
    "极好": "great",
    "兴奋": "great",
    "开心极了": "great",
    # good - 不错
    "不错": "good",
    "开心": "good",
    "高兴": "good",
    "快乐": "good",
    "愉快": "good",
    "好": "good",
    "挺好": "good",
    # neutral - 一般
    "一般": "neutral",
    "平静": "neutral",
    "普通": "neutral",
    "还好": "neutral",
    "正常": "neutral",
    "平淡": "neutral",
    # bad - 不好
    "不好": "bad",
    "难过": "bad",
    "伤心": "bad",
    "郁闷": "bad",
    "烦躁": "bad",
    "焦虑": "bad",
    "疲惫": "bad",
    # terrible - 很糟
    "很糟": "terrible",
    "糟糕": "terrible",
    "糟糕透了": "terrible",
    "很差": "terrible",
    "崩溃": "terrible",
    "愤怒": "terrible",
    "生气": "terrible",
    "绝望": "terrible",
}


def normalize_mood(mood: Optional[str]) -> Optional[str]:
    """
    标准化心情值为英文枚举

    Args:
        mood: 用户输入的心情（可能是中文或英文）

    Returns:
        标准化的英文心情枚举值，如果无法识别则返回原值
    """
    if not mood:
        return mood

    # 已经是英文枚举值
    if mood in MOOD_ENUMS:
        return mood

    # 尝试中文映射
    mood_lower = mood.lower().strip()
    if mood_lower in MOOD_CN_TO_EN:
        return MOOD_CN_TO_EN[mood_lower]

    # 尝试模糊匹配（包含关键词）
    for cn_key, en_value in MOOD_CN_TO_EN.items():
        if cn_key in mood_lower:
            return en_value

    # 无法识别，返回原值（让参数验证处理）
    return mood


@register_skill
class CreateJournalSkill(BaseSkill):
    """创建日记技能"""

    @property
    def name(self) -> str:
        return "create_journal"

    @property
    def description(self) -> str:
        return "创建一篇新的日记"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.MEDIUM

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="content",
                type="string",
                description="日记内容",
                required=True
            ),
            SkillParameter(
                name="mood",
                type="string",
                description="心情（great=很棒, good=不错, neutral=一般, bad=不好, terrible=很糟）",
                required=False,
                enum=MOOD_ENUMS
            )
        ]

    @property
    def keywords(self) -> List[str]:
        return ["写日记", "创建日记", "记日记", "添加日记", "新建日记"]

    @property
    def examples(self) -> List[str]:
        return ["帮我写一篇日记，今天心情很好", "记录一下今天的事情"]

    async def execute(self, **kwargs) -> SkillResult:
        """执行创建日记"""
        content = kwargs.get("content", "")
        mood = normalize_mood(kwargs.get("mood"))

        # 业务逻辑验证
        if not content:
            return SkillResult(
                success=False,
                message="日记内容不能为空"
            )

        # 使用 db 工具插入
        result = await self.db.insert("journal", {
            "content": content,
            "mood": mood
        })

        if not result.success:
            return SkillResult(
                success=False,
                message=result.error or "创建日记失败"
            )

        # 使用 ctx 工具记录上下文
        if self.ctx:
            self.ctx.set_sync("last_journal_id", result.data.get("id"))

        return SkillResult(
            success=True,
            message="已为您创建日记",
            data=result.data,
            risk_level=self.risk_level
        )


@register_skill
class QueryJournalsSkill(BaseSkill):
    """查询日记技能"""

    @property
    def name(self) -> str:
        return "query_journals"

    @property
    def description(self) -> str:
        return "查询日记列表"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="date_expression",
                type="string",
                description="自然语言日期表达式（如：最近一周、昨天、本月）",
                required=False
            ),
            SkillParameter(
                name="start_date",
                type="string",
                description="开始日期（ISO格式）",
                required=False
            ),
            SkillParameter(
                name="end_date",
                type="string",
                description="结束日期（ISO格式）",
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
        return ["日记", "查看日记", "我的日记", "最近日记", "日记列表"]

    @property
    def examples(self) -> List[str]:
        return ["我最近有什么日记？", "查看我的日记", "最近一周的日记"]

    async def execute(self, **kwargs) -> SkillResult:
        """执行查询日记"""
        date_expression = kwargs.get("date_expression")
        limit = kwargs.get("limit", 10)
        filters = {}

        # 使用 datetime 工具解析日期表达式
        if date_expression:
            try:
                dt_result = await self.datetime.execute(
                    expression=date_expression,
                    format="range"
                )
                if dt_result.success and dt_result.data:
                    filters["start_date"] = dt_result.data.get("start_date")
                    filters["end_date"] = dt_result.data.get("end_date")
                else:
                    # 日期解析失败，记录日志但不中断流程
                    logger.warning(f"日期解析失败: {date_expression}, error: {dt_result.error}")
            except Exception as e:
                # 容错处理：日期解析异常不中断查询
                logger.warning(f"日期解析异常: {e}")

        # 使用明确的日期参数
        if kwargs.get("start_date"):
            filters["start_date"] = kwargs["start_date"]
        if kwargs.get("end_date"):
            filters["end_date"] = kwargs["end_date"]

        # 使用 db 工具查询
        try:
            result = await self.db.query("journal", filters, limit)
        except Exception as e:
            logger.error(f"查询日记数据库异常: {e}")
            return SkillResult(
                success=False,
                message=f"查询日记失败: {str(e)}"
            )

        if not result.success:
            logger.error(f"查询日记失败: {result.error}")
            return SkillResult(
                success=False,
                message=result.error or "查询失败"
            )

        journals = result.data or []

        if not journals:
            return SkillResult(
                success=True,
                message="暂无日记记录",
                data=[]
            )

        # 使用 ctx 工具记录上下文
        if self.ctx and journals:
            self.ctx.set_sync("last_journal_id", journals[0].get("id"))

        return SkillResult(
            success=True,
            message=f"找到 {len(journals)} 篇日记",
            data=journals,
            risk_level=self.risk_level
        )


@register_skill
class UpdateJournalSkill(BaseSkill):
    """更新日记技能"""

    @property
    def name(self) -> str:
        return "update_journal"

    @property
    def description(self) -> str:
        return "更新已有日记的内容"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.MEDIUM

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="journal_id",
                type="integer",
                description="日记ID（可省略，使用最近的日记）",
                required=False
            ),
            SkillParameter(
                name="content",
                type="string",
                description="新的日记内容",
                required=False
            ),
            SkillParameter(
                name="mood",
                type="string",
                description="心情（great=很棒, good=不错, neutral=一般, bad=不好, terrible=很糟）",
                required=False,
                enum=MOOD_ENUMS
            )
        ]

    @property
    def keywords(self) -> List[str]:
        return ["修改日记", "更新日记", "编辑日记"]

    @property
    def examples(self) -> List[str]:
        return ["修改刚才那篇日记", "把日记内容改成..."]

    async def execute(self, **kwargs) -> SkillResult:
        """执行更新日记"""
        content = kwargs.get("content")
        mood = normalize_mood(kwargs.get("mood"))

        # 使用 get_context_entity_id 获取日记ID
        journal_id = self.get_context_entity_id(
            "last_journal_id", kwargs.get("journal_id")
        )

        if not journal_id:
            return SkillResult(
                success=False,
                message="请指定要修改的日记"
            )

        # 构建更新数据
        update_data = {}
        if content:
            update_data["content"] = content
        if mood:
            update_data["mood"] = mood

        if not update_data:
            return SkillResult(
                success=False,
                message="没有要更新的内容"
            )

        # 使用 db 工具更新
        result = await self.db.update("journal", journal_id, update_data)

        if not result.success:
            return SkillResult(
                success=False,
                message=result.error or "更新失败"
            )

        return SkillResult(
            success=True,
            message="日记已更新",
            data=result.data,
            risk_level=self.risk_level
        )


@register_skill
class DeleteJournalSkill(BaseSkill):
    """删除日记技能"""

    @property
    def name(self) -> str:
        return "delete_journal"

    @property
    def description(self) -> str:
        return "删除一篇日记（需要确认）"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.HIGH

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="journal_id",
                type="integer",
                description="日记ID（可省略，使用最近的日记）",
                required=False
            )
        ]

    @property
    def keywords(self) -> List[str]:
        return ["删除日记", "删掉日记", "移除日记"]

    @property
    def examples(self) -> List[str]:
        return ["删掉刚才那篇日记", "删除最近的日记"]

    def check_confirmation_required(self, **kwargs) -> bool:
        """删除操作始终需要确认"""
        return True

    async def execute(self, **kwargs) -> SkillResult:
        """执行删除日记"""
        # 使用 get_context_entity_id 获取日记ID
        journal_id = self.get_context_entity_id(
            "last_journal_id", kwargs.get("journal_id")
        )

        if not journal_id:
            return SkillResult(
                success=False,
                message="请指定要删除的日记"
            )

        # 使用 db 工具删除
        result = await self.db.delete("journal", journal_id)

        if not result.success:
            return SkillResult(
                success=False,
                message=result.error or "删除失败"
            )

        return SkillResult(
            success=True,
            message=f"已删除日记: {result.data.get('deleted', {}).get('content_preview', '')}",
            data=result.data,
            risk_level=self.risk_level
        )