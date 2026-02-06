"""认证相关API接口"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import datetime
import hashlib
import json
import os

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# PIN码存储文件
PIN_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "pin.json")


class PinVerifyRequest(BaseModel):
    """PIN码验证请求模型"""
    pin: str


class PinSetRequest(BaseModel):
    """设置PIN码请求模型"""
    pin: str


class AuthResponse(BaseModel):
    """认证响应模型"""
    message: str
    timestamp: str
    data: dict


def ensure_data_dir():
    """确保数据目录存在"""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)


def get_stored_pin():
    """获取存储的PIN码"""
    ensure_data_dir()
    if os.path.exists(PIN_FILE):
        try:
            with open(PIN_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('pin_hash')
        except:
            return None
    return None

def set_stored_pin(pin: str):
    """存储PIN码（哈希处理）"""
    ensure_data_dir()
    pin_hash = hashlib.sha256(pin.encode()).hexdigest()
    with open(PIN_FILE, 'w', encoding='utf-8') as f:
        json.dump({'pin_hash': pin_hash}, f)
    return pin_hash

def verify_pin(pin: str) -> bool:
    """验证PIN码"""
    stored_hash = get_stored_pin()
    if not stored_hash:
        return False
    pin_hash = hashlib.sha256(pin.encode()).hexdigest()
    return pin_hash == stored_hash


@router.post("/verify", response_model=AuthResponse)
async def verify_pin_code(request: PinVerifyRequest):
    """
    验证PIN码

    Args:
        request: 包含PIN码的请求对象

    Returns:
        认证响应，包含验证结果
    """
    is_valid = verify_pin(request.pin)
    if not is_valid:
        raise HTTPException(status_code=401, detail="PIN码验证失败")

    return AuthResponse(
        message="PIN码验证成功",
        timestamp=datetime.datetime.now().isoformat(),
        data={
            "status": "success",
            "authenticated": True,
            "timestamp": datetime.datetime.now().isoformat()
        }
    )


@router.post("/set", response_model=AuthResponse)
async def set_pin_code(request: PinSetRequest):
    """
    设置PIN码

    Args:
        request: 包含新PIN码的请求对象

    Returns:
        设置响应，包含操作结果
    """
    if len(request.pin) < 4:
        raise HTTPException(status_code=400, detail="PIN码必须至少4位数字")

    set_stored_pin(request.pin)

    return AuthResponse(
        message="PIN码设置成功",
        timestamp=datetime.datetime.now().isoformat(),
        data={
            "status": "success",
            "pin_set": True,
            "timestamp": datetime.datetime.now().isoformat()
        }
    )


@router.get("/status", response_model=AuthResponse)
async def get_auth_status():
    """
    获取认证状态

    Returns:
        认证状态响应，包含是否已设置PIN码
    """
    has_pin = get_stored_pin() is not None

    return AuthResponse(
        message="认证状态获取成功",
        timestamp=datetime.datetime.now().isoformat(),
        data={
            "status": "success",
            "has_pin_set": has_pin,
            "timestamp": datetime.datetime.now().isoformat()
        }
    )


# IPC通信处理器
def handle_auth_action(action: str, params: dict) -> dict:
    """
    处理IPC通信中的认证相关操作

    Args:
        action: 操作类型
        params: 操作参数

    Returns:
        操作结果
    """
    if action == 'verify_pin':
        pin = params.get('pin', '')
        is_valid = verify_pin(pin)
        if is_valid:
            return {
                'action': 'verify_pin',
                'status': 'ok',
                'data': {
                    'authenticated': True,
                    'timestamp': datetime.datetime.now().isoformat()
                }
            }
        else:
            return {
                'action': 'verify_pin',
                'status': 'error',
                'error': 'Invalid PIN code'
            }

    elif action == 'set_pin':
        pin = params.get('pin', '')
        if len(pin) < 4:
            return {
                'action': 'set_pin',
                'status': 'error',
                'error': 'PIN码必须至少4位数字'
            }
        set_stored_pin(pin)
        return {
            'action': 'set_pin',
            'status': 'ok',
            'data': {
                'pin_set': True,
                'timestamp': datetime.datetime.now().isoformat()
            }
        }

    elif action == 'get_auth_status':
        has_pin = get_stored_pin() is not None
        return {
            'action': 'get_auth_status',
            'status': 'ok',
            'data': {
                'has_pin_set': has_pin,
                'timestamp': datetime.datetime.now().isoformat()
            }
        }

    else:
        return {
            'action': action,
            'status': 'error',
            'error': '未知的认证操作'
        }
