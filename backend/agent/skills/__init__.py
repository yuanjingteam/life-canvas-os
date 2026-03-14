"""
Skill 技能模块

Skill 是面向用户的、领域特定的能力单元，可组合多个 Tool 完成复杂任务。
"""

from .base import BaseSkill, SkillResult, RiskLevel
from .registry import SkillRegistry

__all__ = [
    "BaseSkill",
    "SkillResult",
    "RiskLevel",
    "SkillRegistry",
]
