"""
统一配置管理模块

所有应用配置集中在此模块管理，支持环境变量覆盖。
"""
import os
import secrets
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


# 获取 backend 目录的父级目录 (即项目根目录)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """应用统一配置类"""

    # ============ 基础配置 ============
    PROJECT_NAME: str = "Life Canvas OS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # ============ 数据库配置 ============
    # 优先使用 APP_DATA_DIR 环境变量（Electron 传入的 userData 目录）
    DATA_DIR: Path = Path(os.getenv("APP_DATA_DIR", BASE_DIR))
    SQLITE_URL: str = f"sqlite:///{DATA_DIR}/life_canvas.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", SQLITE_URL)

    # ============ 备份配置 ============
    BACKUP_DIR: Path = Path(os.getenv("BACKUP_DIR", DATA_DIR / "backups"))

    # ============ 安全配置 ============
    # 加密密钥 - 优先从环境变量读取，否则生成并保存
    ENCRYPTION_KEY: Optional[str] = os.getenv("ENCRYPTION_KEY")

    # PIN 码配置
    PIN_MAX_ATTEMPTS: int = int(os.getenv("PIN_MAX_ATTEMPTS", "3"))
    PIN_LOCK_DURATION_SECONDS: int = int(os.getenv("PIN_LOCK_DURATION", "30"))
    PIN_MIN_LENGTH: int = int(os.getenv("PIN_MIN_LENGTH", "6"))

    # 会话配置
    SESSION_EXPIRE_SECONDS: int = int(os.getenv("SESSION_EXPIRE", "300"))  # 5 分钟

    # ============ Agent 配置 ============
    # ReAct 循环配置
    AGENT_MAX_ITERATIONS: int = int(os.getenv("AGENT_MAX_ITERATIONS", "5"))
    AGENT_TEMPERATURE: float = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
    AGENT_MAX_TOKENS: int = int(os.getenv("AGENT_MAX_TOKENS", "2000"))

    # 上下文配置
    AGENT_CONTEXT_MAX_MESSAGES: int = int(os.getenv("AGENT_CONTEXT_MAX_MESSAGES", "20"))
    AGENT_CONTEXT_RECENT_MESSAGES: int = int(os.getenv("AGENT_CONTEXT_RECENT_MESSAGES", "10"))

    # 确认配置
    AGENT_CONFIRMATION_CODE_LENGTH: int = int(os.getenv("AGENT_CONFIRMATION_CODE_LENGTH", "6"))

    # ============ AI 服务配置 ============
    # DeepSeek 配置
    DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_DEFAULT_MODEL: str = os.getenv("DEEPSEEK_DEFAULT_MODEL", "deepseek-chat")

    # 豆包配置
    DOUBAO_API_URL: str = os.getenv("DOUBAO_API_URL", "https://ark.cn-beijing.volces.com/api/v3")
    DOUBAO_DEFAULT_MODEL: str = os.getenv("DOUBAO_DEFAULT_MODEL", "doubao-seed-2-0-lite-260215")

    # AI 请求配置
    AI_REQUEST_TIMEOUT: float = float(os.getenv("AI_REQUEST_TIMEOUT", "60.0"))
    AI_REQUEST_MAX_RETRIES: int = int(os.getenv("AI_REQUEST_MAX_RETRIES", "3"))

    # ============ 限流配置 ============
    RATE_LIMIT_DEFAULT_CAPACITY: int = int(os.getenv("RATE_LIMIT_DEFAULT_CAPACITY", "120"))
    RATE_LIMIT_DEFAULT_REFILL_RATE: float = float(os.getenv("RATE_LIMIT_DEFAULT_REFILL_RATE", "2.0"))
    RATE_LIMIT_AUTH_CAPACITY: int = int(os.getenv("RATE_LIMIT_AUTH_CAPACITY", "30"))
    RATE_LIMIT_AUTH_REFILL_RATE: float = float(os.getenv("RATE_LIMIT_AUTH_REFILL_RATE", "0.5"))

    # ============ 洞察配置 ============
    INSIGHT_DAILY_LIMIT: int = int(os.getenv("INSIGHT_DAILY_LIMIT", "3"))

    # ============ IPC 认证配置 ============
    # IPC 通信令牌（开发模式下可禁用认证便于调试）
    IPC_AUTH_ENABLED: bool = os.getenv("IPC_AUTH_ENABLED", "True").lower() == "true"
    IPC_SHARED_SECRET: Optional[str] = os.getenv("IPC_SHARED_SECRET")

    # ============ 日志配置 ============
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json 或 text
    LOG_FILE: Optional[Path] = Path(os.getenv("LOG_FILE")) if os.getenv("LOG_FILE") else None

    @property
    def get_encryption_key(self) -> bytes:
        """
        获取加密密钥

        - 优先从环境变量读取
        - 其次从数据目录的安全文件读取
        - 最后生成新密钥并保存

        Returns:
            加密密钥字节
        """
        if self.ENCRYPTION_KEY:
            return self.ENCRYPTION_KEY.encode('utf-8')

        # 尝试从安全文件读取
        key_file = self.DATA_DIR / ".encryption_key"
        if key_file.exists():
            try:
                return key_file.read_text().strip().encode('utf-8')
            except Exception:
                pass

        # 生成新密钥并保存
        new_key = secrets.token_urlsafe(32)
        try:
            key_file.parent.mkdir(parents=True, exist_ok=True)
            key_file.write_text(new_key)
            # 设置文件权限（仅所有者可读写）
            os.chmod(key_file, 0o600)
        except Exception as e:
            # 保存失败时返回临时密钥（仅开发模式允许）
            if self.DEBUG:
                return b"dev_temp_key_do_not_use_in_production_"
            raise RuntimeError(f"无法生成加密密钥：{e}")

        return new_key.encode('utf-8')

    @property
    def get_ipc_shared_secret(self) -> str:
        """
        获取 IPC 共享密钥

        - 优先从环境变量读取
        - 其次从数据目录读取
        - 最后生成新密钥

        Returns:
            IPC 共享密钥字符串
        """
        if self.IPC_SHARED_SECRET:
            return self.IPC_SHARED_SECRET

        # 尝试从文件读取
        secret_file = self.DATA_DIR / ".ipc_secret"
        if secret_file.exists():
            try:
                return secret_file.read_text().strip()
            except Exception:
                pass

        # 生成新密钥并保存
        new_secret = secrets.token_urlsafe(32)
        try:
            secret_file.parent.mkdir(parents=True, exist_ok=True)
            secret_file.write_text(new_secret)
            os.chmod(secret_file, 0o600)
        except Exception as e:
            if self.DEBUG:
                return "dev_ipc_secret_do_not_use_in_production"
            raise RuntimeError(f"无法生成 IPC 密钥：{e}")

        return new_secret

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
