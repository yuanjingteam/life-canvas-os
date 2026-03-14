"""
工具函数 - 日志
"""

import logging


def get_agent_logger() -> logging.Logger:
    """获取 Agent 日志记录器"""
    logger = logging.getLogger("agent")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
