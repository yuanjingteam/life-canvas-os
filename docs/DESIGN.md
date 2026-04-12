# Life Canvas OS 设计文档

> **⚠️ 重要提示：这是设计蓝图文档**
>
> 本文档描述了 Life Canvas OS 的**完整设计架构和规划功能**。
>
> **当前实现状态：**
> - 📊 整体完成度：约 **7-15%**
> - ✅ 已完成：Electron + React + Python 基础框架
> - 🔴 未完成：大部分业务逻辑和组件
>
> **文档用途：**
> - 作为开发的设计目标和参考蓝图
> - 指导后续功能开发的架构方向
> - 非实时反映当前代码状态
>
> **文档版本：** v3.0
> **最后更新：** 2026-02-03
> **审计日期：** 2026-02-05

---

## 一、项目概述

### 1.1 项目定位
Life Canvas OS 是一款基于 Electron + Python + SQLite 的桌面个人成长操作系统，通过八维生命平衡模型帮助用户可视化、管理和优化个人生活的各个方面。

### 1.2 核心理念
- **本地优先**：数据完全存储在本地，用户完全掌控自己的数据
- **系统化思维**：将生活抽象为8个可量化的子系统
- **数据驱动**：通过量化评分和趋势分析辅助决策
- **AI赋能**：利用大模型（支持 DeepSeek/豆包）提供个性化洞察和建议
- **极简美学**：借鉴 Notion/Linear 的设计语言，提供沉浸式体验

### 1.3 目标用户
- 追求自我提升和成长的个人用户
- 习惯量化自我（Quantified Self）的极客群体
- 需要系统化管理多维度生活的知识工作者
- 注重数据隐私和安全的用户

---

## 二、技术栈选择

### 2.1 前端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Electron | 39.2.6 | 桌面应用框架，跨平台支持 |
| React | 19.2.1 | UI 框架 |
| TypeScript | 5.9.3 | 类型安全 |
| Vite | 7.2.6 | 构建工具 |
| shadcn/ui | 最新 | UI 组件库（基于 Radix UI + Tailwind） |
| TailwindCSS | 4.1.17 | 原子化 CSS 引擎 |
| Recharts | 3.7.0 | 数据可视化（雷达图等） |
| Lucide React | 最新 | 图标库 |
| TanStack Query (React Query) | 5.90.20 | 服务端状态管理与缓存 |

**状态管理选择说明：**
- 使用 React Query 统一管理服务端状态和客户端状态
- 提供自动缓存、重试、失效策略
- 适合桌面应用的单一数据源模式

**shadcn/ui 选择理由：**
- 基于 Radix UI，无障碍访问性优秀
- 组件直接复制到项目中，完全可定制
- 与 TailwindCSS 深度集成，样式一致
- 提供 Button、Input、Modal、Toast、Select 等完整组件
- 设计风格极简，符合项目审美要求

### 2.2 后端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 后端服务 |
| FastAPI | 0.100+ | 高性能异步 API 框架（开发环境 HTTP，生产环境 IPC） |
| SQLAlchemy | 2.0+ | ORM |
| Python 标准库 sqlite3 | 内置 | SQLite 驱动（无需额外安装） |
| Pydantic | 2+ | 数据验证 |

**数据库管理策略：**
- 不使用 Alembic（桌面应用不需要复杂迁移）
- 首次启动使用 `Base.metadata.create_all()` 自动建表
- 版本升级时编写增量迁移脚本（按需执行）

### 2.3 AI 集成
用户可选择 2 个大模型提供商之一：
| 提供商 | 标识符 | 说明 |
|--------|--------|------|
| DeepSeek | deepseek | 主力推荐，性价比高，中文能力强 |
| 豆包 | doubao | 字节跳动出品，响应快速 |

**说明：**
- 用户只能配置一个 AI 提供商
- 可在设置页面随时切换
- API Key 使用 AES-256-GCM 加密存储在本地

### 2.4 数据存储
- **SQLite 3**：嵌入式数据库，存储所有用户数据
  - 无需独立数据库服务
  - 数据存储在用户数据目录
  - 支持事务、外键约束
  - 单用户场景性能完全满足需求
  - 数据完全本地化，用户完全掌控

### 2.5 开发工具
- **Biome 2.3.8**：代码格式化和检查（替代 ESLint + Prettier）
- pytest：Python 测试
- Vitest：前端测试
- electron-builder 26.0.12：应用打包
- tsx 4.21.0：TypeScript 执行

---

## 三、核心交互设计

### 3.1 信息架构

```
Life Canvas OS
├── 全局画布 (Canvas)
│   ├── 八维雷达图
│   ├── 子系统概览卡片
│   └── AI 摘要简报
├── 神经洞察 (Insights)
│   └── AI 分析报告卡片
├── 时间轴审计 (History)
│   └── 全系统历史日志时间轴
├── 八大子系统 (System Modules)
│   ├── 饮食系统 (FUEL)
│   ├── 运动系统 (PHYSICAL)
│   ├── 读书系统 (INTELLECTUAL)
│   ├── 工作系统 (OUTPUT)
│   ├── 梦想系统 (RECOVERY)
│   ├── 财务系统 (ASSET)
│   ├── 社交系统 (CONNECTION)
│   └── 环境系统 (ENVIRONMENT)
└── 内核配置 (Settings)
    ├── 用户档案
    │   ├── 基本信息（姓名、生日、MBTI 等）
    │   ├── 价值观设置
    │   └── 百岁目标
    ├── AI 配置
    │   ├── 提供商选择（DeepSeek/豆包 二选一）
    │   ├── API 密钥配置（加密存储）
    │   ├── 模型名称设置（可选，使用默认模型）
    │   └── API 连通性测试
    └── 数据管理
        ├── 数据导出（JSON/CSV）
        ├── 数据导入
        └── 数据清除（重置应用）
```

**AI 配置说明：**
- 用户从 2 个提供商中选择一个（DeepSeek/豆包）
- 每次只能使用一个提供商，切换时需重新配置 API Key
- 提供 API 测试功能，验证配置是否正确
- API Key 使用系统 Keychain + AES 加密存储

### 3.2 交互流程

#### 3.2.1 启动流程
```
用户启动应用
    ↓
Electron 主进程启动
    ↓
启动 Python 后端进程（子进程）
    ↓
Python 初始化 SQLite 数据库（首次运行）
    ↓
建立 IPC 通信通道
    ↓
检查是否已设置 PIN 码
    ↓
[首次使用] → 显示欢迎页 → 设置 PIN 码 → 输入基本信息
    ↓
[已设置 PIN] → 显示 PIN 解锁界面 → 验证 PIN → 进入应用
    ↓
加载用户配置和系统状态
    ↓
显示全局画布
```

**认证方案说明：**
- 采用 **PIN 码（6 位数字）** 替代复杂密码系统
- PIN 码使用 bcrypt 哈希存储在本地数据库
- 会话保持在内存中，应用锁定后需重新输入 PIN
- 可选：使用 SQLCipher 加密整个数据库（高安全模式）


#### 3.2.2 核心操作流

**评分更新流**
```
用户点击子系统卡片
    ↓
进入子系统详情页
    ↓
点击 +/- 按钮调整评分
    ↓
前端通过 IPC 调用 Python 后端
    ↓
Python 更新 SQLite 数据库
    ↓
返回更新后的数据
    ↓
前端实时更新 UI 和雷达图动画
```

**AI 洞察流**
```
用户点击「启动 AI 洞察」
    ↓
收集当前八维评分数据
    ↓
前端通过 IPC → Python 后端 → 大模型 API
    ↓
等待状态（加载动画）
    ↓
Python 解析大模型响应 → 验证数据
    ↓
存储到 SQLite insights 表
    ↓
通过 IPC 返回结构化数据
    ↓
前端渲染洞察卡片（庆祝/警告/行动）
```

**历史记录流**
```
用户在子系统页添加日志
    ↓
填写标签 + 描述 + 时间
    ↓
前端通过 IPC 提交到 Python 后端
    ↓
Python 存入 SQLite logs 表
    ↓
返回新日志数据
    ↓
前端实时更新历史列表
    ↓
时间轴审计页同步更新
```

### 3.3 关键交互细节

#### 3.3.1 雷达图交互
- **悬停**：显示具体维度名称和数值
- **点击**：跳转至对应子系统详情页
- **动画**：数据变化时平滑过渡（1s duration）

#### 3.3.2 子系统卡片
- **快速调整**：悬停时显示 +/- 按钮，点击直接调整评分
- **查看详情**：点击卡片主体进入详情页
- **状态指示**：评分颜色编码（>80 绿色，50-80 橙色，<50 红色）

#### 3.3.3 AI 洞察卡片
- **类型区分**：
  - 庆祝型（celebration）：绿色，Trophy 图标
  - 警告型（warning）：红色，AlertCircle 图标
  - 行动型（action）：蓝色，Zap 图标
- **交互**：点击可展开/折叠详细建议

#### 3.3.4 响应式布局
- 侧边栏：固定 320px 宽度
- 主内容区：自适应，最大宽度 1400px
- 网格系统：基于 Tailwind 的 12 列网格

---

## 四、模块划分

### 4.1 整体架构（安全方案）

```
┌────────────────────────────────────────────────────────────────┐
│                     Electron Main Process                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Python Backend (FastAPI)                    │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │  │
│  │  │   API      │  │    AI      │  │   SQLite DB      │   │  │
│  │  │  Router    │  │  Service   │  │   (本地文件)      │   │  │
│  │  └────────────┘  └────────────┘  └──────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↕ IPC (进程间通信)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            IPC Bridge (python-bridge)                    │  │
│  │   将 FastAPI 调用转换为 IPC 消息，不暴露 HTTP 端口         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
                           ↕ IPC (安全通道)
┌────────────────────────────────────────────────────────────────┐
│                    Electron Renderer                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              React Frontend                               │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────────────────────┐  │  │
│  │  │  Views  │  │Components│  │   IPC Client Layer      │  │  │
│  │  └─────────┘  └─────────┘  └─────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

**安全架构说明：**
- Python 后端与 Electron 通过 **IPC 通信**，不启动 HTTP 服务器
- 消除端口冲突风险
- 消除 CSRF 攻击面（恶意网页无法访问 IPC 通道）
- 进程间通信通过 Electron 的 `ipcMain` 和 `ipcRenderer` 进行
- Python 后端通过 **stdin/stdout** 与 Electron 主进程通信

### 4.2 前端模块 (Electron + React)

#### 4.2.1 实际项目结构

> **注意：** 以下是当前实际的项目结构。许多业务模块仍在开发中。

```
src/
├── main/                   # Electron 主进程
│   ├── index.ts           # 主进程入口
│   ├── python/            # Python 后端管理
│   │   └── manager.ts     # Python 进程管理器
│   └── windows/           # 窗口管理
│       └── main.ts        # 主窗口定义
├── preload/               # 预加载脚本
│   └── index.ts
├── renderer/              # 渲染进程（前端）
│   ├── components/        # React 组件
│   │   ├── ui/           # UI 基础组件
│   │   │   └── alert.tsx # Alert 组件示例
│   │   ├── canvas/       # 画布组件（待开发）
│   │   ├── insights/     # AI 洞察组件（待开发）
│   │   └── system/       # 系统组件（待开发）
│   ├── hooks/            # React Hooks（待开发）
│   ├── lib/              # 工具库
│   │   └── utils.ts      # 工具函数
│   ├── pages/            # 页面组件（待开发）
│   ├── queries/          # TanStack Query（待开发）
│   ├── screens/          # 屏幕组件（待开发）
│   ├── index.html        # 入口 HTML
│   ├── index.tsx         # 入口 React
│   └── routes.tsx        # 路由配置
├── shared/                # 共享模块
│   ├── constants.ts      # 常量定义
│   ├── types.ts          # TypeScript 类型
│   └── utils.ts          # 共享工具函数
├── lib/electron-app/      # Electron 应用工具
│   ├── factories/        # 工厂模式
│   ├── utils/            # 工具函数
│   ├── extensions/       # 扩展
│   └── release/          # 发布相关
└── resources/             # 资源文件
```

#### 4.2.2 规划中的页面模块 (`/src/renderer/pages`)

```
pages/
├── CanvasPage.tsx          # 全局画布主页（待开发）
├── InsightsPage.tsx        # AI 洞察页（待开发）
├── HistoryPage.tsx         # 时间轴审计页（待开发）
├── SystemDetailPage.tsx    # 子系统详情页（待开发）
└── SettingsPage.tsx        # 设置页（待开发）
```

#### 4.2.3 规划中的组件模块 (`/src/renderer/components`)

> **注意：** 以下是规划中的组件结构，当前只有 `ui/alert.tsx` 存在。

```
components/
├── ui/                     # shadcn/ui 组件（部分开发中）
│   ├── alert.tsx          # ✅ 已实现
│   ├── button.tsx         # 待开发
│   ├── input.tsx          # 待开发
│   ├── select.tsx         # 待开发
│   ├── dialog.tsx         # 待开发
│   ├── toast.tsx          # 待开发
│   └── ...
├── layout/                 # 布局组件（待开发）
│   ├── Sidebar.tsx        # 侧边导航栏
│   └── Header.tsx         # 顶部状态栏
├── canvas/                 # 画布组件（待开发）
│   ├── RadarChart.tsx     # 雷达图组件
│   ├── SystemCard.tsx     # 系统概览卡片
│   └── AIBriefing.tsx     # AI 摘要简报
├── system/                 # 子系统组件（待开发）
│   ├── DietTracker.tsx    # 饮食追踪器
│   ├── PhysicalTracker.tsx # 运动追踪器
│   ├── IntellectualSystem.tsx # 读书系统
│   ├── OutputSystem.tsx   # 工作产出系统
│   ├── RecoveryHub.tsx    # 梦想清单
│   ├── FinanceDashboard.tsx # 财务仪表盘
│   ├── SocialEnergy.tsx   # 社交能量
│   └── EnvironmentManager.tsx # 环境管理
├── insights/               # AI 洞察组件（待开发）
│   └── InsightCard.tsx    # 洞察卡片
├── history/                # 历史记录组件（待开发）
│   └── TimelineLog.tsx    # 时间轴日志
└── auth/                   # 认证组件（待开发）
    └── AuthForm.tsx       # 认证表单
```

#### 4.2.4 规划中的状态管理 (`/src/renderer/queries`)

> **注意：** TanStack Query 集成待开发。

```
queries/
├── useSystems.ts           # 系统数据查询（待开发）
├── useInsights.ts          # AI 洞察查询（待开发）
├── useLogs.ts              # 系统日志查询（待开发）
├── useJournal.ts           # 用户日记查询（待开发）
├── useUser.ts              # 用户配置查询（待开发）
└── mutations.ts            # 修改操作（待开发）
```

**React Query 使用模式：**
```typescript
// 示例：使用 React Query 管理系统数据
const { data: systems, isLoading } = useQuery({
  queryKey: ['systems'],
  queryFn: () => ipcClient.invoke('get_systems')
});

const updateScore = useMutation({
  mutationFn: ({ id, score }) => ipcClient.invoke('update_system_score', { id, score }),
  onSuccess: () => queryClient.invalidateQueries(['systems'])
});
```

#### 4.2.5 规划中的 Hooks (`/src/renderer/hooks`)

> **注意：** 自定义 Hooks 待开发。

```
hooks/
├── useIPC.ts               # IPC 通信封装（待开发）
├── usePinLock.ts           # PIN 锁定状态管理（待开发）
└── useDatabaseHealth.ts    # 数据库健康监控（待开发）
```

#### 4.2.6 规划中的 IPC 层

> **注意：** IPC 客户端层待开发，目前通信逻辑可能在主进程中实现。

```
# 规划中的结构
src/renderer/ipc/           # IPC 客户端层（待开发）
├── client.ts               # IPC 客户端封装
├── channels.ts             # 通道名称常量
└── types.ts                # IPC 消息类型定义

# 当前实现位置
src/main/python/manager.ts  # Python 进程管理（包含 IPC 通信逻辑）
```

### 4.3 后端模块 (Python + FastAPI)

#### 4.3.1 实际项目结构

> **注意：** 以下是当前实际的后端结构。许多业务模块仍在开发中。

```
backend/
├── main.py                 # ✅ 应用入口
├── api/                    # API 路由模块（待开发）
│   ├── __init__.py         # ✅ 包初始化文件
│   ├── test.py             # ✅ 测试文件
│   ├── pin.py              # ❌ PIN 认证 API（待开发）
│   ├── system.py           # ❌ 系统数据 API（待开发）
│   ├── insight.py          # ❌ AI 洞察 API（待开发）
│   ├── log.py              # ❌ 系统日志 API（待开发）
│   ├── journal.py          # ❌ 用户日记 API（待开发）
│   ├── ai_config.py        # ❌ AI 配置 API（待开发）
│   └── user.py             # ❌ 用户配置 API（待开发）
├── core/                   # 核心逻辑模块
│   ├── __init__.py         # ✅ 包初始化文件
│   ├── health.py           # ✅ 健康检查模块
│   ├── security.py         # ❌ 安全模块（待开发）
│   ├── database.py         # ❌ 数据库连接（待开发）
│   └── config.py           # ❌ 配置管理（待开发）
├── models/                 # 数据模型（待开发）
│   ├── __init__.py         # ✅ 包初始化文件
│   ├── user.py             # ❌ 用户模型
│   ├── system.py           # ❌ 系统模型
│   ├── log.py              # ❌ 日志模型
│   └── journal.py          # ❌ 日记模型
├── schemas/                # Pydantic Schema（待开发）
│   ├── __init__.py         # ✅ 包初始化文件
│   ├── user.py             # ❌ 用户 Schema
│   ├── system.py           # ❌ 系统 Schema
│   ├── insight.py          # ❌ 洞察 Schema
│   ├── log.py              # ❌ 日志 Schema
│   ├── journal.py          # ❌ 日记 Schema
│   └── ai_config.py        # ❌ AI 配置 Schema
├── services/               # 业务服务（待开发）
│   ├── __init__.py         # ✅ 包初始化文件
│   ├── ai_service.py       # ❌ AI 服务
│   ├── insight_service.py  # ❌ 洞察服务
│   ├── encryption_service.py # ❌ 加密服务
│   └── system_service.py   # ❌ 系统服务
├── db/                     # 数据库模块（待开发）
│   ├── __init__.py         # ✅ 包初始化文件
│   ├── session.py          # ❌ 数据库会话
│   └── init_db.py          # ❌ 初始化脚本
├── build/                  # PyInstaller 打包输出
│   └── backend/            # 打包后的可执行文件
└── dist/                   # 构建产物
```

#### 4.3.2 双模式通信架构

**开发环境 vs 生产环境：**

| 环境 | 通信方式 | 优势 | 使用场景 |
|------|----------|------|----------|
| 开发环境 | HTTP (localhost:8000) | 可直接用 Postman/curl 测试，调试方便 | 本地开发 |
| 生产环境 | IPC (stdin/stdout) | 无端口冲突，无 CSRF 风险 | 打包后应用 |

**启动模式：**
```bash
# 开发模式：启动 HTTP 服务器
python main.py --dev

# 生产模式：IPC 通信（Electron 调用）
python main.py
```

---

#### 4.3.3 IPC 通信协议（生产模式）

**请求格式（Electron → Python）：**
```json
{
  "id": "unique-request-id",
  "action": "update_system_score",
  "params": { "system_id": "FUEL", "delta": 5 }
}
```

**响应格式（Python → Electron）：**
```json
{
  "id": "unique-request-id",
  "success": true,
  "data": { "new_score": 85 }
}
```

**协议说明：**
- 不再模拟 HTTP 路由，使用直接函数调用
- `action` 对应 Python 后端的处理函数
- `params` 为函数参数
- 添加长度前缀解决粘包问题：`[JSON长度]\n[JSON内容]`

#### 4.3.4 Action 列表（开发环境 HTTP + 生产环境 IPC）

**PIN 认证模块**
| Action | HTTP 端点 | 描述 |
|--------|-----------|------|
| setup_pin | POST /api/pin/setup | 首次设置 PIN |
| verify_pin | POST /api/pin/verify | 验证 PIN 解锁 |
| change_pin | POST /api/pin/change | 修改 PIN |
| lock_app | POST /api/pin/lock | 锁定应用 |

**系统数据模块**
| Action | HTTP 端点 | 描述 |
|--------|-----------|------|
| get_systems | GET /api/systems | 获取所有系统状态 |
| get_system | GET /api/systems/{system_id} | 获取单个系统详情 |
| update_system_score | PATCH /api/systems/{system_id}/score | 更新系统评分 |
| update_system_stats | PATCH /api/systems/{system_id}/stats | 更新系统统计数据 |
| get_system_logs | GET /api/systems/{system_id}/logs | 获取系统日志 |

**AI 洞察模块**
| Action | HTTP 端点 | 描述 |
|--------|-----------|------|
| generate_insights | POST /api/insights/generate | 生成 AI 洞察报告 |
| get_insights_history | GET /api/insights/history | 获取历史洞察记录 |

**日志模块**
| Action | HTTP 端点 | 描述 |
|--------|-----------|------|
| add_log | POST /api/logs | 添加新日志 |
| get_logs | GET /api/logs | 获取日志列表（支持分页、筛选） |
| delete_log | DELETE /api/logs/{log_id} | 删除日志 |

**用户配置模块**
| Action | HTTP 端点 | 描述 |
|--------|-----------|------|
| get_user_config | GET /api/user/config | 获取用户配置 |
| update_user_config | PATCH /api/user/config | 更新用户配置（含基本信息） |

**AI 配置模块（简化：单一配置）**
| Action | HTTP 端点 | 描述 |
|--------|-----------|------|
| get_ai_config | GET /api/ai/config | 获取当前 AI 配置 |
| update_ai_config | PUT /api/ai/config | 更新 AI 配置（提供商 + API Key） |
| test_ai_config | POST /api/ai/config/test | 测试 API 连通性 |

**用户日记模块（新增）**
| Action | HTTP 端点 | 描述 |
|--------|-----------|------|
| get_journals | GET /api/journal | 获取日记列表（支持分页、筛选） |
| get_journal | GET /api/journal/{id} | 获取单条日记详情 |
| create_journal | POST /api/journal | 创建新日记 |
| update_journal | PUT /api/journal/{id} | 更新日记 |
| delete_journal | DELETE /api/journal/{id} | 删除日记 |
| get_journal_stats | GET /api/journal/stats | 获取日记统计（按心情、日期分组） |

**健康检查模块**
| Action | HTTP 端点 | 描述 |
|--------|-----------|------|
| health | GET /api/health | 健康检查（IPC 心跳用） |
| ping | GET /api/ping | Ping 检查 |

### 4.4 数据库设计（SQLite）

#### 4.4.1 数据库位置
```
macOS:  ~/Library/Application Support/Life Canvas OS/data.db
Windows: %APPDATA%/Life Canvas OS/data.db
Linux:  ~/.config/Life Canvas OS/data.db
```

#### 4.4.2 ER 图

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│user_profile  │         │user_settings │         │ ai_config    │
├──────────────┤         ├──────────────┤         ├──────────────┤
│ id (PK)      │    ┌───▶│ id (PK)      │         │ user_id (PK) │
│ pin_hash     │    │    │ theme        │         │ provider     │
│ display_name │    │    │ language     │         │ api_key_enc  │
│ birthday     │    │    │ auto_save... │         │ model_name   │
│ mbti         │    │    │ sync_enabled │         │ created_at   │
│ values       │    │    │ ...          │         │ updated_at   │
│ ...          │    │    └──────────────┘         └──────────────┘
└──────────────┘    │
                    │
         ┌───────────┴──────────┬─────────────────┬─────────────────┐
         │                    │                 │                 │
┌──────────────┐      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│systems_base  │      │user_journal  │  │   insights    │  │action_items  │
├──────────────┤      ├──────────────┤  ├──────────────┤  ├──────────────┤
│ id (PK)      │      │ id (PK)      │  │ id (PK)      │  │ id (PK)      │
│ user_id (FK) │      │ user_id (FK) │  │ user_id (FK) │  │ system_id... │
│ type         │      │ title        │  │ content      │  │ text         │
│ score        │      │ content      │  │ system_scores│  │ completed    │
│ ...          │      │ mood         │  │ generated_at │  │ created_at   │
└──────────────┘      │ tags         │  │ created_at   │  └──────────────┘
       │              │ created_at   │  └──────────────┘
       │              └──────────────┘
       │
   ┌───┴──────────────────────┬──────────────────┬─────────────────┐
   │                          │                  │                 │
┌──────────────┐      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│systems_fuel  │      │systems_physi..│  │systems_intel.│  │systems_out.. │
├──────────────┤      ├──────────────┤  ├──────────────┤  ├──────────────┤
│ system_id    │      │ system_id    │  │ system_id    │  │ system_id    │
│ consistency  │      │ maintenance..│  │ total_sparks │  │ focus_hours..│
│ baseline_... │      │ weekly_plan  │  │ current_book │  │ tasks_compl..│
│ last_devia...│      │ progress     │  │ reading_prog │  │ current_okr  │
└──────────────┘      └──────────────┘  └──────────────┘  └──────────────┘

┌──────────────┐      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│systems_recov.│      │systems_asset │  │systems_conne.│  │systems_envir.│
├──────────────┤      ├──────────────┤  ├──────────────┤  ├──────────────┤
│ system_id    │      │ system_id    │  │ system_id    │  │ system_id    │
│ total_dreams │      │ monthly_inc..│  │ social_energy│  │ spaces_json  │
│ realized_... │      │ net_worth    │  │ total_friend │  │ inventory_...│
│ dreams_json  │      │ assets_json  │  │ friends_json │  │ overdue_task │
└──────────────┘      │ liabilities..│  └──────────────┘  │ next_maint...│
                      └──────────────┘                     └──────────────┘

         ┌──────────────┐
         │     logs     │
         ├──────────────┤
         │ id (PK)      │
         │ system_id(FK)│
         │ label        │
         │ value        │
         │ timestamp    │
         │ metadata     │
         └──────────────┘
```

**表关系说明：**
- `user_profile` 和 `user_settings` 是一对一关系
- `systems_base` 是所有子系统的公共字段表
- 8 个 `systems_*` 表通过 `system_id` 关联到 `systems_base`
- `logs` 和 `action_items` 通过 `system_id` 关联到 `systems_base`

#### 4.4.3 表结构定义（SQLite DDL）

##### 用户相关表

**user_profile 表（用户身份信息）**
```sql
CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT CHECK(id = 1),  -- 用户唯一标识，单用户应用固定为1
    pin_hash TEXT NOT NULL,                              -- bcrypt 哈希的6位PIN码，空字符串表示未设置
    display_name TEXT NOT NULL DEFAULT 'User',           -- 用户显示名称
    birthday DATE,                                       -- 出生日期，格式 YYYY-MM-DD，用于计算生命进度
    mbti TEXT,                                           -- MBTI性格类型，16种类型之一
    values TEXT,                                         -- 价值观，JSON数组格式，如'["自由","创造力","成长"]'
    life_expectancy INTEGER DEFAULT 85,                  -- 百岁目标，默认85岁，用于生命倒计时
    locked_at TIMESTAMP,                                 -- 应用锁定时间戳，用于自动锁定功能
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 记录创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP       -- 记录最后更新时间
);

-- 初始化默认用户
INSERT INTO user_profile (id, pin_hash, display_name) VALUES (1, '', 'User');
```

**user_settings 表（用户配置信息）**
```sql
CREATE TABLE user_settings (
    user_id INTEGER PRIMARY KEY DEFAULT 1,               -- 关联用户ID，固定为1
    theme TEXT DEFAULT 'light',                           -- 主题设置：light=亮色, dark=暗色, auto=跟随系统
    language TEXT DEFAULT 'zh-CN',                        -- 界面语言，默认简体中文
    auto_save_enabled INTEGER DEFAULT 1,                  -- 自动保存开关，1=启用, 0=禁用
    auto_save_interval INTEGER DEFAULT 60,                -- 自动保存间隔（秒），默认60秒
    notification_enabled INTEGER DEFAULT 1,              -- 通知开关，是否启用系统通知
    notification_time TEXT DEFAULT '09:00',               -- 每日提醒时间
    show_year_progress INTEGER DEFAULT 1,                 -- 是否显示年度进度条
    show_weekday INTEGER DEFAULT 1,                       -- 是否显示星期几
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 配置创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 配置更新时间
    FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
);

-- 初始化默认设置
INSERT INTO user_settings (user_id) VALUES (1);
```

**ai_config 表（AI配置，简化为单一配置）**
```sql
CREATE TABLE ai_config (
    user_id INTEGER PRIMARY KEY DEFAULT 1,               -- 关联用户ID，固定为1
    provider TEXT NOT NULL CHECK(provider IN ('deepseek', 'doubao')),  -- AI提供商
    api_key_enc TEXT NOT NULL,                           -- AES-256-GCM加密的API密钥
    model_name TEXT,                                     -- 可选：自定义模型名称，为空使用默认模型
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 配置创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 配置更新时间
    FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
);

-- 提供商默认模型配置
-- deepseek: deepseek-chat
-- doubao: Doubao-pro-256k
```

##### 用户日记表

**user_journal 表（用户日记/日志）**
```sql
CREATE TABLE user_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                -- 日记唯一标识
    user_id INTEGER NOT NULL DEFAULT 1,                  -- 关联用户ID
    title TEXT NOT NULL,                                 -- 日记标题，简短描述
    content TEXT NOT NULL,                               -- 日记正文内容，支持长文本
    mood TEXT CHECK(mood IN ('great', 'good', 'neutral', 'bad', 'terrible')),  -- 当时心情：great=很好, good=好, neutral=一般, bad=差, terrible=很差
    tags TEXT,                                          -- 标签，JSON数组格式，如'["工作","突破","AI"]'
    related_system TEXT CHECK(related_system IN ('FUEL', 'PHYSICAL', 'INTELLECTUAL', 'OUTPUT', 'RECOVERY', 'ASSET', 'CONNECTION', 'ENVIRONMENT', NULL)),  -- 关联的系统，可选
    is_private INTEGER DEFAULT 1,                        -- 是否私密，1=私密(不同步), 0=公开(未来可能支持分享)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 日记创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 日记最后更新时间
    FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
);

CREATE INDEX idx_journal_created ON user_journal(created_at DESC);    -- 按创建时间降序索引，用于时间线查询
CREATE INDEX idx_journal_mood ON user_journal(mood);                 -- 按心情索引，用于统计分析
CREATE INDEX idx_journal_tags ON user_journal(tags);                 -- 按标签索引，用于标签搜索
```

##### 子系统相关表

**systems_base 表（子系统公共字段）**
```sql
CREATE TABLE systems_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                -- 系统唯一标识
    user_id INTEGER NOT NULL DEFAULT 1,                  -- 关联用户ID
    type TEXT NOT NULL CHECK(type IN ('FUEL', 'PHYSICAL', 'INTELLECTUAL',  -- 系统类型枚举
                                      'OUTPUT', 'RECOVERY', 'ASSET',
                                      'CONNECTION', 'ENVIRONMENT')),
    score INTEGER DEFAULT 50 CHECK(score BETWEEN 0 AND 100),  -- 系统评分，范围0-100
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 系统创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 系统更新时间
    UNIQUE(user_id, type),                               -- 同一用户每种系统类型只能有一条记录
    FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
);

CREATE INDEX idx_systems_base_user_type ON systems_base(user_id, type);  -- 用户+类型组合索引
```

**systems_fuel 表（饮食系统专属字段）**
```sql
CREATE TABLE systems_fuel (
    system_id INTEGER PRIMARY KEY,                       -- 关联systems_base.id
    consistency INTEGER DEFAULT 0 CHECK(consistency BETWEEN 0 AND 100),  -- 一致性评分，与基准的符合程度
    baseline_breakfast TEXT,                            -- 早餐基准配置，JSON格式
    baseline_lunch TEXT,                                -- 午餐基准配置，JSON格式
    baseline_dinner TEXT,                               -- 晚餐基准配置，JSON格式
    baseline_snacks TEXT,                               -- 零食基准配置，JSON格式，如'{"enabled":false}'
    last_deviation TEXT,                                -- 最近偏离记录，JSON格式
    FOREIGN KEY (system_id) REFERENCES systems_base(id) ON DELETE CASCADE
);
```

**systems_physical 表（运动系统专属字段）**
```sql
CREATE TABLE systems_physical (
    system_id INTEGER PRIMARY KEY,                       -- 关联systems_base.id
    maintenance_index INTEGER DEFAULT 0 CHECK(maintenance_index BETWEEN 0 AND 100),  -- 维护指数
    weekly_plan TEXT,                                   -- 本周运动计划，JSON数组
    weekly_progress INTEGER DEFAULT 0 CHECK(weekly_progress BETWEEN 0 AND 100),  -- 本周完成进度
    last_workout_at TIMESTAMP,                          -- 最后运动时间
    total_workout_hours REAL DEFAULT 0,                 -- 累计运动小时数，保留1位小数
    FOREIGN KEY (system_id) REFERENCES systems_base(id) ON DELETE CASCADE
);
```

**systems_intellectual 表（读书系统专属字段）**
```sql
CREATE TABLE systems_intellectual (
    system_id INTEGER PRIMARY KEY,                       -- 关联systems_base.id
    total_sparks INTEGER DEFAULT 0,                      -- 累计思想火花数量（摘录、笔记数）
    current_book_id TEXT,                               -- 当前阅读书籍的唯一标识
    reading_progress INTEGER DEFAULT 0 CHECK(reading_progress BETWEEN 0 AND 100),  -- 当前阅读进度百分比
    last_read_at TIMESTAMP,                             -- 最后阅读时间
    books_json TEXT,                                    -- 书籍列表，JSON数组格式
    FOREIGN KEY (system_id) REFERENCES systems_base(id) ON DELETE CASCADE
);
```

**systems_output 表（工作系统专属字段）**
```sql
CREATE TABLE systems_output (
    system_id INTEGER PRIMARY KEY,                       -- 关联systems_base.id
    focus_hours_today REAL DEFAULT 0,                   -- 今日专注小时数
    focus_hours_week REAL DEFAULT 0,                    -- 本周专注小时数
    tasks_completed_today INTEGER DEFAULT 0,            -- 今日完成任务数
    current_okr TEXT,                                   -- 当前OKR目标，JSON格式
    FOREIGN KEY (system_id) REFERENCES systems_base(id) ON DELETE CASCADE
);
```

**systems_recovery 表（梦想系统专属字段）**
```sql
CREATE TABLE systems_recovery (
    system_id INTEGER PRIMARY KEY,                       -- 关联systems_base.id
    total_dreams INTEGER DEFAULT 0,                      -- 总梦想数量
    realized_dreams INTEGER DEFAULT 0,                   -- 已实现梦想数量
    progress_percentage REAL DEFAULT 0,                 -- 完成百分比，保留2位小数
    dreams_json TEXT,                                   -- 梦想列表，JSON数组格式
    FOREIGN KEY (system_id) REFERENCES systems_base(id) ON DELETE CASCADE
);
```

**systems_asset 表（财务系统专属字段）**
```sql
CREATE TABLE systems_asset (
    system_id INTEGER PRIMARY KEY,                       -- 关联systems_base.id
    monthly_income REAL DEFAULT 0,                       -- 月收入，单位：元
    base_net_worth REAL DEFAULT 0,                      -- 基础净资产，单位：元
    current_net_worth REAL DEFAULT 0,                   -- 当前净资产，单位：元
    assets_json TEXT,                                   -- 资产明细，JSON格式
    liabilities_json TEXT,                              -- 负债明细，JSON格式
    last_sync_at TIMESTAMP,                             -- 最后同步时间
    FOREIGN KEY (system_id) REFERENCES systems_base(id) ON DELETE CASCADE
);
```

**systems_connection 表（社交系统专属字段）**
```sql
CREATE TABLE systems_connection (
    system_id INTEGER PRIMARY KEY,                       -- 关联systems_base.id
    social_energy INTEGER DEFAULT 50 CHECK(social_energy BETWEEN 0 AND 100),  -- 社交能量值
    total_friends INTEGER DEFAULT 0,                     -- 好友总数
    close_friends INTEGER DEFAULT 0,                     -- 密友数量
    last_interaction_at TIMESTAMP,                      -- 最后社交时间
    friends_json TEXT,                                  -- 好友列表，JSON数组格式
    FOREIGN KEY (system_id) REFERENCES systems_base(id) ON DELETE CASCADE
);
```

**systems_environment 表（环境系统专属字段）**
```sql
CREATE TABLE systems_environment (
    system_id INTEGER PRIMARY KEY,                       -- 关联systems_base.id
    spaces_json TEXT,                                   -- 空间维护计划列表，JSON数组格式
    inventory_json TEXT,                                -- 物品清单，JSON数组格式
    overdue_tasks INTEGER DEFAULT 0,                     -- 逾期维护任务数
    next_maintenance_at TIMESTAMP,                      -- 下次维护时间
    FOREIGN KEY (system_id) REFERENCES systems_base(id) ON DELETE CASCADE
);
```

##### 系统日志与行动项表

**logs 表（系统日志）**
```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                -- 日志唯一标识
    system_id INTEGER NOT NULL,                          -- 关联systems_base.id
    label TEXT NOT NULL,                                 -- 日志标签，简短分类
    value TEXT,                                         -- 日志详细内容
    metadata TEXT,                                      -- 额外元数据，JSON格式
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 日志创建时间
    FOREIGN KEY (system_id) REFERENCES systems_base(id) ON DELETE CASCADE
);

CREATE INDEX idx_logs_system_created ON logs(system_id, created_at DESC);  -- 系统ID+时间降序索引
```

**action_items 表（行动项/里程碑）**
```sql
CREATE TABLE action_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                -- 行动项唯一标识
    system_id INTEGER NOT NULL,                          -- 关联systems_base.id
    text TEXT NOT NULL,                                  -- 行动项/里程碑描述
    completed INTEGER DEFAULT 0 CHECK(completed IN (0, 1)),  -- 完成状态，0=未完成, 1=已完成
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 创建时间
    FOREIGN KEY (system_id) REFERENCES systems_base(id) ON DELETE CASCADE
);

CREATE INDEX idx_action_items_system_completed ON action_items(system_id, completed);  -- 系统ID+完成状态索引
```

##### AI 洞察表

**insights 表（AI生成的洞察报告）**
```sql
CREATE TABLE insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                -- 洞察报告唯一标识
    user_id INTEGER NOT NULL DEFAULT 1,                  -- 关联用户ID
    content TEXT NOT NULL,                               -- 洞察内容，JSON数组格式，包含多条洞察
    system_scores TEXT,                                 -- 生成时的系统评分快照，JSON格式
    provider_used TEXT,                                 -- 使用的AI提供商
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 生成时间
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      -- 记录创建时间
    FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
);

CREATE INDEX idx_insights_user_generated ON insights(user_id, generated_at DESC);  -- 用户+生成时间降序索引
```

#### 4.4.4 数据库查询示例

**获取某个子系统的完整信息（公共字段 + 专属字段）：**
```sql
-- 获取饮食系统完整信息
SELECT b.*, f.*
FROM systems_base b
LEFT JOIN systems_fuel f ON f.system_id = b.id
WHERE b.type = 'FUEL' AND b.user_id = 1;

-- 获取运动系统完整信息
SELECT b.*, p.*
FROM systems_base b
LEFT JOIN systems_physical p ON p.system_id = b.id
WHERE b.type = 'PHYSICAL' AND b.user_id = 1;
```

**获取所有系统及其评分（用于雷达图）：**
```sql
SELECT type, score
FROM systems_base
WHERE user_id = 1
ORDER BY type;
```

**用户日记统计查询：**
```sql
-- 按心情统计日记数量
SELECT mood, COUNT(*) as count
FROM user_journal
WHERE user_id = 1
GROUP BY mood;

-- 获取最近的日记
SELECT id, title, mood, tags, created_at
FROM user_journal
WHERE user_id = 1
ORDER BY created_at DESC
LIMIT 20;
```

#### 4.4.5 SQLite 配置与加密

**Python SQLAlchemy 配置：**
```python
# backend/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys
from pathlib import Path

# 获取用户数据目录
if os.name == 'nt':  # Windows
    DATA_DIR = Path(os.environ['APPDATA']) / 'Life Canvas OS'
elif os.name == 'posix':  # macOS / Linux
    if sys.platform == 'darwin':
        DATA_DIR = Path.home() / 'Library' / 'Application Support' / 'Life Canvas OS'
    else:
        DATA_DIR = Path.home() / '.config' / 'life-canvas-os'

DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / 'data.db'

# SQLite 连接字符串
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 多线程必需
    echo=False  # 生产环境设为 False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**API Key 加密方案：**
- **加密算法**：AES-256-GCM
- **密钥管理**：
  - macOS: Keychain Services
  - Windows: Credential Manager
  - Linux: libsecret / Secret Service API
- **加密流程**：
  1. 首次配置时生成随机主密钥（256-bit）
  2. 主密钥存储到系统 Keychain
  3. API Key 使用主密钥加密后存储到 SQLite
  4. 使用时从 Keychain 读取主密钥解密

### 4.5 Electron 主进程模块

#### 4.5.1 实际项目结构

> **注意：** 以下是当前实际的主进程结构。

```
main/
├── index.ts                # ✅ 主进程入口
├── python/                 # Python 后端管理
│   └── manager.ts          # ✅ Python 进程管理器
└── windows/                # 窗口管理
    └── main.ts             # ✅ 主窗口定义
```

#### 4.5.2 规划中的模块

> **注意：** 以下模块在规划中，待开发。

```
main/
├── ipc/                    # IPC 处理器（待开发）
│   ├── index.ts            # IPC 处理器注册
│   ├── handlers/
│   │   ├── system.ts       # 系统相关 IPC
│   │   └── database.ts     # 数据库操作 IPC
│   └── channels.ts         # 通道名称常量
├── python/
│   ├── manager.ts          # ✅ 已实现
│   ├── bridge.ts           # IPC 与 Python 通信桥接（待开发）
│   └── monitor.ts          # 后端健康监控（待开发）
└── menu.ts                 # 应用菜单配置（待开发）
```

#### 4.5.1 Python 进程启动与通信

**Electron 端：带健康检查的进程管理**
```typescript
// main/python/manager.ts
import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import EventEmitter from 'events';

export class PythonManager extends EventEmitter {
  private process: ChildProcess | null = null;
  private healthCheckTimer?: NodeJS.Timeout;
  private responseCallbacks = new Map<string, (response: any) => void>();
  private stdoutBuffer = '';
  public isReady = false;

  start() {
    const isDev = process.env.NODE_ENV === 'development';
    const pythonPath = isDev
      ? 'python'  // 开发环境使用系统 Python
      : path.join(process.resourcesPath, 'python-runtime', 'backend');  // 生产环境使用打包的可执行文件

    const args = isDev ? ['backend/main.py', '--dev'] : [];

    this.process = spawn(pythonPath, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, PYTHONUNBUFFERED: '1' }
    });

    // 监听 stdout（使用长度前缀协议）
    this.process.stdout?.on('data', (data) => {
      this.stdoutBuffer += data.toString();
      this.processBuffer();
    });

    // 监听 stderr（日志输出）
    this.process.stderr?.on('data', (data) => {
      console.error('[Python]', data.toString());
    });

    // 进程退出处理
    this.process.on('exit', (code) => {
      console.error(`Python process exited with code ${code}`);
      this.isReady = false;
      this.stopHealthCheck();
      this.emit('exit', code);

      // 自动重启（非正常退出时）
      if (code !== 0 && code !== null) {
        setTimeout(() => this.restart(), 2000);
      }
    });

    // 启动健康检查
    this.startHealthCheck();
  }

  private processBuffer() {
    while (true) {
      const newlineIndex = this.stdoutBuffer.indexOf('\n');
      if (newlineIndex === -1) break;

      const lengthStr = this.stdoutBuffer.slice(0, newlineIndex);
      const length = parseInt(lengthStr);

      if (isNaN(length)) {
        // 不是长度前缀格式，可能是日志，跳过
        this.stdoutBuffer = this.stdoutBuffer.slice(newlineIndex + 1);
        continue;
      }

      const jsonStart = newlineIndex + 1;
      const jsonEnd = jsonStart + length;

      if (this.stdoutBuffer.length < jsonEnd) break;  // 数据不完整

      const jsonStr = this.stdoutBuffer.slice(jsonStart, jsonEnd);
      this.stdoutBuffer = this.stdoutBuffer.slice(jsonEnd);

      try {
        const response = JSON.parse(jsonStr);
        this.handleResponse(response);
      } catch (e) {
        console.error('Failed to parse response:', e);
      }
    }
  }

  private handleResponse(response: any) {
    // 处理健康检查响应
    if (response.action === 'pong') {
      this.isReady = true;
      return;
    }

    // 处理业务响应
    const callback = this.responseCallbacks.get(response.id);
    if (callback) {
      callback(response);
      this.responseCallbacks.delete(response.id);
    }
  }

  async sendRequest(action: string, params: any = {}, timeout = 30000): Promise<any> {
    return new Promise((resolve, reject) => {
      const id = `${Date.now()}-${Math.random()}`;
      const request = { id, action, params };

      // 设置超时
      const timer = setTimeout(() => {
        this.responseCallbacks.delete(id);
        reject(new Error('Request timeout'));
      }, timeout);

      // 注册回调
      this.responseCallbacks.set(id, (response) => {
        clearTimeout(timer);
        if (response.success) {
          resolve(response.data);
        } else {
          reject(new Error(response.error || 'Unknown error'));
        }
      });

      // 发送请求（长度前缀格式）
      const jsonStr = JSON.stringify(request);
      const message = `${Buffer.byteLength(jsonStr)}\n${jsonStr}`;
      this.process?.stdin.write(message);
    });
  }

  private startHealthCheck() {
    // 每 30 秒发送 ping
    this.healthCheckTimer = setInterval(async () => {
      try {
        await this.sendRequest('ping', {}, 5000);
      } catch (e) {
        console.error('Health check failed, restarting...');
        this.restart();
      }
    }, 30000);
  }

  private stopHealthCheck() {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = undefined;
    }
  }

  restart() {
    this.stop();
    setTimeout(() => this.start(), 1000);
  }

  stop() {
    this.stopHealthCheck();
    this.process?.kill();
    this.process = null;
    this.isReady = false;
  }
}
```

**Python 端：双模式启动与 Action 路由**
```python
# backend/main.py
import sys
import json
import threading
from fastapi import FastAPI
from api import pin, system, insight, log, user
from core.health import register_handlers

app = FastAPI()

# 注册所有路由
app.include_router(pin.router, prefix="/api/pin", tags=["pin"])
app.include_router(system.router, prefix="/api/systems", tags=["systems"])
app.include_router(insight.router, prefix="/api/insights", tags=["insights"])
app.include_router(log.router, prefix="/api/logs", tags=["logs"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
register_handlers(app)  # 注册健康检查处理器

# Action 处理器映射（IPC 模式）
ACTION_HANDLERS = {
    'ping': lambda params: {'action': 'pong'},
    'setup_pin': pin.setup_pin,
    'verify_pin': pin.verify_pin,
    'get_systems': system.get_systems,
    'update_system_score': system.update_system_score,
    # ... 其他 action 映射
}

def ipc_loop():
    """IPC 通信循环（生产模式）"""
    for line in sys.stdin:
        try:
            # 解析长度前缀格式
            length = int(line.strip())
            json_data = sys.stdin.read(length)
            request = json.loads(json_data)

            # 路由到对应的处理器
            handler = ACTION_HANDLERS.get(request['action'])
            if handler:
                result = handler(request.get('params', {}))
                response = {
                    'id': request['id'],
                    'success': True,
                    'data': result
                }
            else:
                response = {
                    'id': request['id'],
                    'success': False,
                    'error': f'Unknown action: {request["action"]}'
                }

            # 发送响应（长度前缀格式）
            response_str = json.dumps(response)
            sys.stdout.write(f'{len(response_str.encode())}\n{response_str}')
            sys.stdout.flush()

        except Exception as e:
            error_response = {
                'id': request.get('id', ''),
                'success': False,
                'error': str(e)
            }
            error_str = json.dumps(error_response)
            sys.stdout.write(f'{len(error_str.encode())}\n{error_str}')
            sys.stdout.flush()

if __name__ == "__main__":
    if '--dev' in sys.argv:
        # 开发模式：启动 HTTP 服务器
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    else:
        # 生产模式：IPC 通信
        # 在单独线程中启动 IPC 循环
        ipc_thread = threading.Thread(target=ipc_loop, daemon=True)
        ipc_thread.start()

        # 保持主线程运行
        import time
        while True:
            time.sleep(1)
```

**健康检查模块（Python 端）：**
```python
# backend/core/health.py
from fastapi import APIRouter
from db.session import SessionLocal

router = APIRouter()

@router.get("/api/health")
async def health_check():
    """健康检查端点"""
    try:
        # 测试数据库连接
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/api/ping")
async def ping():
    """Ping 检查"""
    return {"action": "pong"}

def register_handlers(app):
    """注册健康检查处理器到 action 映射"""
    ACTION_HANDLERS = {
        'health': lambda params: health_check(),
        'ping': lambda params: ping()
    }
    return ACTION_HANDLERS
```

---

## 五、数据流设计

### 5.1 前端 → 后端通信（IPC 方案）

**IPC 请求流**
```
React Component
    ↓
调用 IPC Client 层
    ↓
ipcRenderer.send('python-request', { id, method, path, body })
    ↓
Electron Main Process 接收
    ↓
通过 stdin 发送给 Python 进程
    ↓
Python 解析 JSON → 路由到 FastAPI 处理器
    ↓
Pydantic Schema 验证
    ↓
业务逻辑处理（Service 层）
    ↓
SQLite 数据库操作
    ↓
Python 通过 stdout 返回 JSON 响应
    ↓
Electron 接收 → 通过 IPC 返回给渲染进程
    ↓
前端更新状态
```

### 5.2 AI 洞察生成流

```
用户点击「启动 AI 洞察」
    ↓
前端通过 IPC 调用 POST /api/insights/generate
    ↓
Python 后端收集当前用户系统评分
    ↓
从 user_ai_config 表获取用户配置的 API 密钥
    ↓
调用 AI Service（按优先级选择可用模型）
    ↓
构建 Prompt → 发送请求到大模型 API
    ↓
解析 JSON 响应 → 数据验证
    ↓
存储到 SQLite insights 表
    ↓
通过 IPC 返回结构化数据
    ↓
前端渲染洞察卡片
```

---

## 六、安全设计

### 6.1 IPC 通信安全
- **进程隔离**：Python 后端与渲染进程完全隔离
- **消息验证**：所有 IPC 消息携带唯一 ID，防止重放攻击
- **权限控制**：仅允许预定义的 action 调用
- **无 HTTP 暴露**：生产环境不监听任何网络端口，彻底消除 CSRF 风险

### 6.2 PIN 码认证安全
- **PIN 格式**：6 位数字，简单易记
- **哈希存储**：使用 bcrypt 哈希存储，加盐保护
- **内存会话**：解锁状态保存在内存中，应用锁定后需重新输入
- **失败限制**：连续失败 5 次后延迟 30 秒
- **可选数据库加密**：支持 SQLCipher 加密整个数据库（高安全模式）

### 6.3 数据安全
- **数据库位置**：SQLite 文件存储在用户数据目录
- **API Key 加密**：使用系统 Keychain + AES-256-GCM 加密
  - macOS: Keychain Services
  - Windows: Credential Manager
  - Linux: libsecret / Secret Service API
- **日志安全**：敏感数据（PIN、API Key）不记录日志
- **可选加密**：用户可选择启用数据库加密（使用 SQLCipher）

### 6.4 Electron 安全
```typescript
// main/index.ts
const mainWindow = new BrowserWindow({
  webPreferences: {
    nodeIntegration: false,       // 禁用 Node 集成
    contextIsolation: true,       // 启用上下文隔离
    sandbox: true,                // 启用沙箱
    preload: path.join(__dirname, 'preload.js')
  }
});

// preload.js - 暴露安全的 IPC API
contextBridge.exposeInMainWorld('electronAPI', {
  invoke: (channel: string, ...args: any[]) => {
    // 仅允许白名单通道
    const validChannels = ['python-request', 'db-query'];
    if (validChannels.includes(channel)) {
      return ipcRenderer.invoke(channel, ...args);
    }
  }
});
```

---

## 七、部署与打包

### 7.1 开发环境
```bash
# 前端
npm install
npm run dev

# 后端（开发时可独立运行，便于调试）
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py --dev  # 开发模式，同时启动 HTTP 服务器和 IPC
```

### 7.2 生产打包
```bash
# 1. 使用 PyInstaller 打包 Python 后端
cd backend
pyinstaller --onefile \
  --add-data "api:api" \
  --add-data "core:core" \
  --add-data "models:models" \
  --add-data "schemas:schemas" \
  --add-data "services:services" \
  --add-data "db:db" \
  --hidden-import fastapi \
  --hidden-import sqlalchemy \
  --hidden-import pydantic \
  main.py

# 2. 打包 Electron 应用
npm run build
npm run package

# 产物
dist/
├── Life Canvas OS-dmg-x64.dmg     # macOS 安装包
├── Life Canvas OS-win-x64.exe     # Windows 安装包
└── Life Canvas OS-linux-x64.AppImage  # Linux 安装包

# Python 后端会被嵌入到
# Contents/Resources/python-runtime/backend (macOS)
# resources/python-runtime/backend (Windows/Linux)
```

### 7.3 开发依赖清单
```
# backend/requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
passlib[bcrypt]==1.7.4  # PIN 哈希
cryptography==41.0.7     # API Key 加密
openai==1.3.5            # 兼容 DeepSeek API
httpx==0.25.2            # 异步 HTTP 客户端
python-dotenv==1.0.0     # 环境变量管理
```

### 7.4 数据库初始化

**首次启动自动建表：**
```python
# backend/db/init_db.py
from sqlalchemy import create_engine
from models import user_profile, user_settings, ai_config, system, journal
from core.database import engine

def init_database():
    """初始化数据库，创建所有表"""
    # 创建所有表
    user_profile.Base.metadata.create_all(bind=engine)
    user_settings.Base.metadata.create_all(bind=engine)
    ai_config.Base.metadata.create_all(bind=engine)

    # 系统相关表
    system.SystemBase.metadata.create_all(bind=engine)
    system.SystemFuel.metadata.create_all(bind=engine)
    system.SystemPhysical.metadata.create_all(bind=engine)
    system.SystemIntellectual.metadata.create_all(bind=engine)
    system.SystemOutput.metadata.create_all(bind=engine)
    system.SystemRecovery.metadata.create_all(bind=engine)
    system.SystemAsset.metadata.create_all(bind=engine)
    system.SystemConnection.metadata.create_all(bind=engine)
    system.SystemEnvironment.metadata.create_all(bind=engine)

    # 日志和行动项表
    system.Log.metadata.create_all(bind=engine)
    system.ActionItem.metadata.create_all(bind=engine)

    # 日记和洞察表
    journal.UserJournal.metadata.create_all(bind=engine)
    journal.Insight.metadata.create_all(bind=engine)

    # 插入默认数据
    from db.session import SessionLocal
    db = SessionLocal()

    try:
        # 1. 插入默认用户
        if not db.query(user_profile.UserProfile).first():
            default_user = user_profile.UserProfile(
                id=1,
                pin_hash='',  # 空哈希表示未设置 PIN
                display_name='User'
            )
            db.add(default_user)

        # 2. 插入默认设置
        if not db.query(user_settings.UserSettings).first():
            default_settings = user_settings.UserSettings(user_id=1)
            db.add(default_settings)

        # 3. 插入8个默认系统
        for sys_type in ['FUEL', 'PHYSICAL', 'INTELLECTUAL', 'OUTPUT',
                         'RECOVERY', 'ASSET', 'CONNECTION', 'ENVIRONMENT']:
            if not db.query(system.SystemBase).filter_by(type=sys_type).first():
                # 创建公共字段
                base_system = system.SystemBase(
                    user_id=1,
                    type=sys_type,
                    score=50
                )
                db.add(base_system)
                db.flush()  # 获取 ID

                # 创建专属字段
                if sys_type == 'FUEL':
                    db.add(system.SystemFuel(system_id=base_system.id))
                elif sys_type == 'PHYSICAL':
                    db.add(system.SystemPhysical(system_id=base_system.id))
                elif sys_type == 'INTELLECTUAL':
                    db.add(system.SystemIntellectual(system_id=base_system.id))
                elif sys_type == 'OUTPUT':
                    db.add(system.SystemOutput(system_id=base_system.id))
                elif sys_type == 'RECOVERY':
                    db.add(system.SystemRecovery(system_id=base_system.id))
                elif sys_type == 'ASSET':
                    db.add(system.SystemAsset(system_id=base_system.id))
                elif sys_type == 'CONNECTION':
                    db.add(system.SystemConnection(system_id=base_system.id))
                elif sys_type == 'ENVIRONMENT':
                    db.add(system.SystemEnvironment(system_id=base_system.id))

        db.commit()
        print("✅ Database initialized successfully!")
        print("✅ Created 8 systems with base and detail tables")

    except Exception as e:
        db.rollback()
        print(f"❌ Initialization failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
```

**版本升级迁移脚本（按需）：**
```python
# backend/db/migrations/migration_002_add_journal_table.py
"""
版本 1.1.0 迁移脚本：添加用户日记功能
"""
def upgrade():
    from db.session import SessionLocal
    db = SessionLocal()
    try:
        # 创建日记表
        db.execute("""
            CREATE TABLE IF NOT EXISTS user_journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                mood TEXT CHECK(mood IN ('great', 'good', 'neutral', 'bad', 'terrible')),
                tags TEXT,
                related_system TEXT,
                is_private INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
            )
        """)

        # 创建索引
        db.execute("CREATE INDEX IF NOT EXISTS idx_journal_created ON user_journal(created_at DESC)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_journal_mood ON user_journal(mood)")

        db.commit()
        print("✅ Migration 1.1.0 completed: Added user_journal table")

    except Exception as e:
        db.rollback()
        print(f"❌ Migration failed: {e}")
    finally:
        db.close()

def downgrade():
    """回滚迁移"""
    from db.session import SessionLocal
    db = SessionLocal()
    try:
        db.execute("DROP TABLE IF EXISTS user_journal")
        db.commit()
        print("✅ Rollback completed: Dropped user_journal table")
    except Exception as e:
        db.rollback()
        print(f"❌ Rollback failed: {e}")
    finally:
        db.close()
```

---

## 八、后续扩展方向

### 8.1 功能扩展
- [ ] 数据导入/导出（CSV/JSON/Markdown）
- [ ] 插件系统支持自定义子系统
- [ ] 社区分享子系统配置模板
- [ ] 数据可视化报告导出 PDF
- [ ] 移动端适配（React Native 或 Tauri 移植）
- [ ] 小组件模式（桌面小组件）
- [ ] 全局快捷键支持

### 8.2 AI 增强
- [ ] 对话式 AI 助手集成（本地 + 云端）
- [ ] 自动化目标拆解建议
- [ ] 基于历史数据的趋势预测
- [ ] 个性化习惯养成计划
- [ ] AI 辅助日记分析（情绪趋势、关键词提取）

### 8.3 数据安全与备份
- [ ] 可选的云端备份功能（加密后上传）
- [ ] 数据库加密选项（SQLCipher）
- [ ] 自动备份到指定目录
- [ ] 数据导出为加密压缩包
- [ ] 跨设备数据迁移工具

### 8.4 社交与分享（可选）
- [ ] 匿名社区分享（可公开日记和成就）
- [ ] 子系统配置模板市场
- [ ] 成就徽章系统
- [ ] 月度/年度报告生成

---

## 附录：开发优先级建议

### Phase 1: MVP（最小可行产品）
1. ✅ 基础项目搭建（Electron + React + Python）
2. ✅ SQLite 数据库设计与自动建表（子系统表拆分）
3. ✅ 双模式通信机制（开发 HTTP + 生产 IPC）
4. ✅ PIN 认证系统
5. ✅ 八大子系统 CRUD（公共字段 + 专属字段）
6. ✅ 雷达图可视化
7. ✅ 基础 AI 洞察功能（DeepSeek/文心/豆包 三选一）
8. ✅ Python 进程健康检查
9. ✅ 用户设置管理

### Phase 2: 核心功能完善
1. ⏳ 各子系统详细功能实现（8个系统专属界面）
2. ⏳ AI 配置管理与 API 测试功能
3. ⏳ 历史记录与时间轴
4. ⏳ 用户日记功能（新增）
5. ⏳ 数据导入/导出
6. ⏳ 行动项/里程碑管理
7. ⏳ 数据备份与恢复

### Phase 3: 体验优化
1. ⏳ UI/UX 细节打磨（shadcn/ui 组件定制）
2. ⏳ 性能优化（数据库查询优化、懒加载）
3. ⏳ 错误处理与日志系统
4. ⏳ 打包与分发（macOS/Windows/Linux）
5. ⏳ 应用内自动更新
6. ⏳ 全局快捷键支持

---

## 项目总结

### 当前实现状态

> **最后更新：** 2026-02-05

#### ✅ 已完成模块

**前端框架：**
- ✅ Electron + React 19 基础框架
- ✅ TypeScript 配置
- ✅ Vite 构建系统
- ✅ 路由配置（`src/renderer/routes.tsx`）
- ✅ 共享类型定义（`src/shared/types.ts`）
- ✅ 共享常量（`src/shared/constants.ts`）
- ✅ 一个 UI 组件示例（`components/ui/alert.tsx`）

**主进程：**
- ✅ 主进程入口（`src/main/index.ts`）
- ✅ 窗口管理（`src/main/windows/main.ts`）
- ✅ Python 进程管理器（`src/main/python/manager.ts`）

**后端框架：**
- ✅ FastAPI 应用入口（`backend/main.py`）
- ✅ 健康检查模块（`backend/core/health.py`）
- ✅ 基础目录结构（api、core、db、models、schemas、services）

**构建工具：**
- ✅ Electron 应用工厂模式
- ✅ 发布和构建脚本
- ✅ Biome 代码格式化配置

#### 🔴 待开发模块

**前端业务逻辑：**
- ❌ 所有页面组件（Canvas、Insights、History、Settings、SystemDetail）
- ❌ UI 组件库（Button、Input、Dialog、Toast 等）
- ❌ 布局组件（Sidebar、Header）
- ❌ 业务组件（8个子系统、图表、卡片等）
- ❌ React Query 集成
- ❌ 自定义 Hooks（useIPC、usePinLock、useDatabaseHealth）
- ❌ IPC 客户端封装

**后端业务逻辑：**
- ❌ PIN 认证系统
- ❌ 用户配置管理
- ❌ 8个子系统 CRUD
- ❌ AI 洞察生成
- ❌ 用户日记功能
- ❌ 数据库模型和初始化
- ❌ 所有业务 API

#### 📊 实现进度

| 模块类型 | 规划数量 | 已实现 | 实现率 |
|---------|---------|--------|--------|
| 前端页面 | 5 | 0 | 0% |
| UI 组件 | 20+ | 1 | ~5% |
| React Query Hooks | 6 | 0 | 0% |
| 自定义 Hooks | 3 | 0 | 0% |
| 主进程模块 | 7 | 3 | 43% |
| 后端 API | 7 | 0 | 0% |
| 后端 Models | 4 | 0 | 0% |
| 后端 Schemas | 6 | 0 | 0% |
| 后端 Services | 4 | 0 | 0% |
| **总计** | **70+** | **4** | **~6%** |

---

### 核心特性

| 特性 | 说明 |
|------|------|
| **技术栈** | Electron + React + Python + SQLite |
| **数据存储** | 本地 SQLite，完全掌控用户数据 |
| **AI 集成** | 支持 DeepSeek/文心一言/豆包 三选一 |
| **认证方式** | 6位 PIN 码 + 可选数据库加密 |
| **子系统** | 8个维度，公共字段 + 专属字段表分离 |
| **用户日记** | 支持心情记录、标签关联、统计分析 |
| **通信架构** | 开发环境 HTTP，生产环境 IPC |
| **跨平台** | 支持 macOS/Windows/Linux |

### 数据库表清单（16个表）

**用户相关（3个）：**
- user_profile（用户身份）
- user_settings（用户配置）
- ai_config（AI配置）

**日记与洞察（2个）：**
- user_journal（用户日记）
- insights（AI洞察）

**子系统（10个）：**
- systems_base（子系统公共字段）
- systems_fuel（饮食系统）
- systems_physical（运动系统）
- systems_intellectual（读书系统）
- systems_output（工作系统）
- systems_recovery（梦想系统）
- systems_asset（财务系统）
- systems_connection（社交系统）
- systems_environment（环境系统）
- action_items（行动项）

**日志（1个）：**
- logs（系统日志）

---

*文档版本：v3.0*
*最后更新：2026-02-03*
