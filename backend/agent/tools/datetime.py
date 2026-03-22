"""
日期时间工具
解析自然语言日期时间表达
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import re

from backend.agent.tools.base import BaseTool, ToolResult, ToolParameter
from backend.agent.utils.logger import get_logger

logger = get_logger("datetime")


class DateTimeTool(BaseTool):
    """日期时间解析工具"""

    # 中文日期表达式映射
    RELATIVE_PATTERNS = {
        r"今天": 0,
        r"今日": 0,
        r"昨天": -1,
        r"昨日": -1,
        r"前天": -2,
        r"明天": 1,
        r"明日": 1,
        r"后天": 2,
    }

    WEEKDAY_PATTERNS = {
        r"本周一": "this_monday",
        r"本周二": "this_tuesday",
        r"本周三": "this_wednesday",
        r"本周四": "this_thursday",
        r"本周五": "this_friday",
        r"本周六": "this_saturday",
        r"本周日": "this_sunday",
        r"上周一": "last_monday",
        r"上周二": "last_tuesday",
        r"上周三": "last_wednesday",
        r"上周四": "last_thursday",
        r"上周五": "last_friday",
        r"上周六": "last_saturday",
        r"上周日": "last_sunday",
    }

    TIME_RANGE_PATTERNS = {
        r"最近(\d+)天": "recent_days",
        r"最近一周": "recent_week",
        r"最近一月": "recent_month",
        r"本周": "this_week",
        r"上周": "last_week",
        r"本月": "this_month",
        r"上月": "last_month",
    }

    @property
    def name(self) -> str:
        return "datetime_parse"

    @property
    def description(self) -> str:
        return "解析自然语言日期时间表达式，返回标准日期格式"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="expression",
                type="string",
                description="自然语言日期表达式（如：今天、昨天、最近一周、本周一等）",
                required=True
            ),
            ToolParameter(
                name="format",
                type="string",
                description="输出格式（date/datetime/range）",
                required=False
            )
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """执行日期解析"""
        expression = kwargs.get("expression", "").strip()
        output_format = kwargs.get("format", "date")

        try:
            result = self._parse_expression(expression, output_format)
            return ToolResult(success=True, data=result)
        except Exception as e:
            logger.error(f"Date parse failed: {e}")
            return ToolResult(success=False, error=str(e))

    def _parse_expression(self, expression: str, output_format: str) -> Dict[str, Any]:
        """解析日期表达式"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # 检查相对日期
        for pattern, delta in self.RELATIVE_PATTERNS.items():
            if re.search(pattern, expression):
                target_date = today + timedelta(days=delta)
                return self._format_result(target_date, output_format)

        # 检查星期几
        for pattern, value in self.WEEKDAY_PATTERNS.items():
            if re.search(pattern, expression):
                target_date = self._get_weekday_date(value, today)
                return self._format_result(target_date, output_format)

        # 检查时间范围
        for pattern, range_type in self.TIME_RANGE_PATTERNS.items():
            match = re.search(pattern, expression)
            if match:
                if range_type == "recent_days":
                    days = int(match.group(1))
                    start_date = today - timedelta(days=days - 1)
                    return {
                        "start_date": start_date.isoformat(),
                        "end_date": today.isoformat(),
                        "type": "range"
                    }
                elif range_type == "recent_week":
                    start_date = today - timedelta(days=6)
                    return {
                        "start_date": start_date.isoformat(),
                        "end_date": today.isoformat(),
                        "type": "range"
                    }
                elif range_type == "recent_month":
                    start_date = today - timedelta(days=29)
                    return {
                        "start_date": start_date.isoformat(),
                        "end_date": today.isoformat(),
                        "type": "range"
                    }
                elif range_type == "this_week":
                    start_date = today - timedelta(days=today.weekday())
                    end_date = start_date + timedelta(days=6)
                    return {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "type": "range"
                    }
                elif range_type == "last_week":
                    start_date = today - timedelta(days=today.weekday() + 7)
                    end_date = start_date + timedelta(days=6)
                    return {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "type": "range"
                    }
                elif range_type == "this_month":
                    start_date = today.replace(day=1)
                    return {
                        "start_date": start_date.isoformat(),
                        "end_date": today.isoformat(),
                        "type": "range"
                    }
                elif range_type == "last_month":
                    first_of_this_month = today.replace(day=1)
                    end_date = first_of_this_month - timedelta(days=1)
                    start_date = end_date.replace(day=1)
                    return {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "type": "range"
                    }

        # 尝试解析标准日期格式
        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m月%d日", "%Y年%m月%d日"]:
            try:
                parsed = datetime.strptime(expression, fmt)
                if parsed.year == 1900:
                    # 没有年份的日期，使用当前年
                    parsed = parsed.replace(year=today.year)
                return self._format_result(parsed, output_format)
            except ValueError:
                continue

        # 无法解析，返回今天
        return self._format_result(today, output_format)

    def _get_weekday_date(self, weekday_key: str, today: datetime) -> datetime:
        """获取指定星期的日期"""
        weekday_map = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }

        if weekday_key.startswith("this_"):
            day_name = weekday_key.replace("this_", "")
            target_weekday = weekday_map[day_name]
            days_ahead = target_weekday - today.weekday()
            if days_ahead < 0:
                days_ahead += 7
            return today + timedelta(days=days_ahead)
        elif weekday_key.startswith("last_"):
            day_name = weekday_key.replace("last_", "")
            target_weekday = weekday_map[day_name]
            days_behind = today.weekday() - target_weekday
            if days_behind <= 0:
                days_behind += 7
            return today - timedelta(days=days_behind)

        return today

    def _format_result(self, date: datetime, output_format: str) -> Dict[str, Any]:
        """格式化结果"""
        if output_format == "datetime":
            return {
                "date": date.isoformat(),
                "type": "datetime"
            }
        elif output_format == "range":
            return {
                "start_date": date.isoformat(),
                "end_date": date.isoformat(),
                "type": "range"
            }
        else:
            return {
                "date": date.date().isoformat(),
                "type": "date"
            }