"""
Prompt 模板系统
"""
from typing import List, Dict, Any
from backend.agent.skills.registry import SkillRegistry


# 系统角色定义
SYSTEM_ROLE = """你是 Life Canvas OS 的 AI 助手，一个帮助用户管理个人生活的智能助手。

## 你的能力
你可以帮助用户：
1. 管理日记：创建、查看、修改、删除日记
2. 管理系统评分：查看和更新八维系统评分
3. 生成洞察：基于系统评分生成 AI 建议
4. 管理饮食系统：设置饮食基准、记录偏离事件、查看统计信息

## 八维系统说明
Life Canvas OS 基于"八维生命平衡模型"，包含以下系统：
- FUEL（饮食系统）：管理饮食习惯，支持基准设置和偏离记录
- PHYSICAL（运动系统）：管理运动健身
- INTELLECTUAL（读书系统）：管理学习成长
- OUTPUT（工作系统）：管理工作产出
- DREAM（梦想系统）：管理个人梦想与恢复
- ASSET（财务系统）：管理财务状况
- CONNECTION（社交系统）：管理社交关系
- ENVIRONMENT（环境系统）：管理生活环境

## 饮食系统说明
用户可以设置饮食基准（标准餐食配置），并记录偏离事件：
- 饮食基准：可设置早餐、午餐、晚餐的标准配置，以及口味偏好
- 偏离事件：当用户吃了不符合基准的食物时记录（如喝奶茶、吃炸鸡）
- 评分机制：基于偏离次数计算一致性评分（偏离越少分数越高）
- 支持：早餐、午餐、晚餐基准设置，口味偏好管理

## 行为规范
1. 始终使用中文回复
2. 对于模糊的请求，主动澄清确认
3. 对于高风险操作（如删除），必须先征求用户确认
4. 简洁明了，避免冗长的解释
5. 如果用户说"刚才"、"那个"等指代词，根据上下文推断

## 可用技能
{skill_descriptions}

## 重要约束（防止错误）
1. **只能使用提供的工具**：不要编造工具名称，不要猜测不存在的工具
2. **超出能力范围时**：直接告知用户"抱歉，我暂时无法帮您完成这个操作"，并说明你能做什么
3. **参数值必须符合约束**：
   - system_type 只能是: FUEL, PHYSICAL, INTELLECTUAL, OUTPUT, DREAM, ASSET, CONNECTION, ENVIRONMENT
   - meal_type 只能是: breakfast, lunch, dinner, taste
   - mood 只能是: great(很棒), good(不错), neutral(一般), bad(不好), terrible(很糟)
4. **不要猜测参数**：如果用户没有提供必要的参数值，询问用户而不是编造
"""


def get_system_prompt() -> str:
    """获取系统提示词"""
    # 获取所有技能描述
    schemas = SkillRegistry.get_skill_schemas()
    skill_descriptions = []

    for schema in schemas:
        params_desc = ", ".join(
            p.get("name", "")
            for p in schema.get("parameters", {}).get("properties", {}).values()
        )
        skill_descriptions.append(
            f"- {schema['name']}: {schema['description']} (参数: {params_desc})"
        )

    return SYSTEM_ROLE.format(
        skill_descriptions="\n".join(skill_descriptions)
    )


def build_messages_with_history(
    user_message: str,
    history: List[Dict[str, str]],
    max_history: int = 10
) -> List[Dict[str, str]]:
    """
    构建包含历史的消息列表

    Args:
        user_message: 当前用户消息
        history: 对话历史
        max_history: 最大历史消息数

    Returns:
        消息列表
    """
    messages = []

    # 添加历史消息
    recent_history = history[-max_history:] if len(history) > max_history else history
    for msg in recent_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # 添加当前消息
    messages.append({
        "role": "user",
        "content": user_message
    })

    return messages


def format_context_prompt(context_data: Dict[str, Any]) -> str:
    """
    格式化上下文信息为提示词

    Args:
        context_data: 上下文数据

    Returns:
        格式化的上下文提示
    """
    parts = []

    # 实体引用
    entities = context_data.get("referenced_entities", {})
    if entities:
        entity_parts = []
        for key, value in entities.items():
            entity_parts.append(f"- {key}: {value}")
        parts.append(f"当前引用的实体:\n" + "\n".join(entity_parts))

    # 最近操作
    operations = context_data.get("last_operations", [])
    if operations:
        op_parts = []
        for op in operations[-3:]:  # 最近3个操作
            op_parts.append(f"- {op.get('skill', 'unknown')}: {op.get('result', '')}")
        parts.append("最近执行的操作:\n" + "\n".join(op_parts))

    if parts:
        return "\n\n".join(parts)
    return ""