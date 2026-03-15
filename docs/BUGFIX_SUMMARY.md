# Agent 模块问题修复记录

**日期**: 2026-03-14 (更新：2026-03-15)

---

## 问题一：Agent 接口调用失败

**日期**: 2026-03-14

`pnpm dev` 后 Agent 接口调用失败，后端无响应。

### 原因

缺失 `aiohttp` 依赖

Agent 的 LLM 客户端（DeepSeek/豆包）依赖 `aiohttp` 发起 HTTP 请求，但虚拟环境中未安装该依赖。

### 解决方案

```bash
source venv/bin/activate
pip install "aiohttp>=3.9.0"
```

### 代码修复

**`backend/agent/llm/deepseek.py` 和 `doubao.py`**

```python
# 错误：aiohttp.ClientTimeout 不是异常类
except aiohttp.ClientTimeout:
    raise TimeoutError("请求超时")

# 正确
except asyncio.TimeoutError:
    raise TimeoutError("请求超时")
```

**`ChatPanel.tsx`**

集成 ConfirmDialog 确认对话框，支持风险操作确认流程。

### 经验

1. **新增模块后立即安装依赖** - 修改 `requirements.txt` 后执行 `pip install -r requirements.txt`
2. **异常类型要准确** - `aiohttp.ClientTimeout` 是配置类，不是异常类
3. **启动前清理端口** - `lsof -ti:8000 | xargs kill -9`

---

## 问题二：AI 回复只显示一个字符

**日期**: 2026-03-15

### 问题描述

AI 助手回复异常，每次只显示一个字符，如"好"、"我"、"你"等，每条消息有不同的时间戳。

### 根本原因

两个独立的 bug 导致：

1. **后端**: `backend/agent/init.py` 文件顶部缺少 `import asyncio` 导入
2. **前端**: Vite 环境中错误地使用了 `process.env.NODE_ENV` 来判断开发/生产模式

### 解决方案

#### 1. 后端修复

**文件**: `backend/agent/init.py`

在文件顶部添加 `import asyncio`:

```python
"""
Agent 模块初始化

负责初始化 LLM 客户端、注册 Skills、创建执行器实例。
"""

import os
import asyncio  # 新增：修复 NameError
from typing import Dict, Any, Optional
from .llm.base import LLMClient, LLMMessage, LLMToolDefinition, LLMResponse, LLMProviderType
# ... 其他导入
```

**原因**: 流式输出代码使用 `asyncio.sleep(0.02)` 模拟打字机效果，但缺少导入导致 `NameError: name 'asyncio' is not defined`

#### 2. 前端修复

**文件**:
- `src/renderer/components/agent/ChatPanel.tsx`
- `src/renderer/api/client.ts`
- `src/renderer/hooks/useDataApi.ts`

**修改**: 将 `process.env.NODE_ENV === 'development'` 改为 `import.meta.env.DEV`

**`ChatPanel.tsx` 第 53 行**:
```typescript
// 修复前
const [useStreaming, setUseStreaming] = useState(process.env.NODE_ENV === 'development')

// 修复后
const [useStreaming, setUseStreaming] = useState(import.meta.env.DEV)
```

**`api/client.ts` 第 7 行**:
```typescript
// 修复前
const IS_DEV = process.env.NODE_ENV === 'development'

// 修复后
const IS_DEV = import.meta.env.DEV
```

**原因**: Vite 环境中应使用 `import.meta.env.DEV` 而非 Node.js 的 `process.env.NODE_ENV`。Vite 在构建时会处理 `import.meta.env`，而 `process.env` 在浏览器环境中可能为 `undefined`。

### 验证

后端流式输出测试结果（正常）:

```
Initializing agent...
DeepSeek 客户端创建成功，模型：deepseek-chat

Testing stream chat with simple message...
Chunk 1: {'type': 'content', 'data': '你'}
Chunk 2: {'type': 'content', 'data': '好'}
Chunk 3: {'type': 'content', 'data': '！'}
Chunk 4: {'type': 'content', 'data': '我'}
Chunk 5: {'type': 'content', 'data': '是'}
...

Total chunks received: 15
Full content: 你好！我是 Life Canv
```

### 经验

1. **Vite 环境变量** - 在 Vite 项目中使用 `import.meta.env.DEV` 而非 `process.env.NODE_ENV`
2. **检查导入语句** - 使用异步功能前确保导入 `asyncio`
3. **流式输出测试** - 测试完整链路，包括后端生成和前端解析

---

## 通用验证步骤

```bash
# 检查 Python 依赖
source venv/bin/activate
python3 -c "import aiohttp; print(aiohttp.__version__)"

# 清理端口
lsof -ti:8000 | xargs kill -9

# 启动开发服务器
pnpm dev
```
