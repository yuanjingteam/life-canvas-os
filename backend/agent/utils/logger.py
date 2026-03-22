"""
Agent 日志工具
"""
import logging
import sys
import os
from pathlib import Path
from datetime import datetime


# 判断是否为 IPC 模式（非开发模式）
IS_IPC_MODE = '--dev' not in sys.argv


def get_logger(name: str = "agent") -> logging.Logger:
    """获取 Agent 模块日志器"""
    logger = logging.getLogger(f"backend.agent.{name}")

    if not logger.handlers:
        # 在 IPC 模式下，使用简单的日志格式避免编码问题
        if IS_IPC_MODE:
            # IPC 模式：输出到 stderr，使用简单 ASCII 格式避免编码问题
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s [%(levelname)s] [agent.%(name)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
            )
            # 确保使用 UTF-8 编码
            if hasattr(handler.stream, 'reconfigure'):
                handler.stream.reconfigure(encoding='utf-8', errors='replace')
        else:
            # 开发模式：正常输出
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
            )

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger