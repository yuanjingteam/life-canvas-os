# Life Canvas OS

> 基于八维量化模型的 AI 驱动个人成长桌面操作系统

<div align="center">

![Life Canvas OS](./resources/public/logo.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Electron](https://img.shields.io/badge/Electron-39.2.6-blue)](https://www.electronjs.org/)
[![React](https://img.shields.io/badge/React-19.2.1-blue)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.12-green)](https://www.python.org/)

**一个帮助你系统化管理、量化并优化个人生活的桌面应用**

[功能特性](#-核心特性) • [快速开始](#-快速开始) • [开发指南](#-开发指南) • [贡献](#-贡献)

</div>

---

## 📖 项目简介

Life Canvas OS 是一款创新的个人成长管理工具，基于**八维生命平衡模型**，帮助你：

- 🎯 **系统化管理**：将生活抽象为 8 个可量化的子系统
- 📊 **数据驱动**：通过量化评分和趋势分析辅助决策
- 🤖 **AI 洞察**：利用 AI 技术提供个性化分析和建议
- 🔒 **隐私优先**：数据完全存储在本地，你拥有完全控制权
- 🎨 **极简美学**：现代化的 UI 设计，提供沉浸式体验

### 🎯 八维生命平衡模型

1. **饮食系统 (FUEL)** - 追踪饮食习惯，保持健康基准
2. **运动系统 (PHYSICAL)** - 监控运动计划，维护身体活力
3. **读书系统 (INTELLECTUAL)** - 记录阅读进度，积累思想火花
4. **工作系统 (OUTPUT)** - 管理工作产出，追踪 OKR 目标
5. **梦想系统 (RECOVERY)** - 设定并实现人生梦想
6. **财务系统 (ASSET)** - 管理资产和负债，实现财务自由
7. **社交系统 (CONNECTION)** - 维护人际关系，提升社交能量
8. **环境系统 (ENVIRONMENT)** - 优化生活空间，创建理想环境

---

## ✨ 核心特性

### 当前已实现 ✅

- **跨平台桌面应用** - 基于 Electron，支持 macOS、Windows、Linux
- **现代化前端** - React 19 + TypeScript + Vite
- **Python 后端** - FastAPI + SQLite 双模式架构
- **进程管理** - 健康检查和自动重启机制
- **代码规范** - Biome 统一代码格式化

### 规划中 🔜

- **PIN 码认证** - 6 位数字快速锁定应用
- **八维评分系统** - 可视化雷达图展示
- **AI 智能洞察** - 支持 DeepSeek/豆包，提供个性化建议
- **用户日记** - 记录心情、关联系统、统计分析
- **时间轴审计** - 完整的生活轨迹回顾
- **数据管理** - 导入/导出、备份恢复

> **注意：** 项目处于早期开发阶段（约 7% 完成）。详细的实现进度请查看 [docs/STRUCTURE_AUDIT.md](./docs/STRUCTURE_AUDIT.md)

---

## 🛠️ 技术栈

### 前端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| [Electron](https://www.electronjs.org/) | 39.2.6 | 跨平台桌面应用框架 |
| [React](https://react.dev/) | 19.2.1 | UI 框架 |
| [TypeScript](https://www.typescriptlang.org/) | 5.9.3 | 类型安全 |
| [Vite](https://vitejs.dev/) | 7.2.6 | 快速构建工具 |
| [TailwindCSS](https://tailwindcss.com/) | 4.1.17 | 原子化 CSS 框架 |
| [shadcn/ui](https://ui.shadcn.com/) | Latest | 高质量 React 组件 |
| [TanStack Query](https://tanstack.com/query) | 5.90.20 | 服务端状态管理 |
| [Recharts](https://recharts.org/) | 3.7.0 | 数据可视化 |

### 后端技术

| 技术 | 版本 | 说明 |
|------|------|------|
| [Python](https://www.python.org/) | 3.12+ | 后端服务语言 |
| [FastAPI](https://fastapi.tiangolo.com/) | 0.104.1+ | 高性能异步 API 框架 |
| [SQLAlchemy](https://www.sqlalchemy.org/) | 2.0.23+ | Python ORM |
| [Pydantic](https://docs.pydantic.dev/) | 2.5.0+ | 数据验证 |
| [SQLite](https://www.sqlite.org/) | 3 | 嵌入式数据库 |

### 开发工具

- **Biome 2.3.8** - 代码格式化和检查
- **electron-builder 26.0.12** - 应用打包
- **tsx 4.21.0** - TypeScript 执行

---

## 🚀 快速开始

### 环境要求

- **Node.js** >= 18.0.0
- **Python** >= 3.12
- **pnpm** >= 8.0.0（推荐）或 npm >= 9.0.0

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/your-org/life-canvas-os.git
cd life-canvas-os
```

#### 2. 安装前端依赖

```bash
# 使用 pnpm（推荐）
pnpm install

# 或使用 npm
npm install
```

#### 3. 设置 Python 环境

```bash
# 创建 Python 虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装 Python 依赖（待添加 requirements.txt）
# pip install -r backend/requirements.txt
```

#### 4. 启动开发服务器

```bash
# 启动 Electron 开发模式
pnpm dev

# 或使用 npm
npm run dev
```

应用将自动启动并打开开发窗口。

---

## 💻 开发指南

### 项目结构

```
life-canvas-os/
├── backend/                 # Python 后端
│   ├── api/                # API 路由（待开发）
│   ├── core/               # 核心逻辑
│   ├── models/             # 数据模型（待开发）
│   ├── schemas/            # Pydantic Schema（待开发）
│   ├── services/           # 业务服务（待开发）
│   ├── db/                 # 数据库模块（待开发）
│   └── main.py             # 应用入口
│
├── docs/                   # 项目文档
│   ├── REQUIREMENT.md      # 产品需求文档
│   ├── DESIGN.md           # 设计文档
│   ├── PROJECT_STANDARDS.md # 项目规范
│   └── STRUCTURE_AUDIT.md  # 结构审计报告
│
├── scripts/                # 构建和发布脚本
│
├── src/                    # 前端源代码
│   ├── main/               # Electron 主进程
│   │   ├── index.ts        # 主进程入口
│   │   ├── python/         # Python 进程管理
│   │   └── windows/        # 窗口管理
│   │
│   ├── preload/            # 预加载脚本
│   │   └── index.ts
│   │
│   ├── renderer/           # 渲染进程（React）
│   │   ├── components/     # React 组件
│   │   │   ├── ui/        # shadcn/ui 组件
│   │   │   ├── canvas/    # 画布组件（待开发）
│   │   │   ├── insights/  # AI 洞察（待开发）
│   │   │   └── system/    # 系统组件（待开发）
│   │   ├── hooks/         # 自定义 Hooks（待开发）
│   │   ├── pages/         # 页面组件（待开发）
│   │   ├── queries/       # TanStack Query（待开发）
│   │   └── routes.tsx     # 路由配置
│   │
│   ├── shared/             # 共享模块
│   │   ├── constants.ts   # 常量定义
│   │   ├── types.ts       # TypeScript 类型
│   │   └── utils.ts       # 工具函数
│   │
│   ├── lib/electron-app/   # Electron 工具库
│   └── resources/          # 资源文件
│
├── .gitignore
├── package.json
├── tsconfig.json
├── biome.json
├── electron.vite.config.ts
└── README.md
```

### 开发命令

```bash
# 启动开发服务器
pnpm dev

# 构建项目
pnpm build

# 运行测试（待配置）
pnpm test

# 代码格式化
pnpm format

# 代码检查
pnpm lint

# 类型检查
pnpm typecheck

# 打包 Python 后端
pnpm build:python

# 完整构建（Python + Electron）
pnpm build:all

# 创建发布版本
pnpm release
```

### 代码规范

项目使用 **Biome** 进行代码格式化和检查：

```bash
# 格式化所有代码
pnpm format

# 检查代码规范
pnpm lint

# 自动修复问题
pnpm lint:fix
```

详细的开发规范请查看：[docs/PROJECT_STANDARDS.md](./docs/PROJECT_STANDARDS.md)

### 架构设计

- **设计文档**：[docs/DESIGN.md](./docs/DESIGN.md)
- **产品需求**：[docs/REQUIREMENT.md](./docs/REQUIREMENT.md)
- **实现状态**：[docs/STRUCTURE_AUDIT.md](./docs/STRUCTURE_AUDIT.md)

---

## 📊 当前实现状态

### ✅ 已完成（约 7%）

**前端：**
- [x] Electron + React 19 基础框架
- [x] TypeScript + Vite 配置
- [x] 路由配置
- [x] 共享类型定义
- [x] shadcn/ui Alert 组件示例

**主进程：**
- [x] 主进程入口
- [x] 窗口管理
- [x] Python 进程管理器（带健康检查）

**后端：**
- [x] FastAPI 应用框架
- [x] 健康检查接口
- [x] 基础目录结构

### 🔴 待开发

**核心功能：**
- [ ] PIN 码认证系统
- [ ] 用户配置管理
- [ ] 8 个子系统 CRUD
- [ ] AI 洞察生成
- [ ] 用户日记功能
- [ ] 数据库模型和初始化

**前端组件：**
- [ ] 页面组件（Canvas、Insights、History、Settings）
- [ ] UI 组件库（Button、Input、Dialog、Toast 等）
- [ ] 布局组件（Sidebar、Header）
- [ ] 雷达图可视化

**后端 API：**
- [ ] PIN 认证 API
- [ ] 用户配置 API
- [ ] 系统数据 API
- [ ] AI 洞察 API
- [ ] 用户日记 API

详细的实现计划请查看：[docs/DESIGN.md#开发优先级建议](./docs/DESIGN.md)

---

## 🤝 贡献

我们欢迎所有形式的贡献！

### 贡献指南

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'feat: add some amazing feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Type 类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试
- `chore`: 构建/工具

**示例：**
```bash
git commit -m "feat(auth): add PIN code verification"
git commit -m "fix(api): handle database connection error"
git commit -m "docs(readme): update installation guide"
```

---

## 📝 开发路线图

### Phase 0: 基础设施 ✅
- [x] Electron + React + Python 框架
- [x] 基础目录结构
- [x] Python 进程管理

### Phase 1: 数据层 🔜
- [ ] 数据库模型设计
- [ ] 数据库初始化脚本
- [ ] Pydantic schemas
- [ ] 数据库迁移机制

### Phase 2: 后端 API 🔜
- [ ] PIN 认证系统
- [ ] 用户配置 API
- [ ] 系统数据 API
- [ ] AI 洞察 API
- [ ] 用户日记 API

### Phase 3: 前端组件 🔜
- [ ] UI 基础组件库
- [ ] 布局组件
- [ ] 页面组件
- [ ] React Query 集成
- [ ] 雷达图可视化

### Phase 4: 业务逻辑 🔜
- [ ] 8 个子系统详细功能
- [ ] AI 洞察生成
- [ ] 用户日记
- [ ] 时间轴审计

### Phase 5: 打包发布 🔜
- [ ] macOS 安装包
- [ ] Windows 安装包
- [ ] Linux 安装包
- [ ] 自动更新机制

---

## 📄 许可证

本项目采用 [MIT](./LICENSE) 许可证。

---

## 🙏 致谢

- [Electron](https://www.electronjs.org/) - 跨平台桌面应用框架
- [React](https://react.dev/) - UI 框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [shadcn/ui](https://ui.shadcn.com/) - 精美的 React 组件库
- [TailwindCSS](https://tailwindcss.com/) - 实用优先的 CSS 框架

---
