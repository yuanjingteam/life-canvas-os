# 营养师 Agent (Agentic RAG Pro) 软件设计文档 (SDD)

## 1. 引言

### 1.1 编写目的
本文档旨在为 `life-canvas-os` 项目中的高级营养师 Agent 提供技术架构指南。方案从传统的“检索增强生成 (RAG)”进化为**“智能代理 (Agentic)”架构**，通过集成高精度计算工具与时序动态画像能力，解决大模型在数值计算上的“幻觉”问题及对实时生理数据的感知滞后问题。

### 1.2 项目背景
在 2026 年的 AI 范式下，营养建议的专业性不再仅取决于知识库的广度，更取决于对用户实时体征（时序数据）的精准分析与计算。本方案通过引入 **Function Calling (工具调用)** 与 **Advanced RAG (高级检索)**，将 Agent 打造为一个具备“大脑（推理）”与“计算器（数学工具）”的专业闭环系统。*注：多模态感知（如拍照识餐）将作为后续迭代方向，本阶段暂不实现。*

### 1.3 核心目标
- **数值零幻觉**：通过 Python Math Tool 计算 BMI/TDEE 等核心指标，杜绝 LLM 直接生成数值。
- **时序动态干预**：基于用户近一周的体征波动（HealthLogs），实现策略的动态调整（如从减脂模式切换为恢复模式）。
- **专业知识赋能**：构建涵盖食物成分、膳食指南、临床营养学的专业向量知识库。

---

## 2. 需求分析

### 2.1 用户场景 (User Scenarios)
1. **趋势化营养指导**：用户询问“为什么我这周减重变慢了？”，Agent 调取近 7 天运动与摄入日志，进行趋势分析并给出原因。
2. **精准医疗避障**：用户声明有某种慢性病，Agent 在检索指南的同时，调用 SQL 数据库验证推荐食材的禁忌属性。
3. **日常饮食评估**：用户记录三餐，Agent 基于用户的减脂目标，分析营养摄入比例，并给出明天的饮食调整建议。

### 2.2 功能需求 (Functional Requirements)
1. **计算型工具集成 (Agentic Tools)**：
   - **Math Executor**：基于 Python 脚本精准计算 TDEE、营养缺口、合理摄入比例。
   - **Router 机制**：自动识别 Query 属性，将数值查询路由至 SQL，原则建议走 RAG。
2. **时序动态画像 (Temporal User Profile)**：
   - **HealthLogs 追踪**：记录体重、体脂、空腹血糖等随时间变化的序列数据。
   - **目标进度追踪**：根据近一周的数据波动动态调整当日推荐热量强度。
3. **专业营养知识检索（Advanced RAG）**：
   - 从营养学向量知识库中检索高度相关的文献、指南片段或食物数据。

### 2.3 非功能需求 (Non-functional Requirements)
1. **隐私安全 (Privacy & Local-First)**：
   - **本地化部署支持**：核心健康数据支持在本地 LLM（如 Llama 3 8B）处理，确保隐私不出本地。
   - **PII 脱敏**：在调用公网 API 前，自动剥离个人身份识别信息 (PII)。
2. **专业性与安全性**：所有建议必须符合主流营养学共识（如《中国居民膳食指南》），严禁给出有害健康的极端建议；必须包含标准免责声明。

---

## 3. 总体设计

### 3.1 增强型 Agent 业务架构
系统基于 **ReAct (Reasoning + Acting)** 框架构建：
- **感知层**：Schema 解析处理结构化日志，NLP 提取用户意图。
- **规划层**：负责任务拆解（Task Decomposition），判断是否需要调用计算工具或检索知识库。
- **工具层**：
  - **RAG Engine**：专业文献检索。
  - **Python Interpreter**：数学与逻辑计算。
  - **SQL Connector**：结构化食物成分库查询。

### 3.2 路由与任务流转 (Router Mechanism)
1. **Query 入口** -> **Router 决策**：
   - 属于“事实/数据查询” -> 路由至 **SQL Tool/Math Tool**。
   - 属于“原则/常识咨询” -> 路由至 **Advanced RAG**。
2. **多源信息融合** -> **Final Generator** 输出。

---

## 4. 详细设计

### 4.1 营养师知识库与高级检索 (Advanced RAG)
**4.1.1 检索策略优化**
- **Parent Document Retrieval (Small-to-Big)**：
  - 向量匹配使用 200 tokens 的子块提高检索精度；
  - 喂给 LLM 时召回其所在的 1000-1500 tokens 父级段落，确保指南的完整上下文。
- **混合检索 (Hybrid Search)**：
  - 参数配置：`alpha=0.6` (向量 0.6 + 关键字 0.4)。
  - 针对专业术语使用 BM25 算法进行精准增强。

**4.1.2 结果重排 (Reranking)**
- 使用 **Cross-Encoder (如 bge-reranker-v2-m3)** 对召回的 Top-20 文献进行二次打分，仅保留相关性 > 0.75 的核心片段。

### 4.2 时序动态画像模块 (Temporal Profile)
**4.2.1 增强型 Schema (Temporal User Profile)**
```json
{
  "static": {"gender": "female", "height": 165, "conditions": ["anemia"]},
  "temporal_logs": [
    {"date": "2026-04-01", "weight": 60.5, "steps": 8000, "kcal_in": 1800},
    {"date": "2026-04-05", "weight": 59.8, "steps": 12000, "kcal_in": 1650}
  ],
  "trends": {"weight_delta_7d": -0.7, "basal_metabolism_trend": "stable"},
  "pii_masking": {"mask_level": "high", "local_storage_only": true}
}
```

### 4.3 智能工具调用模块 (Agentic Tools)
Agent 必须在以下场景通过 **Function Calling** 调用原子工具：
- **Math_Tool (Python)**：
  - 场景：计算 TDEE、计算营养缺口。
  - 约束：LLM 禁止直接计算数值，必须生成 Python 代码并由后台沙箱执行，消除数值幻觉。
- **Diet_Router (Logical Router)**：
  - 场景：区分用户是在问“我能吃这个吗？”（查 RAG）还是“这个多少热量？”（查 SQL）。

### 4.4 建议生成逻辑 (Agentic Prompt)
```text
【角色】：资深注册营养师 Agentic Pro
【工具输出】：{{tool_outputs}} (包含 Python 计算出的精准 TDEE 与 SQL 查出的食物数据)
【检索背景】：{{rag_context}} (包含最新的膳食指南片段)
【用户时序状态】：{{health_logs}} (显示用户最近 3 天摄入超标)
【任务】：基于上述事实而非推测，为用户提供今日晚餐调整方案。
【约束】：数值必须引用工具输出，严禁私自估算。
```

---

## 5. 接口设计

### 5.1 增强型对话接口
**POST `/api/v1/agent/chat/pro`**
- **Request Body**:
  ```json
  {
    "session_id": "string",
    "query": "string",
    "user_id": "string"
  }
  ```
- **Response**: SSE Stream (包含计算过程、检索状态、最终建议)

---

## 6. 数据设计

### 6.1 向量库与时序库
- **向量库 (Qdrant/Chroma)**：存储分级营养指南，开启 **Sparse Vector** 支持。
- **关系库 (Postgres/SQLite)**：
  - `food_nutrients`：结构化食物成分库。
  - `user_health_logs`：存储时序体征数据（HealthLogs）。

---

## 7. 部署设计

1. **混合计算模式**：
   - **Edge Runtime**：运行 PII 脱敏脚本与本地 Llama 模型进行初步意图识别。
   - **Cloud Runtime**：运行高性能 RAG 检索与复杂推理。
2. **安全沙箱**：Python Math Tool 必须在独立的沙箱环境中运行，防止代码注入。

---

## 8. 测试设计

### 8.1 准确性回归测试
- **数值计算测试**：输入特定体征数据，验证 Agent 返回的 BMR/TDEE 数值是否与标准公式执行结果完全一致（误差需 < 0.1%）。
- **RAG 质量测试**：使用 RAGAs 评估 Faithfulness (忠实度) 和 Answer Relevance (回答相关度)。

---

## 9. 风险与应对措施

| 风险项 | 影响范围 | 应对措施 |
| --- | --- | --- |
| **数值幻觉** | 核心建议错误 | 强制使用 Math Tool；若工具调用失败，禁止给出具体数值，仅提供定性建议。 |
| **时序数据断裂** | 画像不准 | 增加“数据缺失提示”机制，引导用户补齐近 3 天体重信息。 |
| **隐私数据泄露** | 违反隐私法 | 实施 PII 扫描层；提供“本地私有化”部署开关，关闭云端同步。 |

---

## 10. 未来迭代方向：多模态感知 (Future Work)
在后续版本中，计划引入以下功能：
- **拍照识餐**：通过 Vision API 识别照片中的食材种类与分量。
- **营养标签识别**：通过 OCR 自动解析食品包装上的营养成分。
