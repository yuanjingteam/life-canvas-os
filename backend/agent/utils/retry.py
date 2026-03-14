"""
工具函数 - 重试机制
"""

import asyncio
import time
from functools import wraps
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential: bool = True,
    exceptions: tuple = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    带退避的重试装饰器

    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        exponential: 是否使用指数退避
        exceptions: 需要重试的异常类型

    Returns:
        装饰器
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        break

                    # 计算延迟
                    if exponential:
                        delay = min(base_delay * (2**attempt), max_delay)
                    else:
                        delay = base_delay

                    await asyncio.sleep(delay)

            raise last_exception  # type: ignore

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        break

                    # 计算延迟
                    if exponential:
                        delay = min(base_delay * (2**attempt), max_delay)
                    else:
                        delay = base_delay

                    time.sleep(delay)

            raise last_exception  # type: ignore

        # 检查原函数是否是异步函数
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
