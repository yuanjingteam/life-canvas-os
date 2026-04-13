"""
基础服务模块

提供所有服务类的公共基类，包含通用的数据库操作和工具方法。
"""
from typing import Optional, TypeVar, Generic, List
from sqlalchemy.orm import Session, DeclarativeBase

from backend.models.user import User


# 定义泛型类型约束（使用 DeclarativeBase 作为基类）
T = TypeVar('T', bound=DeclarativeBase)


class BaseService(Generic[T]):
    """
    服务基类

    提供通用的 CRUD 操作和工具方法。

    用法:
        class UserService(BaseService[User]):
            def get_by_username(self, username: str) -> Optional[User]:
                return self.get_by_field("username", username)
    """

    model_class: type[T] = None  # 子类需要指定模型类

    def __init__(self, db: Session):
        """
        初始化服务

        Args:
            db: 数据库会话
        """
        self.db = db

    def get(self, id: int) -> Optional[T]:
        """
        根据 ID 获取记录

        Args:
            id: 记录 ID

        Returns:
            记录对象，不存在则返回 None
        """
        if self.model_class is None:
            raise NotImplementedError("model_class 必须在子类中定义")
        return self.db.query(self.model_class).filter(self.model_class.id == id).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """
        获取所有记录

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            记录列表
        """
        if self.model_class is None:
            raise NotImplementedError("model_class 必须在子类中定义")
        return self.db.query(self.model_class).limit(limit).offset(offset).all()

    def get_by_field(self, field: str, value) -> Optional[T]:
        """
        根据字段值获取记录

        Args:
            field: 字段名
            value: 字段值

        Returns:
            记录对象，不存在则返回 None
        """
        if self.model_class is None:
            raise NotImplementedError("model_class 必须在子类中定义")
        return self.db.query(self.model_class).filter(getattr(self.model_class, field) == value).first()

    def create(self, data: dict) -> T:
        """
        创建记录

        Args:
            data: 数据字典

        Returns:
            创建的记录对象
        """
        if self.model_class is None:
            raise NotImplementedError("model_class 必须在子类中定义")
        obj = self.model_class(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, data: dict) -> Optional[T]:
        """
        更新记录

        Args:
            id: 记录 ID
            data: 更新数据字典

        Returns:
            更新后的记录对象，不存在则返回 None
        """
        obj = self.get(id)
        if obj is None:
            return None

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        """
        删除记录

        Args:
            id: 记录 ID

        Returns:
            是否删除成功
        """
        obj = self.get(id)
        if obj is None:
            return False

        self.db.delete(obj)
        self.db.commit()
        return True

    def exists(self, id: int) -> bool:
        """
        检查记录是否存在

        Args:
            id: 记录 ID

        Returns:
            是否存在
        """
        return self.get(id) is not None

    def count(self) -> int:
        """
        获取记录总数

        Returns:
            记录总数
        """
        if self.model_class is None:
            raise NotImplementedError("model_class 必须在子类中定义")
        return self.db.query(self.model_class).count()


# ============ 便捷工具函数 ============

def get_current_user(db: Session) -> Optional[User]:
    """
    获取当前用户（单用户应用，默认返回第一个用户）

    Args:
        db: 数据库会话

    Returns:
        用户对象，不存在则返回 None
    """
    return db.query(User).first()


def get_user_or_raise(db: Session) -> User:
    """
    获取当前用户，不存在则抛出异常

    Args:
        db: 数据库会话

    Returns:
        用户对象

    Raises:
        ValueError: 用户不存在
    """
    user = get_current_user(db)
    if user is None:
        raise ValueError("用户不存在")
    return user
