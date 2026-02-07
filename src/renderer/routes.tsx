import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from '~/renderer/components/layout/MainLayout';

// 页面组件（暂时使用占位符）
function PlaceholderPage({ name }: { name: string }) {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div>
        <h1 className="text-4xl font-black text-apple-textMain dark:text-white tracking-tight">
          {name}
        </h1>
        <p className="text-apple-textSec dark:text-white/40 mt-2 text-lg">
          此页面正在开发中...
        </p>
      </div>

      <div className="glass-effect rounded-2xl p-8 text-center">
        <p className="text-apple-textSec dark:text-white/60">
          💡 敬请期待更多功能
        </p>
      </div>
    </div>
  );
}

export function AppRoutes() {
  return (
    <HashRouter>
      <Routes>
        {/* 默认重定向到 dashboard */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        {/* 主应用路由（带布局） */}
        <Route element={<MainLayout />}>
          <Route path="/dashboard" element={<PlaceholderPage name="全局总览" />} />
          <Route path="/system/fuel" element={<PlaceholderPage name="饮食系统" />} />
          <Route path="/journal" element={<PlaceholderPage name="生活日记" />} />
          <Route path="/journal/:id" element={<PlaceholderPage name="日记详情" />} />
          <Route path="/timeline" element={<PlaceholderPage name="审计时间轴" />} />
          <Route path="/settings" element={<PlaceholderPage name="系统设置" />} />
          <Route path="/system/:type" element={<PlaceholderPage name="子系统详情" />} />
        </Route>
      </Routes>
    </HashRouter>
  );
}
