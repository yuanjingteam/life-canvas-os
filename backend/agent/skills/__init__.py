"""
Skill 技能模块
包含所有可执行的技能
"""

from backend.agent.skills.base import BaseSkill
from backend.agent.skills.registry import SkillRegistry

# 导入所有技能以确保注册
from backend.agent.skills import journal
from backend.agent.skills import system
from backend.agent.skills import insight
from backend.agent.skills import diet
from backend.agent.skills import math
from backend.agent.skills import nutrition

__all__ = ["BaseSkill", "SkillRegistry"]