"""
Prompt 模板

定义 Agent 的系统提示词和对话示例。
"""

from typing import List, Dict, Any, Optional


class PromptTemplate:
    """Prompt 模板类"""

    # 系统提示词
    SYSTEM_PROMPT = """你是 Life Canvas OS 的 AI 助手，一款基于八维生命平衡模型的桌面应用。

## 可用能力

你可以通过调用以下技能来帮助用户：
{tools_description}

## 领域知识

八维系统包括：
- FUEL (饮食系统) - 管理饮食健康
- PHYSICAL (运动系统) - 管理运动健身
- INTELLECTUAL (学习系统) - 管理读书学习
- OUTPUT (工作系统) - 管理工作产出
- DREAM (梦想系统) - 管理梦想和恢复
- ASSET (财务系统) - 管理财务收入
- CONNECTION (社交系统) - 管理社交关系
- ENVIRONMENT (环境系统) - 管理生活环境

## 行为规范

1. 始终用中文回复
2. 语气友好、专业、简洁
3. 模糊输入时主动澄清
4. 高风险操作需要用户确认
5. 不要编造信息，不知道就说不知道

## 回复风格

- 创建操作：确认已创建的内容，并询问是否需要补充
- 查询操作：直接返回结果，必要时提供建议
- 更新操作：确认更新前后的变化
- 删除操作：删除前必须确认，删除后告知结果

## 对话示例

User: 帮我写一篇日记
Assistant: 好的，请告诉我日记的内容？

User: 今天心情很好，完成了项目里程碑
Assistant: 已为您创建日记《今天心情很好》！心情标记为「开心」，需要添加标签吗？

User: 我的运动评分是多少
Assistant: 您的运动系统 (PHYSICAL) 当前评分为 78 分，比上周提升了 5 分，继续保持！

User: 删掉刚才那篇日记
Assistant: 确认删除日记《今天心情很好》？此操作不可撤销。
"""

    # 确认提示词模板
    CONFIRMATION_PROMPT = """请确认以下操作：

**操作类型**: {skill_name}
**操作内容**: {operation_description}

**风险等级**: {risk_level}

请回复"确认"继续，或回复"取消"终止操作。"""

    # 错误提示词模板
    ERROR_PROMPT = {
        "parameter_missing": "请告诉我{param_name}是什么？",
        "parameter_invalid": "{param_name}需要在{constraint}范围内",
        "operation_failed": "操作失败：{error}，请稍后重试",
        "llm_unavailable": "AI 服务暂时不可用，已切换到简化模式。",
    }

    @classmethod
    def build_system_prompt(
        cls,
        tools_description: str = "",
        custom_instructions: Optional[str] = None,
    ) -> str:
        """
        构建系统提示词

        Args:
            tools_description: 工具描述
            custom_instructions: 自定义指令

        Returns:
            str: 完整的系统提示词
        """
        prompt = cls.SYSTEM_PROMPT

        if tools_description:
            prompt = prompt.replace("{tools_description}", tools_description)
        else:
            prompt = prompt.replace("{tools_description}", "（技能将在运行时注入）")

        if custom_instructions:
            prompt += f"\n\n## 自定义指令\n\n{custom_instructions}"

        return prompt

    @classmethod
    def build_confirmation_prompt(
        cls,
        skill_name: str,
        operation_description: str,
        risk_level: str,
    ) -> str:
        """
        构建确认提示词

        Args:
            skill_name: 技能名称
            operation_description: 操作描述
            risk_level: 风险等级

        Returns:
            str: 确认提示词
        """
        return cls.CONFIRMATION_PROMPT.format(
            skill_name=skill_name,
            operation_description=operation_description,
            risk_level=risk_level,
        )

    @classmethod
    def build_error_prompt(cls, error_type: str, **kwargs) -> str:
        """
        构建错误提示词

        Args:
            error_type: 错误类型
            **kwargs: 格式化参数

        Returns:
            str: 错误提示词
        """
        template = cls.ERROR_PROMPT.get(error_type, "发生错误：{error}")
        return template.format(**kwargs)

    @classmethod
    def build_compression_prompt(cls, messages: List[Dict[str, str]]) -> str:
        """
        构建记忆压缩提示词

        Args:
            messages: 对话消息列表

        Returns:
            str: 压缩提示词
        """
        return f"""请将以下对话历史压缩为简洁摘要，保留关键信息：
- 用户的主要意图
- 已执行的关键操作
- 重要实体引用（如日记 ID）

对话历史：
{cls._format_messages(messages)}

摘要："""

    @staticmethod
    def _format_messages(messages: List[Dict[str, str]]) -> str:
        """格式化消息列表"""
        formatted = []
        for msg in messages[-20:]:  # 只保留最近 20 条
            role = "用户" if msg["role"] == "user" else "助手"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
