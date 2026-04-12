# Life Canvas OS 前端开发规划

> 更新日期：2026-02-07
> 规划基础：基于 `/Users/petrel/electron-app/life-canvas-os-ui` UI设计
> 开发范围：仅前端，不涉及后端API实现

---

## 📊 整体进度概览

```
Phase 1: ░░░░░░░░░░░░░░░░░░░░   0% (UI 基础设施)
Phase 2: ░░░░░░░░░░░░░░░░░░░░   0% (核心布局)
Phase 3: ░░░░░░░░░░░░░░░░░░░░   0% (页面开发)
Phase 4: ░░░░░░░░░░░░░░░░░░░░   0% (子系统集成)
Phase 5: ░░░░░░░░░░░░░░░░░░░░   0% (集成与优化)
```

---

## 🎯 核心设计原则

基于UI设计，本项目的核心设计原则：

1. **Apple 风格设计**：玻璃拟态（Glassmorphism）效果
2. **深色/浅色主题**：自动检测系统主题设置
3. **优雅的动画**：使用 animate-in 类实现流畅过渡
4. **响应式布局**：适配不同窗口尺寸
5. **统一的设计语言**：使用 TailwindCSS + 自定义颜色系统

---

## Phase 1: UI 基础设施 ✨

### 1.1 样式系统配置

#### 已安装的依赖 ✅

- [x] lucide-react（图标库）
- [x] recharts（图表库）
- [x] class-variance-authority（样式变体管理）
- [x] clsx & tailwind-merge（类名工具）
- [x] @tanstack/react-query（状态管理）
- [x] react-hook-form（表单管理）
- [x] @uiw/react-md-editor（Markdown 编辑器）
- [x] date-fns（日期处理）

#### shadcn/ui 组件添加

使用 `npx shadcn@latest add <component>` 添加需要的组件：

**基础组件（必需）**：

- [ ] button - 按钮组件
- [ ] input - 输入框
- [ ] textarea - 文本域
- [ ] label - 标签
- [ ] card - 卡片组件（用于替代/增强 GlassCard）
- [ ] select - 下拉选择
- [ ] switch - 开关
- [ ] slider - 滑块
- [ ] tabs - 标签页
- [ ] dialog - 对话框
- [ ] toast - 消息提示
- [ ] dropdown-menu - 下拉菜单

**表单组件（用于设置页面）**：

- [ ] form - 表单容器
- [ ] checkbox - 复选框
- [ ] radio-group - 单选框组

**其他有用组件**：

- [ ] avatar - 头像（侧边栏用户卡片）
- [ ] badge - 徽章（标签显示）
- [ ] separator - 分隔线
- [ ] scroll-area - 滚动区域
- [ ] tooltip - 工具提示

#### 自定义颜色系统

**文件**：`tailwind.config.js` / `src/renderer/globals.css`

需要添加 Apple 风格的颜色变量：

```css
/* 浅色模式 */
--apple-bgMain: #fafafc --apple-bg2: #f5f5f7 --apple-bgSidebar: #ebebed
  --apple-textMain: #1d1d1f --apple-textSec: #86868b --apple-textTer: #afb1b6
  --apple-border: #e5e5ea --apple-accent: #0a84ff /* 深色模式 */
  --apple-bgMain-dark: #000000 --apple-textMain-dark: #ffffff
  /* ... 其他深色变量 */;
```

#### 动画工具类

**文件**：`src/renderer/globals.css`

添加玻璃拟态效果和动画类：

```css
.sidebar-glass {
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.liquid-glass {
  background: rgba(255, 255, 255, 0.7);
}

.shadow-apple-soft {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* animate-in 动画系列 */
.animate-in {
  animation-fill-mode: both;
}
.fade-in {
  animation: fade-in 0.5s ease-out;
}
.zoom-in-95 {
  animation: zoom-in-95 0.5s ease-out;
}
.slide-in-from-bottom-4 {
  animation: slide-in 0.7s ease-out;
}
```

---

### 1.2 项目特定自定义组件

> 说明：基础 UI 组件使用 shadcn/ui，这里只列出项目特定的自定义组件

#### GlassCard 组件（需优化）

**文件**：`src/renderer/components/GlassCard.tsx`

- [ ] 优化浅色/深色模式适配
- [ ] 添加 title 属性支持
- [ ] 添加 className 自定义支持
- [ ] 确保 glassmorphism 效果在深色模式下正确显示
- [ ] **是否与 shadcn/ui Card 组件整合？需要决策**

#### 需要的自定义组件

- [ ] `src/renderer/components/layout/Sidebar.tsx` - 侧边栏（使用 shadcn/ui 组件构建）
- [ ] `src/renderer/components/layout/MainLayout.tsx` - 主布局
- [ ] `src/renderer/components/layout/PageHeader.tsx` - 页面头部
- [ ] `src/renderer/components/auth/PinLockScreen.tsx` - PIN 锁屏界面
- [ ] `src/renderer/components/canvas/SystemCard.tsx` - 系统卡片（全局画布用）
- [ ] `src/renderer/components/canvas/RadarChartCard.tsx` - 雷达图卡片
- [ ] `src/renderer/components/canvas/LifeProgressCard.tsx` - 生命进度卡片
- [ ] `src/renderer/components/canvas/AIInsightCard.tsx` - AI 洞察卡片
- [ ] `src/renderer/components/journal/JournalCard.tsx` - 日记卡片
- [ ] `src/renderer/components/journal/MoodSelector.tsx` - 情绪选择器
- [ ] `src/renderer/components/timeline/TimelineItem.tsx` - 时间轴条目
- [ ] `src/renderer/components/timeline/TimelineFilter.tsx` - 时间轴筛选器

---

### 1.3 工具函数

**文件**：`src/renderer/lib/utils.ts`

- [x] cn() 函数（合并 Tailwind 类名）
- [ ] formatDate() - 日期格式化
- [ ] formatTimestamp() - 时间戳格式化
- [ ] calculateLifeProgress() - 计算生命进度
- [ ] getMoodEmoji() - 获取情绪表情
- [ ] getMoodColor() - 获取情绪颜色

---

## Phase 2: 核心布局组件 🏗️

### 2.1 应用状态管理

#### 全局 Context

**文件**：`src/renderer/contexts/AppContext.tsx`

使用 React Context 管理全局状态：

```typescript
interface AppState {
  // 用户信息
  user: UserProfile;

  // 八个维度评分
  dimensions: Record<DimensionType, number>;

  // 饮食系统数据
  fuelSystem: FuelSystemData;

  // 日记列表
  journals: JournalEntry[];

  // 锁定状态
  isLocked: boolean;

  // 主题设置
  theme: "light" | "dark" | "auto";

  // AI 配置
  aiConfig: AIConfig;

  // 系统配置
  systemConfig: SystemConfig;
}
```

- [ ] 创建 AppContext
- [ ] 创建 Provider 组件
- [ ] 创建 useApp hook
- [ ] 实现 localStorage 持久化
- [ ] 实现主题切换逻辑

---

### 2.2 主应用结构

#### App.tsx 重构

**文件**：`src/renderer/App.tsx`

参考 UI 设计的 App.tsx，实现：

- [ ] 状态管理集成
- [ ] 主题切换逻辑（监听系统主题）
- [ ] 锁屏/解锁逻辑
- [ ] 背景渐变效果
- [ ] 路由集成

#### PinLockScreen 组件

**文件**：`src/renderer/components/auth/PinLockScreen.tsx`

- [ ] 4 位 PIN 码输入界面
- [ ] 玻璃拟态卡片效果
- [ ] 错误提示动画
- [ ] 解锁按钮交互
- [ ] 背景模糊效果

---

### 2.3 布局组件

#### Sidebar 组件

**文件**：`src/renderer/components/layout/Sidebar.tsx`

参考 UI 设计的侧边栏：

- [ ] Logo 和版本号显示
- [ ] 导航菜单（5个主要项目）
- [ ] 当前页面高亮
- [ ] 玻璃拟态效果
- [ ] 用户信息卡片（头像、姓名、MBTI、寿命）
- [ ] 锁定按钮

导航菜单项：

1. 全局总览（Dashboard）
2. 饮食系统（Fuel System）
3. 生活日记（Journal）
4. 时间轴（Timeline）
5. 系统设置（Settings）

#### MainLayout 组件

**文件**：`src/renderer/components/layout/MainLayout.tsx`

- [ ] 集成 Sidebar
- [ ] 主内容区域
- [ ] 背景渐变动画
- [ ] 响应式布局

#### PageHeader 组件

**文件**：`src/renderer/components/layout/PageHeader.tsx`

- [ ] 页面标题
- [ ] 副标题/描述
- [ ] 操作按钮区域

---

### 2.4 路由配置更新

**文件**：`src/renderer/routes.tsx`

更新路由结构：

```typescript
<HashRouter>
  <Routes>
    {/* 默认重定向 */}
    <Route path="/" element={<Navigate to="/dashboard" replace />} />

    {/* 主应用路由（带布局） */}
    <Route element={<MainLayout />}>
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/system/fuel" element={<FuelSystemPage />} />
      <Route path="/journal" element={<JournalPage />} />
      <Route path="/journal/:id" element={<JournalDetailPage />} />
      <Route path="/timeline" element={<TimelinePage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Route>

    {/* 其他子系统路由 */}
    <Route path="/system/:type" element={<SystemDetailPage />} />
  </Routes>
</HashRouter>
```

---

## Phase 3: 核心页面开发 📄

### 3.1 Dashboard（全局总览）

**文件**：`src/renderer/pages/dashboard/DashboardPage.tsx`

参考 UI：`views/Dashboard.tsx`

功能清单：

- [ ] 欢迎信息（用户名）
- [ ] 平衡总分显示
- [ ] **八维雷达图**（使用 Recharts）
  - [ ] RadarChart 配置
  - [ ] PolarGrid 网格线
  - [ ] PolarAngleAxis 维度标签
  - [ ] 雷达区域填充
  - [ ] 浅色/深色模式适配

- [ ] **AI 智能洞察卡片**
  - [ ] 洞察内容显示
  - [ ] 首要改进建议
  - [ ] "查看详细报告"按钮

- [ ] **生命进度卡片**
  - [ ] 百岁目标显示
  - [ ] 生命进度百分比计算
  - [ ] 进度条动画
  - [ ] 引用文字

- [ ] **八维小卡片网格**
  - [ ] 8 个维度的小卡片
  - [ ] 每个卡片显示图标、名称、评分
  - [ ] 悬停动画效果
  - [ ] 点击跳转到详情页

---

### 3.2 FuelSystem（饮食系统）

**文件**：`src/renderer/pages/systems/FuelSystemPage.tsx`

参考 UI：`views/FuelSystem.tsx`

功能清单：

- [ ] 页面标题和描述
- [ ] **一致性评分卡片**
  - [ ] 实时计算（100 - 偏离次数 × 5）
  - [ ] 橙色主题样式

- [ ] **每日基准（Baseline）卡片**
  - [ ] 显示基准文本
  - [ ] 编辑模式切换
  - [ ] Textarea 编辑器
  - [ ] 保存/取消按钮

- [ ] **记录偏离事件卡片**
  - [ ] 输入框（添加偏离描述）
  - [ ] 添加按钮（+ 图标）
  - [ ] Enter 键提交
  - [ ] 警告提示（每次偏离降低 5%）

- [ ] **偏离时间轴**
  - [ ] 偏离事件列表
  - [ ] 时间戳显示
  - [ ] 删除按钮（悬停显示）
  - [ ] 空状态提示

---

### 3.3 Journal（生活日记）

**文件**：`src/renderer/pages/journal/JournalPage.tsx`

参考 UI：`views/Journal.tsx`

功能清单：

- [ ] 页面标题
- [ ] **新建日记按钮**
- [ ] **日记列表**
  - [ ] 日期分组显示
  - [ ] 情绪图标
  - [ ] 日记内容预览
  - [ ] 标签显示
  - [ ] 点击查看详情

- [ ] **筛选器**
  - [ ] 按日期范围筛选
  - [ ] 按情绪筛选
  - [ ] 按标签筛选
  - [ ] 按关联维度筛选

- [ ] **空状态**
  - [ ] 无日记时的提示
  - [ ] 引导创建日记

#### JournalEditor（日记编辑器）

**文件**：`src/renderer/pages/journal/JournalEditorPage.tsx`

- [ ] 标题输入
- [ ] Markdown 编辑器
- [ ] 情绪选择器（5 种情绪）
- [ ] 标签输入（支持多个）
- [ ] 关联维度选择（多选）
- [ ] 附件上传
- [ ] 保存/更新按钮
- [ ] 取消按钮

---

### 3.4 Timeline（时间轴）

**文件**：`src/renderer/pages/timeline/TimelinePage.tsx`

参考 UI：`views/TimelineView.tsx`

功能清单：

- [ ] 页面标题
- [ ] **时间轴视图**
  - [ ] 按日期分组
  - [ ] 显示所有类型的事件
    - 维度评分变化
    - 日记记录
    - 偏离事件
    - 系统设置更改
  - [ ] 时间轴连接线
  - [ ] 事件图标（根据类型）

- [ ] **筛选器**
  - [ ] 按事件类型筛选
  - [ ] 按日期范围筛选
  - [ ] 按维度筛选

- [ ] **搜索功能**
  - [ ] 关键词搜索

---

### 3.5 Settings（系统设置）

**文件**：`src/renderer/pages/settings/SettingsPage.tsx`

参考 UI：`views/SettingsView.tsx`

功能清单：

- [ ] Tabs 导航

#### 基本信息设置 Tab

- [ ] display_name 输入
- [ ] birthday 日期选择器
- [ ] mbti 选择器（16 种类型）
- [ ] values 输入（支持多个）
- [ ] life_expectancy 滑块（50-120 岁）

#### 外观设置 Tab

- [ ] theme 选择（light/dark/auto）
- [ ] language 选择（中文/English）
- [ ] auto_save_enabled 开关
- [ ] notification_enabled 开关
- [ ] show_year_progress 开关
- [ ] show_weekday 开关

#### AI 配置 Tab

- [ ] provider 选择（DeepSeek/豆包）
- [ ] api_key 输入（密码类型）
- [ ] frequency_limit 滑块
- [ ] 测试连接按钮

#### 安全设置 Tab

- [ ] 修改 PIN 功能
- [ ] 确认旧 PIN
- [ ] 输入新 PIN
- [ ] 确认新 PIN
- [ ] 数据导出按钮
- [ ] 数据导入按钮
- [ ] 清除数据按钮（危险操作）

---

## Phase 4: 子系统集成 🧩

### 4.1 其他子系统页面

虽然 UI 设计中只实现了 FuelSystem，但需要为其他 7 个子系统创建类似的页面：

#### SystemDetailPage（通用子系统详情页）

**文件**：`src/renderer/pages/systems/SystemDetailPage.tsx`

支持所有 8 种系统类型：

1. FUEL - 饮食系统（已有独立页面）
2. PHYSICAL - 运动系统
3. INTELLECTUAL - 认知系统
4. OUTPUT - 产出系统
5. RECOVERY - 梦想系统
6. ASSET - 财务系统
7. CONNECTION - 社交系统
8. ENVIRONMENT - 环境系统

每个系统需要：

- [ ] 系统评分显示和调整（+/- 按钮）
- [ ] 系统特定的数据结构
- [ ] 日志记录
- [ ] 行动项管理（待办事项）
- [ ] 进度追踪

### 4.2 子系统特定功能

#### PhysicalSystem（运动系统）

- [ ] 运动计划记录
- [ ] 维护指数追踪
- [ ] 运动日志

#### IntellectualSystem（认知系统）

- [ ] 读书进度追踪
- [ ] 学习笔记
- [ ] 思想火花记录

#### OutputSystem（产出系统）

- [ ] OKR 目标管理
- [ ] 产出记录
- [ ] 专注时间统计

#### RecoverySystem（梦想系统）

- [ ] 梦想清单
- [ ] 睡眠质量记录
- [ ] 恢复活动追踪

#### AssetSystem（财务系统）

- [ ] 资产记录
- [ ] 收支记录
- [ ] 财务目标

#### ConnectionSystem（社交系统）

- [ ] 社交能量记录
- [ ] 人际关系管理
- [ ] 社交活动日志

#### EnvironmentSystem（环境系统）

- [ ] 空间管理任务
- [ ] 环境改善记录
- [ ] 维护提醒

---

## Phase 5: 集成与优化 🚀

### 5.1 API 集成准备

虽然不实现后端，但需要准备好 API 调用的结构：

#### API 客户端

**文件**：`src/renderer/lib/api.ts`

- [ ] 创建 API 基础配置
- [ ] 实现请求拦截器
- [ ] 实现响应拦截器
- [ ] 错误处理
- [ ] TypeScript 类型定义

#### TanStack Query 集成

**文件**：`src/renderer/queries/`

- [ ] 设置 QueryClient
- [ ] 创建查询 Hooks（为未来准备）
  - useUserProfile
  - useDimensions
  - useJournals
  - useFuelSystem
  - 等

---

### 5.2 动画与交互

- [ ] 页面过渡动画
- [ ] 卡片悬停效果
- [ ] 按钮点击反馈
- [ ] 加载状态指示器
- [ ] Toast 通知系统
- [ ] 模态框动画

---

### 5.3 性能优化

- [ ] 代码分割（React.lazy）
- [ ] 路由级懒加载
- [ ] 图表数据缓存
- [ ] 防抖/节流（搜索、输入）
- [ ] 图片懒加载
- [ ] Bundle 大小优化

---

### 5.4 响应式设计

- [ ] 侧边栏在窄屏时的行为
- [ ] 卡片网格在不同尺寸下的布局
- [ ] 移动端适配（虽然主要面向桌面）

---

### 5.5 主题系统完善

- [ ] 确保所有组件支持浅色/深色模式
- [ ] 主题切换动画
- [ ] 系统主题自动检测
- [ ] 主题持久化

---

## 📋 开发优先级

### 第一优先级（P0）- 核心功能

1. Phase 1: 样式系统 + 基础组件
2. Phase 2: 核心布局（Sidebar, MainLayout）
3. Phase 3: Dashboard 页面
4. Phase 3: FuelSystem 页面

### 第二优先级（P1）- 主要功能

5. Phase 3: Journal 页面
6. Phase 3: Settings 页面
7. Phase 3: Timeline 页面

### 第三优先级（P2）- 扩展功能

8. Phase 4: 其他子系统页面
9. Phase 5: 动画与交互优化
10. Phase 5: 性能优化

---

## 🛠️ 技术栈说明

### shadcn/ui 集成

本项目使用 **shadcn/ui**（New York 风格）作为基础组件库：

**优势**：

- ✅ 基于 Radix UI，无障碍支持完善
- ✅ 完全可定制，直接拥有组件代码
- ✅ 与 TailwindCSS 完美集成
- ✅ TypeScript 类型安全
- ✅ 减少重复工作，专注业务逻辑

**使用方式**：

```bash
# 添加组件
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add input
# ... 等等
```

**自定义组件策略**：

- 基础 UI（按钮、输入框、对话框等）→ 使用 shadcn/ui
- 项目特定组件（Sidebar、系统卡片等）→ 自定义开发
- 可使用 shadcn/ui 组件作为构建块

### 其他核心库

- **Recharts** - 雷达图和数据可视化
- **@uiw/react-md-editor** - Markdown 编辑器（日记功能）
- **TanStack Query** - 服务端状态管理（为 API 集成准备）
- **React Hook Form** - 表单管理（设置页面）
- **date-fns** - 日期处理

---

## 🔧 开发规范

### 代码风格

- 使用 TypeScript 严格模式
- 函数组件 + Hooks
- 组件命名：PascalCase
- 文件命名：PascalCase.tsx
- 常量命名：UPPER_SNAKE_CASE
- 使用 Biome 格式化

### 组件使用原则

```typescript
// ✅ 推荐：使用 shadcn/ui 组件
import { Button } from '~/components/ui/button'
import { Card } from '~/components/ui/card'
import { Input } from '~/components/ui/input'

// ✅ 自定义：项目特定组件
import { GlassCard } from '~/components/GlassCard'
import { Sidebar } from '~/components/layout/Sidebar'

// ✅ 组合：基于 shadcn/ui 构建
export const MyCustomCard = () => {
  return (
    <Card className="backdrop-blur-xl bg-white/70">
      <CardHeader>
        <CardTitle>标题</CardTitle>
      </CardHeader>
      <CardContent>
        <Button>点击</Button>
      </CardContent>
    </Card>
  )
}
```

### 组件结构

```tsx
// 1. 导入
import React, { useState } from 'react'
import { SomeComponent } from './components'

// 2. 类型定义
interface Props {
  // ...
}

// 3. 组件定义
export const ComponentName: React.FC<Props> = ({ ... }) => {
  // 3.1 Hooks
  // 3.2 事件处理函数
  // 3.3 渲染逻辑

  return (
    // JSX
  )
}
```

### 样式规范

- 优先使用 TailwindCSS 类名
- 复杂样式使用 CSS 模块或 styled-components
- 响应式设计使用 Tailwind 的响应式前缀
- 深色模式使用 `dark:` 前缀

### 状态管理规范

- 全局状态使用 Context
- 局部状态使用 useState
- 服务端状态使用 TanStack Query
- 表单状态使用 React Hook Form

---

## 📚 参考资源

### UI 设计参考

- UI 设计路径：`/Users/petrel/electron-app/life-canvas-os-ui`
- 核心文件：
  - `App.tsx` - 主应用结构
  - `views/Dashboard.tsx` - 仪表盘
  - `views/FuelSystem.tsx` - 饮食系统
  - `views/Journal.tsx` - 日记系统
  - `views/SettingsView.tsx` - 设置页面
  - `views/TimelineView.tsx` - 时间轴
  - `components/GlassCard.tsx` - 玻璃拟态卡片
  - `constants.tsx` - 常量定义
  - `types.ts` - 类型定义

### 技术文档

- [TailwindCSS 文档](https://tailwindcss.com/)
- [Recharts 文档](https://recharts.org/)
- [Lucide Icons](https://lucide.dev/)
- [React Router v7](https://reactrouter.com/)
- [TanStack Query](https://tanstack.com/query/latest)

---

## ✅ 验收标准

### 功能完整性

- [ ] 所有 5 个主要页面可正常访问
- [ ] 侧边栏导航正常工作
- [ ] 主题切换功能正常
- [ ] PIN 锁定/解锁功能正常
- [ ] 数据可以正常保存到 localStorage

### UI 一致性

- [ ] 所有页面与 UI 设计一致
- [ ] 玻璃拟态效果正确显示
- [ ] 浅色/深色模式无样式问题
- [ ] 动画流畅自然

### 代码质量

- [ ] TypeScript 无类型错误
- [ ] ESLint 无警告
- [ ] 组件结构清晰
- [ ] 代码可维护性高

### 性能

- [ ] 首屏加载时间 < 2s
- [ ] 路由切换流畅
- [ ] 无明显卡顿

---

## 🎉 完成标志

当以下所有条件满足时，前端开发即告完成：

1. ✅ 所有 P0 和 P1 任务完成
2. ✅ 5 个主要页面功能完整
3. ✅ 主题系统工作正常
4. ✅ UI 与设计稿 100% 一致
5. ✅ 通过所有自测用例
6. ✅ 代码通过 TypeScript 类型检查
7. ✅ 性能指标达标

---

**祝开发顺利！🚀**
