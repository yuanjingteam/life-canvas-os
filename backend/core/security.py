"""
IPC 认证与安全模块

提供 IPC 通信的身份验证、请求签名和重放保护机制。
"""
import hmac
import hashlib
import time
import secrets
from typing import Optional, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)


class ReplayProtection:
    """
    重放保护机制

    使用 LRUCache 存储已使用的 nonce，防止重放攻击。
    """

    def __init__(self, max_size: int = 10000, expiry_seconds: int = 300):
        """
        初始化重放保护

        Args:
            max_size: 最大缓存 nonce 数量
            expiry_seconds: nonce 过期时间（秒）
        """
        self._cache: OrderedDict[str, float] = OrderedDict()
        self._max_size = max_size
        self._expiry_seconds = expiry_seconds

    def is_valid(self, nonce: str, timestamp: float) -> bool:
        """
        验证 nonce 是否有效（未使用且未过期）

        Args:
            nonce: 一次性随机数
            timestamp: 请求时间戳

        Returns:
            是否有效
        """
        now = time.time()

        # 检查时间窗口（允许±30 秒的时钟偏差）
        if abs(now - timestamp) > self._expiry_seconds:
            return False

        # 检查 nonce 是否已使用
        if nonce in self._cache:
            return False

        # 清理过期的 nonce
        self._cleanup()

        # 添加新的 nonce
        self._cache[nonce] = now

        # 如果超出大小限制，删除最旧的
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

        return True

    def _cleanup(self):
        """清理过期的 nonce"""
        now = time.time()
        cutoff = now - self._expiry_seconds

        # 删除过期的 nonce
        keys_to_remove = [
            key for key, ts in self._cache.items()
            if ts < cutoff
        ]
        for key in keys_to_remove:
            del self._cache[key]


# 全局重放保护实例
_replay_protection: Optional[ReplayProtection] = None


def get_replay_protection() -> ReplayProtection:
    """获取全局重放保护实例"""
    global _replay_protection
    if _replay_protection is None:
        _replay_protection = ReplayProtection(
            max_size=10000,
            expiry_seconds=settings.SESSION_EXPIRE_SECONDS
        )
    return _replay_protection


class IPCAuthenticator:
    """
    IPC 认证器

    提供基于 HMAC-SHA256 的双向认证机制。

    认证流程：
    1. 客户端生成随机 nonce 和当前时间戳
    2. 客户端计算签名：HMAC-SHA256(nonce + timestamp + payload, shared_secret)
    3. 客户端发送请求：{nonce, timestamp, signature, payload}
    4. 服务端验证时间戳是否在有效窗口内
    5. 服务端验证 nonce 是否未使用（重放保护）
    6. 服务端使用相同算法计算签名并比对
    7. 服务端返回响应（可选：也对响应签名）
    """

    def __init__(self, shared_secret: Optional[str] = None):
        """
        初始化认证器

        Args:
            shared_secret: 共享密钥，默认从配置读取
        """
        self._secret = shared_secret or settings.get_ipc_shared_secret
        self._replay_protection = get_replay_protection()

    def generate_signature(
        self,
        payload: str,
        nonce: Optional[str] = None,
        timestamp: Optional[float] = None
    ) -> Tuple[str, str, float]:
        """
        生成请求签名

        Args:
            payload: 请求体（JSON 字符串）
            nonce: 一次性随机数，不提供则自动生成
            timestamp: 时间戳，不提供则使用当前时间

        Returns:
            (nonce, timestamp, signature) 元组
        """
        if nonce is None:
            nonce = secrets.token_urlsafe(16)

        if timestamp is None:
            timestamp = time.time()

        # 构建待签名消息
        message = f"{nonce}{int(timestamp)}{payload}"

        # 计算 HMAC-SHA256 签名
        signature = hmac.new(
            self._secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return nonce, timestamp, signature

    def verify_signature(
        self,
        payload: str,
        nonce: str,
        timestamp: float,
        signature: str
    ) -> Tuple[bool, str]:
        """
        验证请求签名

        Args:
            payload: 请求体（JSON 字符串）
            nonce: 一次性随机数
            timestamp: 请求时间戳
            signature: 待验证的签名

        Returns:
            (是否有效，错误信息) 元组
        """
        # 验证时间窗口
        now = time.time()
        time_diff = abs(now - timestamp)

        if time_diff > settings.SESSION_EXPIRE_SECONDS:
            return False, f"请求时间戳过期（偏差：{time_diff:.1f}秒）"

        # 验证重放
        if not self._replay_protection.is_valid(nonce, timestamp):
            return False, "请求可能已被重放"

        # 重新计算签名并比对
        message = f"{nonce}{int(timestamp)}{payload}"
        expected_signature = hmac.new(
            self._secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # 使用常量时间比较防止时序攻击
        if not hmac.compare_digest(expected_signature, signature):
            return False, "签名验证失败"

        return True, ""

    def sign_request(self, payload: dict) -> dict:
        """
        对请求进行签名

        Args:
            payload: 请求体字典

        Returns:
            签名后的请求字典
        """
        import json
        payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        nonce, timestamp, signature = self.generate_signature(payload_str)

        return {
            "nonce": nonce,
            "timestamp": timestamp,
            "signature": signature,
            "payload": payload
        }

    def verify_request(self, request: dict) -> Tuple[bool, dict, str]:
        """
        验证并解析请求

        Args:
            request: 请求字典（包含 nonce, timestamp, signature, payload）

        Returns:
            (是否有效，解析后的 payload, 错误信息) 元组
        """
        import json

        nonce = request.get("nonce")
        timestamp = request.get("timestamp")
        signature = request.get("signature")
        payload = request.get("payload")

        if not all([nonce, timestamp, signature, payload]):
            return False, {}, "请求缺少必要字段"

        # 重新序列化 payload 以验证签名
        payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)

        is_valid, error_msg = self.verify_signature(
            payload_str, nonce, timestamp, signature
        )

        if not is_valid:
            return False, {}, error_msg

        return True, payload, ""


# 全局认证器实例
_authenticator: Optional[IPCAuthenticator] = None


def get_ipc_authenticator() -> IPCAuthenticator:
    """获取全局 IPC 认证器实例"""
    global _authenticator
    if _authenticator is None:
        # 如果认证被禁用，返回一个始终验证通过的认证器
        if not settings.IPC_AUTH_ENABLED:
            logger.warning("IPC 认证已禁用（仅开发模式允许）")
            _authenticator = _DisabledAuthenticator()
        else:
            _authenticator = IPCAuthenticator()
    return _authenticator


class _DisabledAuthenticator(IPCAuthenticator):
    """禁用的认证器（仅开发模式使用）"""

    def __init__(self):
        pass

    def generate_signature(self, payload: str, nonce: str = None, timestamp: float = None):
        return "disabled", time.time(), "disabled"

    def verify_signature(self, payload: str, nonce: str, timestamp: float, signature: str):
        return True, ""

    def sign_request(self, payload: dict) -> dict:
        return {
            "nonce": "disabled",
            "timestamp": time.time(),
            "signature": "disabled",
            "payload": payload
        }

    def verify_request(self, request: dict) -> Tuple[bool, dict, str]:
        payload = request.get("payload", request)
        return True, payload, ""
