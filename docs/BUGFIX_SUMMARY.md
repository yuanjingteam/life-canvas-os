# Agent 模块问题修复记录

**日期**: 2026-03-14

---

## 问题

`pnpm dev` 后 Agent 接口调用失败，后端无响应。

---

## 原因

缺失 `aiohttp` 依赖

Agent 的 LLM 客户端（DeepSeek/豆包）依赖 `aiohttp` 发起 HTTP 请求，但虚拟环境中未安装该依赖。

---

## 解决方案

```bash
source venv/bin/activate
pip install "aiohttp>=3.9.0"
```

---

## 代码修复

### 1. `backend/agent/llm/deepseek.py` 和 `doubao.py`

```python
# 错误：aiohttp.ClientTimeout 不是异常类
except aiohttp.ClientTimeout:
    raise TimeoutError("请求超时")

# 正确
except asyncio.TimeoutError:
    raise TimeoutError("请求超时")
```

### 2. `ChatPanel.tsx`

集成 ConfirmDialog 确认对话框，支持风险操作确认流程。

---

## 经验

1. **新增模块后立即安装依赖** - 修改 `requirements.txt` 后执行 `pip install -r requirements.txt`
2. **异常类型要准确** - `aiohttp.ClientTimeout` 是配置类，不是异常类
3. **启动前清理端口** - `lsof -ti:8000 | xargs kill -9`

---

## 验证

```bash
# 检查依赖
python3 -c "import aiohttp; print(aiohttp.__version__)"

# 清理端口
lsof -ti:8000 | xargs kill -9

# 重启
pnpm dev
```
