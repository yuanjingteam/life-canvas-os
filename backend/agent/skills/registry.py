"""
Skill 注册中心

管理所有可用 Skill 的注册、查找和分类。
"""

from typing import Dict, Optional, List
from .base import BaseSkill, RiskLevel


class SkillRegistry:
    """Skill 注册中心（单例模式）"""

    _instance: Optional["SkillRegistry"] = None
    _skills: Dict[str, BaseSkill] = {}
    _skills_by_category: Dict[str, List[str]] = {}

    def __new__(cls) -> "SkillRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, skill: BaseSkill, category: str = "default") -> None:
        """
        注册 Skill

        Args:
            skill: Skill 实例
            category: 分类名称
        """
        self._skills[skill.name] = skill

        if category not in self._skills_by_category:
            self._skills_by_category[category] = []
        if skill.name not in self._skills_by_category[category]:
            self._skills_by_category[category].append(skill.name)

    def unregister(self, name: str) -> bool:
        """
        注销 Skill

        Args:
            name: Skill 名称

        Returns:
            bool: 是否成功注销
        """
        if name in self._skills:
            # 从分类中移除
            for category, names in self._skills_by_category.items():
                if name in names:
                    names.remove(name)
            # 从主字典移除
            del self._skills[name]
            return True
        return False

    def get(self, name: str) -> Optional[BaseSkill]:
        """
        获取 Skill

        Args:
            name: Skill 名称

        Returns:
            Optional[BaseSkill]: Skill 实例，不存在返回 None
        """
        return self._skills.get(name)

    def get_all(self) -> Dict[str, BaseSkill]:
        """获取所有 Skill"""
        return self._skills.copy()

    def get_names(self) -> List[str]:
        """获取所有 Skill 名称"""
        return list(self._skills.keys())

    def get_by_category(self, category: str) -> List[BaseSkill]:
        """
        按分类获取 Skill

        Args:
            category: 分类名称

        Returns:
            List[BaseSkill]: Skill 列表
        """
        names = self._skills_by_category.get(category, [])
        return [self._skills[name] for name in names if name in self._skills]

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        return list(self._skills_by_category.keys())

    def get_by_risk_level(self, risk_level: RiskLevel) -> List[BaseSkill]:
        """
        按风险等级获取 Skill

        Args:
            risk_level: 风险等级

        Returns:
            List[BaseSkill]: Skill 列表
        """
        return [
            skill for skill in self._skills.values()
            if skill.risk_level == risk_level
        ]

    def search_by_trigger(self, text: str) -> List[BaseSkill]:
        """
        根据文本匹配触发词搜索 Skill（用于规则匹配降级）

        Args:
            text: 用户输入文本

        Returns:
            List[BaseSkill]: 匹配的 Skill 列表
        """
        import re
        matched = []
        for skill in self._skills.values():
            for trigger in skill.trigger_words:
                if re.search(trigger, text, re.IGNORECASE):
                    if skill not in matched:
                        matched.append(skill)
                    break
        return matched

    def clear(self) -> None:
        """清空所有 Skill"""
        self._skills.clear()
        self._skills_by_category.clear()

    def __contains__(self, name: str) -> bool:
        return name in self._skills

    def __len__(self) -> int:
        return len(self._skills)
