# backend/schemas/__init__.py

# 假设 user.py 里定义了 UserUpdate 和 AIConfigUpdate
from .user import UserUpdate, AIConfigUpdate

# 将来如果有 record.py，也可以加：
# from .record import RecordCreate, RecordRead
