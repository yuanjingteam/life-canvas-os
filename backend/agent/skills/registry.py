"""
Skill 注册中心
管理和路由所有技能
"""
from typing import Dict, List, Optional, Type, Any
from sqlalchemy.orm import Session

from backend.agent.skills.base import BaseSkill, RiskLevel, SkillResult
from backend.agent.models.context import SessionContext
from backend.agent.utils.logger import get_logger

logger = get_logger("registry")


class SkillRegistry:
    """技能注册中心"""

    _skills: Dict[str, Type[BaseSkill]] = {}

    @classmethod
    def register(cls, skill_class: Type[BaseSkill]) -> Type[BaseSkill]:
        """
        注册技能

        Args:
            skill_class: 技能类

        Returns:
            技能类（支持装饰器用法）
        """
        instance = skill_class()
        cls._skills[instance.name] = skill_class
        logger.info(f"Registered skill: {instance.name}")
        return skill_class

    @classmethod
    def get_skill(
        cls,
        name: str,
        db_session: Session = None,
        context: SessionContext = None,
        context_manager = None
    ) -> Optional[BaseSkill]:
        """
        获取技能实例

        Args:
            name: 技能名称
            db_session: 数据库会话
            context: 会话上下文
            context_manager: 上下文管理器

        Returns:
            技能实例
        """
        skill_class = cls._skills.get(name)
        if skill_class:
            return skill_class(
                db_session=db_session,
                context=context,
                context_manager=context_manager
            )
        return None

    @classmethod
    def list_skills(cls) -> List[str]:
        """获取所有已注册技能名称"""
        return list(cls._skills.keys())

    @classmethod
    def get_skill_schemas(cls) -> List[Dict[str, Any]]:
        """获取所有技能的 Schema"""
        schemas = []
        for name, skill_class in cls._skills.items():
            instance = skill_class()
            schemas.append(instance.get_schema())
        return schemas

    @classmethod
    def match_skill(cls, query: str) -> Optional[str]:
        """
        根据查询匹配技能

        Args:
            query: 用户查询

        Returns:
            匹配的技能名称
        """
        query_lower = query.lower()

        for name, skill_class in cls._skills.items():
            instance = skill_class()
            for keyword in instance.keywords:
                if keyword in query_lower:
                    return name

        return None

    @classmethod
    async def execute_skill(
        cls,
        name: str,
        params: Dict[str, Any],
        db_session: Session,
        context: SessionContext = None,
        context_manager = None
    ) -> SkillResult:
        """
        执行技能

        Args:
            name: 技能名称
            params: 参数
            db_session: 数据库会话
            context: 会话上下文
            context_manager: 上下文管理器

        Returns:
            执行结果
        """
        skill = cls.get_skill(name, db_session, context, context_manager)
        if not skill:
            return SkillResult(
                success=False,
                message=f"未找到技能: {name}"
            )

        # 验证参数
        error = skill.validate_parameters(params)
        if error:
            return SkillResult(
                success=False,
                message=error
            )

        try:
            return await skill.execute(**params)
        except Exception as e:
            logger.error(f"Skill execution failed: {name} - {e}")
            return SkillResult(
                success=False,
                message=f"执行失败: {str(e)}"
            )


def register_skill(skill_class: Type[BaseSkill]) -> Type[BaseSkill]:
    """技能注册装饰器"""
    return SkillRegistry.register(skill_class)