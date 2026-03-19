# Agent 模块问题修复记录

**日期**: 2026-03-19 (更新：2026-03-19 第二次)

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

## 问题三：会话历史加载失败 - 会话不存在

**日期**: 2026-03-17

### 问题描述

前端加载会话历史时报错：
```
Failed to load history: Error: 会话不存在
    at useAgentApi.ts:181:11
    at async AgentPage.tsx:116:25
```

### 根本原因

前端使用 `getSessionId()` 生成随机会话 ID（格式：`sess_${random}`），当切换到新会话或首次访问不存在的会话时，后端的 `ContextManager` 中没有该会话的上下文，返回 404 错误。

**问题链路**：
1. 前端 `ChatPanel.tsx` 调用 `loadSessionHistory(sessionId)`
2. `useAgentApi.getHistory()` 请求 `/api/agent/history?session_id=xxx`
3. 后端 `agent.py` 的 `get_history()` 检查 `ctx_manager.get(session_id)`
4. 新会话在 backend 不存在，返回 404 "会话不存在"

### 解决方案

**文件**: `backend/api/agent.py`

修改 `/api/agent/history` 端点，当会话不存在时返回空数组而非 404 错误：

```python
@router.get("/history", response_model=Dict[str, Any])
async def get_history(session_id: str, limit: int = 10):
    """
    获取会话历史

    返回指定会话的对话历史记录。如果会话不存在，返回空列表。
    """
    try:
        ctx_manager = get_context_manager()
        if not ctx_manager:
            return error_response(message="上下文管理器未初始化", code=500)

        context = ctx_manager.get(session_id)
        if not context:
            # 会话不存在可能是新会话，返回空列表
            return success_response(
                data={"messages": [], "session_id": session_id},
                message="会话不存在或为空",
                code=200,
            )

        # 获取消息历史
        messages = context.messages[-limit:] if context.messages else []

        return success_response(
            data={"messages": messages, "session_id": session_id},
            message="获取历史成功",
            code=200,
        )

    except Exception as e:
        return error_response(message=f"获取历史失败：{str(e)}", code=500)
```

### 验证

修复后，新会话加载时：
- 前端 `getHistory()` 收到 200 响应，`data.messages = []`
- `ChatPanel` 正常初始化空消息列表
- 用户可以正常开始新会话对话

### 经验

1. **前端生成的 ID 要与后端同步** - 考虑在首次请求时自动创建会话上下文
2. **新会话应返回空数据而非错误** - 对于可选资源（如历史记录），不存在时返回空数组更合理
3. **错误处理要区分场景** - 404 适用于"资源应存在但不存在"，新会话应返回 200 + 空数据

---

## 问题四：AI 调用失败缺少用户提示

**日期**: 2026-03-17

### 问题描述

1. 用户未配置 API Key 时，AI 调用失败但没有任何提示
2. AI 调用失败（如超时、认证错误）后，用户不知道原因

### 解决方案

#### 1. 后端修复

**文件**: `backend/agent/init.py`

**新增错误类型**:
```python
class AgentConfigError(Exception):
    """Agent 配置错误（如缺少 API Key）"""
    pass
```

**API Key 检测** - 在 `execute_chat` 和 `execute_stream_chat` 函数中添加：
```python
# 检查 LLM 客户端是否配置了 API Key
llm_client = _agent_executor.llm
if hasattr(llm_client, 'clients') and llm_client.clients:
    # LLMClientWithFallback，检查是否有有效客户端
    has_valid_client = False
    for client in llm_client.clients:
        if hasattr(client, 'api_key') and client.api_key:
            has_valid_client = True
            break
    if not has_valid_client:
        raise AgentConfigError("未配置 AI API Key，请先在设置中配置 DeepSeek 或豆包 API Key")
```

**异常处理** - 捕获各类 LLM 错误并返回友好提示：
```python
try:
    response = await _agent_executor.llm.chat(...)
except AuthenticationError as e:
    yield {"type": "error", "data": f"API Key 验证失败：{str(e)}，请检查 API Key 是否正确"}
except RateLimitError as e:
    yield {"type": "error", "data": f"请求频率超限：{str(e)}，请稍后重试"}
except TimeoutError as e:
    yield {"type": "error", "data": f"请求超时：{str(e)}，请检查网络连接"}
except ServerError as e:
    yield {"type": "error", "data": f"服务端错误：{str(e)}，请稍后重试"}
```

#### 2. 前端修复

**文件**: `src/renderer/components/agent/ChatPanel.tsx`

**导入 toast**:
```typescript
import { toast } from '~/renderer/lib/toast'
```

**错误提示逻辑**:
```typescript
// 流式响应错误处理
if (chunk.type === 'error') {
  const errorMsg = chunk.data || '抱歉，我遇到了一些问题，请稍后重试。'
  // ...更新消息
  // 显示错误提示
  if (errorMsg.includes('API Key')) {
    toast.error(errorMsg, { duration: 5000 })
  } else {
    toast.error(errorMsg)
  }
}

// 非流式模式错误处理
catch (error) {
  const errorMessage = error instanceof Error ? error.message : '未知错误'
  // 显示错误提示
  if (errorMessage.includes('API Key') || errorMessage.includes('未配置 AI')) {
    toast.error(errorMessage, { duration: 5000 })
  } else {
    toast.error(errorMessage || '聊天失败，请稍后重试')
  }
}
```

### 错误类型覆盖

| 错误类型 | 提示信息 | 持续时间 |
|---------|---------|---------|
| 未配置 API Key | "未配置 AI API Key，请先在设置中配置 DeepSeek 或豆包 API Key" | 5 秒 |
| API Key 验证失败 | "API Key 验证失败：{详情}，请检查 API Key 是否正确" | 5 秒 |
| 请求频率超限 | "请求频率超限：{详情}，请稍后重试" | 默认 |
| 请求超时 | "请求超时：{详情}，请检查网络连接" | 默认 |
| 服务端错误 | "服务端错误：{详情}，请稍后重试" | 默认 |
| 其他错误 | 具体错误信息 | 默认 |

### 验证

1. **未配置 API Key**: 显示 5 秒错误提示，引导用户去设置
2. **网络超时**: 显示超时错误，提示检查网络
3. **正常调用**: 流式响应正常工作

### 经验

1. **关键错误要长显示** - API Key 相关错误设置 5 秒显示时间
2. **错误信息要具体** - 区分不同类型的错误，给出针对性建议
3. **降级策略** - 流式失败后自动尝试非流式模式

---

## 问题五：会话管理功能实现 - 多会话切换

**日期**: 2026-03-18

### 需求描述

实现多会话管理功能，允许用户：
1. 创建新会话时生成新的 session ID
2. 旧的 session ID 被保留
3. 切换不同的 session ID 来切换不同的会话窗口
4. 每个会话有独立的对话历史

### 问题分析

之前的会话管理存在问题：
- `createSession()` 调用 `getSessionId()`，如果 localStorage 中已有 session ID 则返回现有的
- 无法创建多个独立的会话
- 没有会话列表功能，无法切换会话

### 解决方案

#### 1. 前端修复 - 会话管理

**文件**: `src/renderer/hooks/useAgentApi.ts`

**新增会话 ID 列表存储**:
```typescript
// 会话 ID 存储键
const SESSION_ID_STORAGE_KEY = 'life_canvas_agent_session_id'

// 会话 ID 列表存储键
const SESSION_ID_LIST_STORAGE_KEY = 'life_canvas_agent_session_ids'

// 生成新的会话 ID
function generateSessionId(): string {
  return `sess_${Math.random().toString(36).substring(2, 14)}`
}

// 保存会话 ID 到历史列表
function saveSessionToHistory(sessionId: string): void {
  try {
    const existing = localStorage.getItem(SESSION_ID_LIST_STORAGE_KEY)
    const sessionList: string[] = existing ? JSON.parse(existing) : []
    if (!sessionList.includes(sessionId)) {
      sessionList.unshift(sessionId) // 新会话放到列表开头
      localStorage.setItem(SESSION_ID_LIST_STORAGE_KEY, JSON.stringify(sessionList))
    }
  } catch (error) {
    console.error('Failed to save session to history:', error)
  }
}

// 获取会话历史列表
function getSessionHistory(): string[] {
  try {
    const existing = localStorage.getItem(SESSION_ID_LIST_STORAGE_KEY)
    return existing ? JSON.parse(existing) : []
  } catch (error) {
    console.error('Failed to get session history:', error)
    return []
  }
}

// 从会话历史列表中移除
function removeSessionFromHistory(sessionId: string): void {
  try {
    const existing = localStorage.getItem(SESSION_ID_LIST_STORAGE_KEY)
    const sessionList: string[] = existing ? JSON.parse(existing) : []
    const filtered = sessionList.filter(id => id !== sessionId)
    localStorage.setItem(SESSION_ID_LIST_STORAGE_KEY, JSON.stringify(filtered))
  } catch (error) {
    console.error('Failed to remove session from history:', error)
  }
}
```

**修复 `createSession` 函数**:
```typescript
// 修复前 - 会返回现有的 session ID
const createSession = useCallback(() => {
  const newSessionId = getSessionId()  // 如果 localStorage 中有 ID 则返回现有的
  setSessionId(newSessionId)
  return newSessionId
}, [])

// 修复后 - 总是生成新的 session ID
const createSession = useCallback(() => {
  const newSessionId = generateSessionId()  // 总是生成新的
  setSessionId(newSessionId)
  return newSessionId
}, [])
```

#### 2. 会话列表侧边栏

**文件**: `src/renderer/components/agent/SessionSidebar.tsx`

**合并后端会话和 localStorage 会话**:
```typescript
const loadSessions = async () => {
  setIsLoading(true)
  try {
    // 从 localStorage 获取会话 ID 列表
    const sessionIds = getSessionHistory()

    // 从后端获取有上下文的会话列表（有实际对话的会话）
    const backendSessions = await getSessions()
    const backendSessionMap = new Map(
      (backendSessions.sessions || []).map((s: any) => [s.session_id, s])
    )

    const mergedSessions: Array<{
      session_id: string
      message_count: number
      last_message_time: string | null
      last_message_preview: string | null
      last_message_role: string | null
    }> = []

    // 先添加有上下文的会话
    for (const session of backendSessions.sessions || []) {
      mergedSessions.push({
        session_id: session.session_id,
        message_count: session.message_count,
        last_message_time: session.last_message_time,
        last_message_preview: session.last_message_preview,
        last_message_role: session.last_message_role,
      })
    }

    // 添加没有上下文的会话 ID（新创建但还没对话的会话）
    for (const sessionId of sessionIds) {
      if (!backendSessionMap.has(sessionId)) {
        mergedSessions.push({
          session_id: sessionId,
          message_count: 0,
          last_message_time: null,
          last_message_preview: null,
          last_message_role: null,
        })
      }
    }

    setSessions(mergedSessions)
  } catch (error) {
    console.error('Failed to load sessions:', error)
    // 降级：只显示 localStorage 中的会话 ID
    const sessionIds = getSessionHistory()
    setSessions(
      sessionIds.map(id => ({
        session_id: id,
        message_count: 0,
        last_message_time: null,
        last_message_preview: null,
        last_message_role: null,
      }))
    )
  } finally {
    setIsLoading(false)
  }
}
```

### 会话管理流程

1. **创建会话**:
   - 用户点击"新建会话"
   - `createSession()` 调用 `generateSessionId()` 生成新的 session ID
   - `setSessionId()` 将新 ID 设为当前会话
   - `saveSessionToHistory()` 将 ID 保存到 localStorage 数组

2. **切换会话**:
   - 用户从侧边栏选择一个会话
   - `switchSession(sessionId)` 更新当前会话 ID
   - `getHistory(sessionId)` 加载该会话的历史消息
   - 更新 UI 显示对应会话的内容

3. **删除会话**:
   - 用户点击删除按钮
   - `deleteSession(sessionId)` 删除后端上下文
   - `removeSessionFromHistory(sessionId)` 从 localStorage 移除

### 经验

1. **多会话管理** - 使用 localStorage 数组存储所有会话 ID，支持会话切换
2. **创建新会话** - `createSession()` 应总是生成新的 ID，而不是复用现有的
3. **会话合并显示** - 合并后端有上下文的会话和前端 localStorage 中的会话 ID

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

---

## 问题六：AgentPage 缺少 API Key 错误提示

**日期**: 2026-03-19

### 问题描述

用户未配置 API Key 时：
- **快捷方式（悬浮球 ChatPanel）**：正确显示错误提示
- **固定页面（AgentPage）**：没有显示错误提示

### 根本原因

`AgentPage.tsx` 的流式错误处理中只更新了消息状态，但缺少 `toast.error()` 调用：

```typescript
// 修复前 - 只显示错误消息，不显示 toast
} else if (chunk.type === 'error') {
  setMessages(prev =>
    prev.map(msg =>
      msg.id === assistantMessageId
        ? { ...msg, content: errorMsg, isError: true }
        : msg
    )
  )
  // 缺少 toast.error() 调用
}
```

### 解决方案

**文件**: `src/renderer/pages/agent/AgentPage.tsx`

1. 导入 `toast`：
```typescript
import { toast } from '~/renderer/lib/toast'
```

2. 在错误处理中添加 toast 提示：
```typescript
} else if (chunk.type === 'error') {
  const errorMsg = chunk.data || '抱歉，我遇到了一些问题，请稍后重试。'
  setMessages(prev =>
    prev.map(msg =>
      msg.id === assistantMessageId
        ? { ...msg, content: errorMsg, isError: true }
        : msg
    )
  )
  // 显示错误提示
  if (errorMsg.includes('API Key')) {
    toast.error(errorMsg, { duration: 5000 })
  } else {
    toast.error(errorMsg)
  }
}
```

---

## 问题七：配置 API Key 后仍提示未配置

**日期**: 2026-03-19

### 问题描述

用户在设置中配置好 API Key 后，与 AI 对话时仍然提示"未配置 AI API Key"。

### 根本原因

`_agent_executor` 在应用启动时初始化后就不再重新加载配置。当用户在设置中配置了 API Key 后，`_agent_executor.llm` 仍然是启动时创建的空客户端（`api_key=""`）。

**问题链路**：
1. 应用启动 → `_create_llm_client_with_fallback()` 被调用
2. 此时数据库中没有 API Key → 创建空的 DeepSeek 客户端
3. 用户在设置中配置 API Key → 数据库更新
4. 用户与 AI 对话 → `_agent_executor.llm` 仍是旧的空客户端
5. API Key 检测失败 → 返回错误提示

### 解决方案

**文件**: `backend/agent/init.py`

在 `execute_chat` 和 `execute_stream_chat` 函数中，每次调用时重新从数据库读取 API Key 配置：

```python
async def execute_chat(message: str, session_id: Optional[str] = None, ...):
    global _agent_executor

    if _agent_executor is None:
        _agent_executor = initialize_agent()

    # 每次调用时重新从数据库读取 API Key 配置
    deepseek_key, deepseek_model, doubao_key, doubao_model = _get_api_key_from_db()

    # 检查是否有有效的 API Key
    has_valid_key = bool(deepseek_key) or bool(doubao_key)
    if not has_valid_key:
        raise AgentConfigError("未配置 AI API Key，请先在设置中配置 DeepSeek 或豆包 API Key")

    # 如果需要，重新初始化 LLM 客户端（当 API Key 发生变化时）
    llm_client = _agent_executor.llm
    need_reinit = False

    # 检查当前客户端是否有效
    if hasattr(llm_client, 'clients') and llm_client.clients:
        has_valid_client = False
        for client in llm_client.clients:
            if hasattr(client, 'api_key') and client.api_key:
                has_valid_client = True
                break
        if not has_valid_client:
            need_reinit = True

    # 如果需要重新初始化且有有效的 API Key
    if need_reinit and has_valid_key:
        print("重新初始化 LLM 客户端...")
        _agent_executor.llm = _create_llm_client_with_fallback()

    # 继续执行...
```

### 经验

1. **动态配置需要动态加载** - 对于可能变化的配置（如 API Key），不应只在启动时读取一次
2. **懒加载 + 缓存失效** - 可以在配置变更时使缓存失效，或使用懒加载方式每次检查
3. **配置变更通知** - 考虑实现配置变更事件，当 API Key 更新时主动重新初始化 LLM 客户端

---

## 问题八：对话时显示两个 AI 对话框

**日期**: 2026-03-19

### 问题描述

用户在与 AI 对话时，界面上显示两个 AI 对话框：
- 一个显示"..."流式指示器的消息气泡
- 一个独立的 loading 指示器

### 根本原因

`ChatPanel.tsx` 和 `AgentPage.tsx` 中同时渲染了两个视觉元素：

1. **消息列表中的助手消息** - 当 `message.isStreaming === true` 时，`ChatMessage` 组件内部显示流式指示器（三个跳动的点）
2. **独立的 loading 指示器** - 当 `isLoading === true` 时，额外渲染一个独立的 loading 气泡

**问题代码**:

```typescript
// ChatPanel.tsx 和 AgentPage.tsx 类似
{messages.map(message => (
  <ChatMessage key={message.id} message={message} />
))}

{/* 加载中 */}
{isLoading && (
  <div className="flex items-start gap-2">
    <div className="w-8 h-8 rounded-full ...">
      <Bot className="w-4 h-4" />
    </div>
    <div className="px-4 py-3">
      <div className="typing-indicator">...</div>
    </div>
  </div>
)}
```

### 解决方案

**文件**:
- `src/renderer/components/agent/ChatPanel.tsx`
- `src/renderer/pages/agent/AgentPage.tsx`

**修改**: 移除独立的 `isLoading` loading 指示器，因为 `ChatMessage` 组件已经通过 `isStreaming` 标志提供了视觉反馈。

**修复后**:
```typescript
{messages.map(message => (
  <ChatMessage key={message.id} message={message} />
))}

<div ref={messagesEndRef} />
```

**流程**:
1. 用户发送消息
2. 添加空的助手消息到列表，`isStreaming: true`
3. `ChatMessage` 渲染该消息，显示流式指示器
4. 接收流式响应，更新消息内容
5. 流式完成，`isStreaming: false`（或移除消息）

### 经验

1. **避免重复视觉反馈** - 流式消息已经有指示器，不需要额外的 loading 指示器
2. **消息状态驱动 UI** - 使用消息的 `isStreaming` 标志控制视觉状态，而非独立的 `isLoading` 状态
3. **简化渲染逻辑** - 移除冗余的 loading 指示器，让消息列表自己渲染所有消息

---

## 问题九：不同会话的历史对话记录渲染混乱

**日期**: 2026-03-19

### 问题描述

切换不同会话时，每个会话的历史对话记录都渲染在同一个对话框中，消息混乱。

### 根本原因

后端返回的历史消息没有 `id` 字段，前端使用 `Date.now().toString()` 作为 fallback ID：

**后端消息格式** (`backend/agent/models/context.py`):
```python
{
    "role": role,
    "content": content,
    "timestamp": datetime.now().isoformat(),
    # 没有 id 字段！
}
```

**前端加载逻辑** (修复前):
```typescript
history.map((msg: any) => ({
  id: msg.id || Date.now().toString(),  // msg.id 是 undefined
  role: msg.role,
  content: msg.content,
  timestamp: msg.timestamp,
}))
```

**问题链路**:
1. 用户切换会话 A，加载历史消息，生成 ID（基于 `Date.now()`）
2. 用户快速切换会话 B，加载历史消息，生成 ID（可能相同的 `Date.now()`）
3. React 使用相同的 `key` 渲染不同消息，导致混淆

### 解决方案

**文件**:
- `src/renderer/components/agent/ChatPanel.tsx`
- `src/renderer/pages/agent/AgentPage.tsx`

**修改**: 使用`会话 ID+ 索引 + 时间戳`生成唯一 ID：

```typescript
// 修复前
history.map((msg: any) => ({
  id: msg.id || Date.now().toString(),
  role: msg.role,
  content: msg.content,
  timestamp: msg.timestamp,
}))

// 修复后
history.map((msg: any, index: number) => ({
  id: `${sessionId}_${index}_${Date.now()}`, // 使用会话 ID+ 索引生成唯一 ID
  role: msg.role,
  content: msg.content,
  timestamp: msg.timestamp,
}))
```

### 经验

1. **消息 ID 必须唯一** - React 列表渲染依赖 `key` 的唯一性，重复的 `key` 会导致渲染混乱
2. **后端消息应包含 ID** - 考虑在后端 `ContextState.add_message()` 中生成并存储消息 ID
3. **Fallsback ID 要可靠** - 使用 `Date.now()` 作为 fallback 在快速操作时可能产生重复 ID
