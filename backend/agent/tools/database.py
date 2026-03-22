"""
数据库工具
提供通用的数据 CRUD 操作能力

设计原则：
- 原子操作：每个方法只做一件事
- 可复用：不包含业务逻辑，供 Skills 调用
- 通用性：支持多种实体类型
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.agent.tools.base import BaseTool, ToolResult, ToolParameter
from backend.agent.utils.logger import get_logger

logger = get_logger("database")


class DatabaseTool(BaseTool):
    """
    通用数据库 CRUD 工具

    提供统一的数据库操作接口，供 Skills 调用。
    不包含业务逻辑验证，只做数据操作。
    """

    def __init__(self, db_session: Session):
        super().__init__(db_session)

    @property
    def name(self) -> str:
        return "database"

    @property
    def description(self) -> str:
        return "通用数据库操作工具，支持查询、插入、更新、删除"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="操作类型：query/insert/update/delete",
                required=True,
                enum=["query", "insert", "update", "delete"]
            ),
            ToolParameter(
                name="entity_type",
                type="string",
                description="实体类型：journal/system/insight/user/deviation",
                required=True
            )
        ]

    async def execute(self, **kwargs) -> ToolResult:
        """
        执行数据库操作

        这是一个通用入口，实际使用时建议直接调用具体方法。
        """
        operation = kwargs.get("operation")
        entity_type = kwargs.get("entity_type")

        if operation == "query":
            return await self.query(
                entity_type=entity_type,
                filters=kwargs.get("filters"),
                limit=kwargs.get("limit", 10)
            )
        elif operation == "insert":
            return await self.insert(
                entity_type=entity_type,
                data=kwargs.get("data", {})
            )
        elif operation == "update":
            return await self.update(
                entity_type=entity_type,
                entity_id=kwargs.get("entity_id"),
                data=kwargs.get("data", {})
            )
        elif operation == "delete":
            return await self.delete(
                entity_type=entity_type,
                entity_id=kwargs.get("entity_id")
            )
        else:
            return ToolResult(
                success=False,
                error=f"不支持的操作类型: {operation}"
            )

    # ==================== 查询操作 ====================

    async def query(
        self,
        entity_type: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> ToolResult:
        """
        查询实体

        Args:
            entity_type: 实体类型 (journal/system/insight/user/deviation)
            filters: 过滤条件
            limit: 返回数量限制

        Returns:
            查询结果列表
        """
        try:
            if entity_type == "journal":
                return await self._query_journals(filters or {}, limit)
            elif entity_type == "system":
                return await self._query_systems(filters or {})
            elif entity_type == "insight":
                return await self._query_insights(filters or {}, limit)
            elif entity_type == "user":
                return await self._query_user()
            elif entity_type == "deviation":
                return await self._query_deviations(filters or {}, limit)
            else:
                return ToolResult(
                    success=False,
                    error=f"不支持的实体类型: {entity_type}"
                )
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return ToolResult(success=False, error=str(e))

    async def _query_journals(
        self, filters: Dict[str, Any], limit: int
    ) -> ToolResult:
        """查询日记"""
        from backend.models.diary import Diary
        from backend.models.user import User

        user = self.db_session.query(User).first()
        if not user:
            return ToolResult(success=False, error="用户不存在")

        query = self.db_session.query(Diary).filter(
            Diary.user_id == user.id
        )

        # 应用过滤条件（添加日期解析的容错处理）
        try:
            if "start_date" in filters:
                start_date = datetime.fromisoformat(filters["start_date"])
                query = query.filter(Diary.created_at >= start_date)
        except (ValueError, TypeError) as e:
            logger.warning(f"日期解析失败 (start_date): {e}")
        try:
            if "end_date" in filters:
                end_date = datetime.fromisoformat(filters["end_date"])
                query = query.filter(Diary.created_at <= end_date)
        except (ValueError, TypeError) as e:
            logger.warning(f"日期解析失败 (end_date): {e}")
        if "mood" in filters:
            query = query.filter(Diary.mood == filters["mood"])

        query = query.order_by(Diary.created_at.desc())
        journals = query.limit(limit).all()

        data = [
            {
                "id": j.id,
                "content": j.content,
                "mood": j.mood,
                "created_at": j.created_at.isoformat() if j.created_at else None
            }
            for j in journals
        ]

        return ToolResult(success=True, data=data)

    async def _query_systems(self, filters: Dict[str, Any]) -> ToolResult:
        """查询系统评分"""
        from backend.models.dimension import System, SYSTEM_TYPES, SystemType
        from backend.models.user import User

        user = self.db_session.query(User).first()
        if not user:
            return ToolResult(success=False, error="用户不存在")

        query = self.db_session.query(System).filter(System.user_id == user.id)

        if "system_type" in filters:
            system_type = filters["system_type"].upper()
            if system_type in SystemType.list():
                query = query.filter(System.type == system_type)

        systems = query.all()

        data = [
            {
                "type": s.type.value if hasattr(s.type, 'value') else s.type,
                "score": s.score,
                "details": s.details,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None
            }
            for s in systems
        ]

        return ToolResult(success=True, data=data)

    async def _query_insights(
        self, filters: Dict[str, Any], limit: int
    ) -> ToolResult:
        """查询洞察"""
        from backend.models.insight import Insight
        from backend.models.user import User

        user = self.db_session.query(User).first()
        if not user:
            return ToolResult(success=False, error="用户不存在")

        query = self.db_session.query(Insight).filter(
            Insight.user_id == user.id
        ).order_by(Insight.generated_at.desc())

        insights = query.limit(limit).all()

        data = [
            {
                "id": i.id,
                "content": i.content,
                "generated_at": i.generated_at.isoformat() if i.generated_at else None
            }
            for i in insights
        ]

        return ToolResult(success=True, data=data)

    async def _query_user(self) -> ToolResult:
        """查询用户信息"""
        from backend.models.user import User

        user = self.db_session.query(User).first()
        if not user:
            return ToolResult(success=False, error="用户不存在")

        data = {
            "id": user.id,
            "display_name": user.display_name,
            "mbti": user.mbti,
            "values": user.values,
            "ai_config": {
                "provider": user.ai_config.get("provider") if user.ai_config else None,
                "model": user.ai_config.get("model") if user.ai_config else None
            } if user.ai_config else None
        }

        return ToolResult(success=True, data=data)

    async def _query_deviations(
        self, filters: Dict[str, Any], limit: int
    ) -> ToolResult:
        """查询饮食偏离记录"""
        from backend.models.dimension import MealDeviation
        from backend.models.user import User

        user = self.db_session.query(User).first()
        if not user:
            return ToolResult(success=False, error="用户不存在")

        query = self.db_session.query(MealDeviation).filter(
            MealDeviation.user_id == user.id
        )

        if "start_date" in filters:
            start_date = datetime.fromisoformat(filters["start_date"])
            query = query.filter(MealDeviation.occurred_at >= start_date)
        if "end_date" in filters:
            end_date = datetime.fromisoformat(filters["end_date"])
            query = query.filter(MealDeviation.occurred_at <= end_date)

        query = query.order_by(MealDeviation.occurred_at.desc())
        deviations = query.limit(limit).all()

        data = [
            {
                "id": d.id,
                "description": d.description,
                "occurred_at": d.occurred_at.isoformat() if d.occurred_at else None
            }
            for d in deviations
        ]

        return ToolResult(success=True, data=data)

    # ==================== 插入操作 ====================

    async def insert(
        self,
        entity_type: str,
        data: Dict[str, Any]
    ) -> ToolResult:
        """
        插入实体

        Args:
            entity_type: 实体类型
            data: 实体数据

        Returns:
            插入结果
        """
        try:
            if entity_type == "journal":
                return await self._insert_journal(data)
            elif entity_type == "deviation":
                return await self._insert_deviation(data)
            else:
                return ToolResult(
                    success=False,
                    error=f"不支持的插入类型: {entity_type}"
                )
        except Exception as e:
            logger.error(f"Database insert failed: {e}")
            return ToolResult(success=False, error=str(e))

    async def _insert_journal(self, data: Dict[str, Any]) -> ToolResult:
        """插入日记"""
        from backend.models.diary import Diary
        from backend.models.user import User

        user = self.db_session.query(User).first()
        if not user:
            return ToolResult(success=False, error="用户不存在")

        journal = Diary(
            user_id=user.id,
            title=data.get("title", "未命名"),
            content=data.get("content", ""),
            mood=data.get("mood")
        )

        self.db_session.add(journal)
        self.db_session.commit()
        self.db_session.refresh(journal)

        return ToolResult(
            success=True,
            data={
                "id": journal.id,
                "content": journal.content,
                "mood": journal.mood,
                "created_at": journal.created_at.isoformat() if journal.created_at else None
            }
        )

    async def _insert_deviation(self, data: Dict[str, Any]) -> ToolResult:
        """插入饮食偏离记录"""
        from backend.models.dimension import MealDeviation, System, SYSTEM_TYPES, SystemType
        from backend.models.user import User

        try:
            user = self.db_session.query(User).first()
            if not user:
                return ToolResult(success=False, error="用户不存在")

            # 数据完整性验证：确保必填字段存在
            # 这是数据层验证，不是业务逻辑验证
            description = data.get("description", "").strip()
            if not description:
                return ToolResult(
                    success=False,
                    error="偏离描述不能为空"
                )

            # 使用字符串值进行数据库查询和插入
            fuel_type = SystemType.FUEL.value

            # 查询用户的 fuel system，如果没有则创建一个
            system = self.db_session.query(System).filter(
                System.user_id == user.id,
                System.type == fuel_type
            ).first()

            if not system:
                system = System(
                    user_id=user.id,
                    type=fuel_type,
                    score=50  # 默认分数
                )
                self.db_session.add(system)
                self.db_session.commit()
                self.db_session.refresh(system)

            deviation = MealDeviation(
                system_id=system.id,
                description=description
            )

            self.db_session.add(deviation)
            self.db_session.commit()
            self.db_session.refresh(deviation)

            logger.info(f"成功创建饮食偏离记录: id={deviation.id}, description={description}")

            return ToolResult(
                success=True,
                data={
                    "id": deviation.id,
                    "description": deviation.description,
                    "occurred_at": deviation.occurred_at.isoformat() if deviation.occurred_at else None
                }
            )
        except Exception as e:
            logger.error(f"插入饮食偏离记录失败: {e}")
            self.db_session.rollback()
            return ToolResult(
                success=False,
                error=f"创建偏离记录失败: {str(e)}"
            )

    # ==================== 更新操作 ====================

    async def update(
        self,
        entity_type: str,
        entity_id: Optional[int],
        data: Dict[str, Any]
    ) -> ToolResult:
        """
        更新实体

        Args:
            entity_type: 实体类型
            entity_id: 实体ID（更新系统评分时可为 None）
            data: 更新数据

        Returns:
            更新结果
        """
        try:
            if entity_type == "journal":
                return await self._update_journal(entity_id, data)
            elif entity_type == "system":
                return await self._update_system(data)
            elif entity_type == "deviation":
                return await self._update_deviation(entity_id, data)
            else:
                return ToolResult(
                    success=False,
                    error=f"不支持的更新类型: {entity_type}"
                )
        except Exception as e:
            logger.error(f"Database update failed: {e}")
            return ToolResult(success=False, error=str(e))

    async def _update_journal(
        self, journal_id: int, data: Dict[str, Any]
    ) -> ToolResult:
        """更新日记"""
        from backend.models.diary import Diary

        journal = self.db_session.query(Diary).filter(
            Diary.id == journal_id
        ).first()

        if not journal:
            return ToolResult(success=False, error="日记不存在")

        if "content" in data:
            journal.content = data["content"]
        if "mood" in data:
            journal.mood = data["mood"]

        self.db_session.commit()
        self.db_session.refresh(journal)

        return ToolResult(
            success=True,
            data={
                "id": journal.id,
                "content": journal.content,
                "mood": journal.mood
            }
        )

    async def _update_system(self, data: Dict[str, Any]) -> ToolResult:
        """更新系统评分"""
        from backend.models.dimension import System, SYSTEM_TYPES, SystemType
        from backend.models.user import User

        user = self.db_session.query(User).first()
        if not user:
            return ToolResult(success=False, error="用户不存在")

        system_type = data.get("system_type")
        score = data.get("score")

        if not system_type or score is None:
            return ToolResult(
                success=False,
                error="缺少 system_type 或 score 参数"
            )

        system_type = system_type.upper()
        if system_type not in SystemType.list():
            return ToolResult(
                success=False,
                error=f"无效的系统类型: {system_type}"
            )

        system = self.db_session.query(System).filter(
            System.user_id == user.id,
            System.type == system_type
        ).first()

        if not system:
            system = System(
                user_id=user.id,
                type=system_type,
                score=score
            )
            self.db_session.add(system)
        else:
            system.score = score

        self.db_session.commit()
        self.db_session.refresh(system)

        return ToolResult(
            success=True,
            data={
                "type": system.type.value if hasattr(system.type, 'value') else system.type,
                "score": system.score
            }
        )

    async def _update_deviation(
        self, deviation_id: int, data: Dict[str, Any]
    ) -> ToolResult:
        """更新饮食偏离记录"""
        from backend.models.dimension import MealDeviation

        deviation = self.db_session.query(MealDeviation).filter(
            MealDeviation.id == deviation_id
        ).first()

        if not deviation:
            return ToolResult(success=False, error="偏离记录不存在")

        if "description" in data:
            deviation.description = data["description"]

        self.db_session.commit()
        self.db_session.refresh(deviation)

        return ToolResult(
            success=True,
            data={
                "id": deviation.id,
                "description": deviation.description
            }
        )

    # ==================== 删除操作 ====================

    async def delete(
        self,
        entity_type: str,
        entity_id: int
    ) -> ToolResult:
        """
        删除实体

        Args:
            entity_type: 实体类型
            entity_id: 实体ID

        Returns:
            删除结果
        """
        try:
            if entity_type == "journal":
                return await self._delete_journal(entity_id)
            elif entity_type == "deviation":
                return await self._delete_deviation(entity_id)
            else:
                return ToolResult(
                    success=False,
                    error=f"不支持的删除类型: {entity_type}"
                )
        except Exception as e:
            logger.error(f"Database delete failed: {e}")
            return ToolResult(success=False, error=str(e))

    async def _delete_journal(self, journal_id: int) -> ToolResult:
        """删除日记"""
        from backend.models.diary import Diary

        journal = self.db_session.query(Diary).filter(
            Diary.id == journal_id
        ).first()

        if not journal:
            return ToolResult(success=False, error="日记不存在")

        deleted_info = {
            "id": journal.id,
            "content_preview": journal.content[:100] + "..." if len(journal.content) > 100 else journal.content
        }

        self.db_session.delete(journal)
        self.db_session.commit()

        return ToolResult(
            success=True,
            data={"deleted": deleted_info}
        )

    async def _delete_deviation(self, deviation_id: int) -> ToolResult:
        """删除饮食偏离记录"""
        from backend.models.dimension import MealDeviation

        deviation = self.db_session.query(MealDeviation).filter(
            MealDeviation.id == deviation_id
        ).first()

        if not deviation:
            return ToolResult(success=False, error="偏离记录不存在")

        deleted_info = {
            "id": deviation.id,
            "description": deviation.description
        }

        self.db_session.delete(deviation)
        self.db_session.commit()

        return ToolResult(
            success=True,
            data={"deleted": deleted_info}
        )