"""
工具函数 - 安全检测（Gatekeeper）

第一道防线：本地规则过滤，检测明显的恶意模式。
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SecurityCheckResult:
    """安全检查结果"""

    is_safe: bool
    reason: Optional[str] = None
    action: str = "allow"  # allow, block, warn


class Gatekeeper:
    """
    守门员 - 恶意模式检测

    检测 Prompt 注入、权限提升、数据泄露等攻击模式。
    """

    def __init__(self):
        # 恶意模式正则
        self.malicious_patterns = [
            # Prompt 注入模式
            (r"忽略.{0,10}指令", "prompt_injection"),
            (r"ignore.{0,10}instruction", "prompt_injection"),
            (r"forget.{0,10}previous", "prompt_injection"),
            (r"disregard.{0,10}above", "prompt_injection"),
            (r"绕过.{0,10}限制", "prompt_injection"),
            (r"bypass.{0,10}restriction", "prompt_injection"),
            # 权限提升模式
            (r"给我.{0,10}管理员", "privilege_escalation"),
            (r"grant.{0,10}admin", "privilege_escalation"),
            (r"sudo", "privilege_escalation"),
            (r"提升.{0,10}权限", "privilege_escalation"),
            # 数据泄露模式
            (r"显示.{0,10}系统提示", "data_leak"),
            (r"show.{0,10}system prompt", "data_leak"),
            (r"reveal.{0,10}instruction", "data_leak"),
            (r"你的.{0,10}提示词", "data_leak"),
            # 命令注入模式
            (r";\s*rm\s+", "command_injection"),
            (r"\|\s*bash", "command_injection"),
            (r"`.*`", "command_injection"),
            # SQL 注入模式
            (r"'\s*OR\s+'1'\s*=\s*'1", "sql_injection"),
            (r";\s*DROP\s+TABLE", "sql_injection"),
            (r"--\s*$", "sql_injection"),
        ]

        # 编译正则
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), attack_type)
            for pattern, attack_type in self.malicious_patterns
        ]

    def check(self, user_input: str) -> SecurityCheckResult:
        """
        检查用户输入

        Args:
            user_input: 用户输入文本

        Returns:
            SecurityCheckResult: 检查结果
        """
        # 检查空输入
        if not user_input or not user_input.strip():
            return SecurityCheckResult(
                is_safe=False,
                reason="输入为空",
                action="block",
            )

        # 检查长度限制（防止超长输入攻击）
        if len(user_input) > 2000:
            return SecurityCheckResult(
                is_safe=False,
                reason="输入过长，限制 2000 字符",
                action="block",
            )

        # 检查恶意模式
        for pattern, attack_type in self.compiled_patterns:
            if pattern.search(user_input):
                return SecurityCheckResult(
                    is_safe=False,
                    reason=f"检测到潜在{attack_type}攻击模式",
                    action="block",
                )

        # 检查通过
        return SecurityCheckResult(is_safe=True, action="allow")

    def add_pattern(self, pattern: str, attack_type: str) -> None:
        """
        添加新的检测模式

        Args:
            pattern: 正则表达式
            attack_type: 攻击类型
        """
        compiled = re.compile(pattern, re.IGNORECASE)
        self.compiled_patterns.append((compiled, attack_type))


# 单例实例
_gatekeeper_instance: Optional[Gatekeeper] = None


def get_gatekeeper() -> Gatekeeper:
    """获取 Gatekeeper 单例"""
    global _gatekeeper_instance
    if _gatekeeper_instance is None:
        _gatekeeper_instance = Gatekeeper()
    return _gatekeeper_instance
