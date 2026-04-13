import { lazy, Suspense } from 'react'
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom'
import { MainLayout } from '~/renderer/components/layout/MainLayout'
import { PageLoading } from '~/renderer/components/ui/PageLoading'

// 懒加载页面组件（使用命名导出）
const DashboardPage = lazy(() =>
  import('~/renderer/pages/dashboard/DashboardPage').then(m => ({
    default: m.DashboardPage,
  }))
)
const FuelSystemPage = lazy(() =>
  import('~/renderer/pages/systems/FuelSystemPage').then(m => ({
    default: m.FuelSystemPage,
  }))
)
const AssetOverviewPage = lazy(() =>
  import('~/renderer/pages/assets/AssetOverviewPage').then(m => ({
    default: m.default,
  }))
)
const AssetCategoryDetailPage = lazy(() =>
  import('~/renderer/pages/assets/AssetCategoryDetailPage').then(m => ({
    default: m.default,
  }))
)
const JournalPage = lazy(() =>
  import('~/renderer/pages/journal/JournalPage').then(m => ({
    default: m.JournalPage,
  }))
)

const TimelinePage = lazy(() =>
  import('~/renderer/pages/timeline/TimelinePage').then(m => ({
    default: m.TimelinePage,
  }))
)
const SettingsPage = lazy(() =>
  import('~/renderer/pages/settings/SettingsPage').then(m => ({
    default: m.SettingsPage,
  }))
)
const PinSetupPage = lazy(() =>
  import('~/renderer/pages/settings/PinSetupPage').then(m => ({
    default: m.PinSetupPage,
  }))
)
const PinChangePage = lazy(() =>
  import('~/renderer/pages/settings/PinChangePage').then(m => ({
    default: m.PinChangePage,
  }))
)
const PinDeletePage = lazy(() =>
  import('~/renderer/pages/settings/PinDeletePage').then(m => ({
    default: m.PinDeletePage,
  }))
)
const InsightDetailPage = lazy(() =>
  import('~/renderer/pages/insight/InsightDetailPage').then(m => ({
    default: m.InsightDetailPage,
  }))
)
const InsightHistoryPage = lazy(() =>
  import('~/renderer/pages/insight/InsightHistoryPage').then(m => ({
    default: m.InsightHistoryPage,
  }))
)
const InsightHistoryDetailPage = lazy(() =>
  import('~/renderer/pages/insight/InsightHistoryDetailPage').then(m => ({
    default: m.InsightHistoryDetailPage,
  }))
)
const AgentPage = lazy(() =>
  import('~/renderer/pages/agent/AgentPage').then(m => ({
    default: m.AgentPage,
  }))
)

export function AppRoutes() {
  return (
    <HashRouter>
      <Routes>
        {/* 默认重定向到 dashboard */}
        <Route element={<Navigate replace to="/dashboard" />} path="/" />

        {/* 主应用路由（带布局） */}
        <Route element={<MainLayout />}>
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <DashboardPage />
              </Suspense>
            }
            path="/dashboard"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <AssetCategoryDetailPage />
              </Suspense>
            }
            path="/asset/categories/:category"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <AssetOverviewPage />
              </Suspense>
            }
            path="/asset"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <FuelSystemPage />
              </Suspense>
            }
            path="/system/fuel"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <JournalPage />
              </Suspense>
            }
            path="/journal"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <TimelinePage />
              </Suspense>
            }
            path="/timeline"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <SettingsPage />
              </Suspense>
            }
            path="/settings"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <PinSetupPage />
              </Suspense>
            }
            path="/settings/pin"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <PinChangePage />
              </Suspense>
            }
            path="/settings/pin/change"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <PinDeletePage />
              </Suspense>
            }
            path="/settings/pin/delete"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <InsightDetailPage />
              </Suspense>
            }
            path="/insights/detail"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <InsightHistoryPage />
              </Suspense>
            }
            path="/insights/history"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <InsightHistoryDetailPage />
              </Suspense>
            }
            path="/insights/history/detail"
          />
          <Route
            element={
              <Suspense fallback={<PageLoading />}>
                <AgentPage />
              </Suspense>
            }
            path="/agent"
          />
          <Route
            element={<Navigate replace to="/dashboard" />}
            path="/system/:type"
          />
        </Route>
      </Routes>
    </HashRouter>
  )
}
