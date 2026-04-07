# 营养师 Agent (Agentic RAG Pro) 测试驱动开发 (TDD) 文档

## 1. 引言
本文档定义了营养师 Agent 的技术测试用例与验证逻辑。本 TDD 方案遵循“测试先行”原则，涵盖单元测试 (Unit Tests)、集成测试 (Integration Tests) 以及针对 AI Agent 的特有评估指标 (AI Evaluation)。

## 2. 测试策略
- **单元测试 (Unit Tests)**：验证原子工具（如数学计算函数、SQL 构建器）的逻辑正确性。
- **集成测试 (Integration Tests)**：验证 Agent 编排流 (LangGraph/ReAct Flow) 的工具调用与状态流转。
- **RAG 评估 (RAGAs)**：针对检索片段的忠实度 (Faithfulness) 和回答的相关性 (Relevancy) 进行量化打分。
- **E2E 冒烟测试**：验证从 FastAPI 接口输入到 SSE 流式输出的完整链路。

---

## 3. 技术单元测试用例 (Unit Tests)

### 3.1 数学计算工具 (Math Executor)
**测试目标**：确保 Python 沙箱执行的公式无误。
- **Test ID**: `UT-MATH-001`
- **输入**: `{"gender": "male", "weight": 80, "height": 175, "age": 30, "activity": 1.55}`
- **预期输出**: `TDEE = 2650.5` (允许误差 ±0.1)
- **断言逻辑**: `assert math_tool.calculate_tdee(input) == 2650.5`

### 3.2 隐私脱敏中间件 (Privacy Redactor)
**测试目标**：验证 PII 信息在发送前被剔除。
- **Test ID**: `UT-PRIVACY-001`
- **输入**: `"你好，我是张三，我的邮箱是 zhangsan@example.com，我有轻度脂肪肝。"`
- **预期输出**: `"你好，我是 [USER]，我的邮箱是 [EMAIL]，我有轻度脂肪肝。"`
- **断言逻辑**: `assert privacy_gate.redact(input) does not contain "张三"`

---

## 4. 集成与逻辑测试用例 (Integration Tests)

### 4.1 路由决策逻辑 (Router Branching)
**测试目标**：验证 Router 是否正确分流。
- **Test ID**: `IT-ROUTER-001`
- **场景**: 用户提问 "100g 苹果有多少热量？"
- **预期路径**: 触发 `SQL_Connector` 而非 `RAG_Engine`。
- **验证手段**: 使用 LangSmith 追踪 Trace，检查 Tool 调用记录。

### 4.2 时序趋势感知 (Temporal Analysis)
**测试目标**：验证 Agent 是否根据 `HealthLogs` 调整建议。
- **Test ID**: `IT-TEMPORAL-001`
- **Mock 数据**: 过去 7 天体重下降 3.5kg (减重过快)。
- **用户 Query**: "我明天怎么吃？"
- **预期行为**: LLM 状态机识别到趋势异常，并在 Prompt 组装阶段自动加入 "增加能量摄入" 的上下文。
- **断言逻辑**: 最终建议 Markdown 中必须包含关键词 "减重过快" 或 "增加热量"。

---

## 5. RAG 专项评估用例 (RAGAs Metrics)

### 5.1 检索忠实度 (Faithfulness)
**测试目标**：生成的回答是否完全基于召回的 Context。
- **评估标准**: 分数需 > 0.85。
- **失败定义**: 如果生成的回答中出现了 Context 之外的生僻营养指标建议（幻觉）。

### 5.2 上下文精度 (Context Precision)
**测试目标**：召回的 Top-K 片段中，真正有用的片段比例。
- **评估标准**: 分数需 > 0.8。
- **验证方法**: 手动构建 Gold Dataset (问题-答案对)，运行 RAGAs 评估脚本。

---

## 6. 端到端测试 (E2E Tests)

### 6.1 流式输出完整性
**测试目标**：验证 SSE 接口的流式稳定性。
- **Test ID**: `E2E-SSE-001`
- **执行过程**:
  1. 调用 `/api/v1/agent/chat/pro`。
  2. 模拟长时间推理（包含一次 Math Tool 调用）。
  3. 检查 HTTP 状态码为 200，且 `content-type` 为 `text/event-stream`。
  4. 验证数据流中包含完整的 Markdown 结构。

---

## 7. 测试环境要求
- **Python**: `pytest`, `pytest-asyncio`, `pytest-mock`
- **AI 评估**: `ragas`, `langchain-smith`
- **Mock Server**: 使用 `unittest.mock` 模拟 Vector DB 的召回响应。

## 8. 持续集成 (CI) 触发阈值
- **代码覆盖率 (Coverage)**: 核心 Tool 逻辑需达 90%。
- **RAG 基准线**: 每次更新知识库后，必须通过 `Golden_Test_Set` 且 Faithfulness 分数不下降。
