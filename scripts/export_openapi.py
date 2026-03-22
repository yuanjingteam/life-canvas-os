#!/usr/bin/env python3
"""
导出 OpenAPI 格式的接口文档
"""
import json
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.health import router as health_router
from backend.api.test import router as test_router
from backend.api.auth import router as auth_router
from backend.api.diet import router as diet_router
from backend.api.systems import router as systems_router
from backend.api.users import router as users_router
from backend.api.journals import router as journals_router
from backend.api.insights import router as insights_router
from backend.api.data import router as data_router
from backend.api.timeline import router as timeline_router
from backend.api.agent import router as agent_router
from backend.core.exceptions import setup_exception_handlers


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    app = FastAPI(
        title="Life Canvas OS API",
        description="""# 八维生命平衡系统 API

基于「八维生命平衡模型」的个人生活管理桌面应用。

## 八维系统

| 系统类型 | 中文名 | 描述 |
|---------|-------|------|
| FUEL | 饮食系统 | 记录饮食、营养追踪 |
| PHYSICAL | 运动系统 | 运动记录、体能管理 |
| INTELLECTUAL | 读书系统 | 阅读记录、知识管理 |
| OUTPUT | 工作系统 | 工作产出、任务管理 |
| DREAM | 梦想系统 | 目标追踪、愿景规划 |
| ASSET | 财务系统 | 收支记录、资产管理 |
| CONNECTION | 社交系统 | 人际关系、社交活动 |
| ENVIRONMENT | 环境系统 | 居住环境、生活空间 |

## 认证方式

使用 PIN 码认证（6位数字）。

## 统一响应格式

所有接口返回统一格式：
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {},
  "timestamp": "2024-01-01T00:00:00"
}
```
""",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_exception_handlers(app)

    # 注册路由
    app.include_router(health_router, tags=["health"])
    app.include_router(test_router, tags=["test"])
    app.include_router(auth_router, tags=["authentication"])
    app.include_router(diet_router, tags=["diet"])
    app.include_router(systems_router, tags=["systems"])
    app.include_router(users_router, tags=["users"])
    app.include_router(journals_router, tags=["journals"])
    app.include_router(insights_router, tags=["insights"])
    app.include_router(data_router, tags=["data-management"])
    app.include_router(timeline_router, tags=["timeline"])
    app.include_router(agent_router, tags=["agent"])

    return app


def export_openapi(output_path: str = "docs/openapi.json"):
    """导出 OpenAPI 文档"""
    app = create_app()
    openapi_schema = app.openapi()

    # 确保输出目录存在
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

    # 统计信息
    paths = openapi_schema.get("paths", {})
    endpoint_count = sum(len(methods) for methods in paths.values())

    print(f"[OK] OpenAPI 文档已导出到: {output_file}")
    print(f"[INFO] 共 {len(paths)} 个路径, {endpoint_count} 个端点")

    # 按标签分组统计
    tags_count = {}
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "patch", "delete"]:
                for tag in details.get("tags", ["untagged"]):
                    tags_count[tag] = tags_count.get(tag, 0) + 1

    print("\n[模块统计]")
    for tag, count in sorted(tags_count.items()):
        print(f"   {tag}: {count} 个端点")

    return output_file


if __name__ == "__main__":
    export_openapi()