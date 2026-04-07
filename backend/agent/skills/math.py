from typing import Any, Dict, List
from backend.agent.skills.base import BaseSkill, RiskLevel, SkillResult, SkillParameter
from backend.agent.skills.registry import register_skill
from backend.agent.tools.math_tool import calculate_tdee

@register_skill
class CalculateTDEESkill(BaseSkill):
    """计算 TDEE 的数学工具技能"""

    @property
    def name(self) -> str:
        return "calculate_tdee"

    @property
    def description(self) -> str:
        return "使用数学公式精确计算 TDEE (总每日能量消耗)"

    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW

    @property
    def parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="gender", type="string", description="性别 (male/female)", required=True, enum=["male", "female"]
            ),
            SkillParameter(
                name="weight", type="number", description="体重 (kg)", required=True
            ),
            SkillParameter(
                name="height", type="number", description="身高 (cm)", required=True
            ),
            SkillParameter(
                name="age", type="integer", description="年龄 (岁)", required=True
            ),
            SkillParameter(
                name="activity", type="number", description="活动系数 (如 1.2 对应久坐, 1.55 对应中度活动)", required=True
            )
        ]

    @property
    def keywords(self) -> List[str]:
        return ["TDEE", "基础代谢", "能量消耗"]

    @property
    def examples(self) -> List[str]:
        return ["计算我的 TDEE", "算一下我每天消耗多少热量"]

    async def execute(self, **kwargs) -> SkillResult:
        try:
            # Attempt to fetch missing metrics from SystemLog (Temporal Logic)
            if self.db_session:
                from backend.models.dimension import SystemLog, System, SystemType
                # Look for the most recent 'weight' and 'height' in logs
                weight = kwargs.get("weight")
                height = kwargs.get("height")
                
                if not weight or not height:
                    logs = self.db_session.query(SystemLog).join(System).filter(
                        System.type.in_([SystemType.FUEL, SystemType.PHYSICAL]),
                        SystemLog.label.in_(["weight", "height"])
                    ).order_by(SystemLog.created_at.desc()).limit(10).all()
                    
                    for log in logs:
                        if not weight and log.label == "weight":
                            weight = float(log.value)
                        if not height and log.label == "height":
                            height = float(log.value)
                    
                    if weight: kwargs["weight"] = weight
                    if height: kwargs["height"] = height

            tdee = calculate_tdee(kwargs)
            return SkillResult(
                success=True,
                message=f"经由数学工具计算得出，您的精确 TDEE 为: {tdee:.1f} kcal (体重: {kwargs.get('weight')}kg, 身高: {kwargs.get('height')}cm)",
                data={"tdee": tdee}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                message=f"计算出错: {str(e)}"
            )
