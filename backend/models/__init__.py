# 数据模型模块
# backend/models/__init__.py

from .user import User
from .dimension import Dimension
from .record import DailyRecord
from .diary import Diary
from .insight import Insight

# 这里的顺序不重要，重要的是把所有类都导出来
# 这样以后你在其他文件只需要：from backend.models import User, DailyRecord
