import {
  ChevronRight,
  Settings,
  PanelLeftClose,
  PanelLeft,
  Bot,
} from 'lucide-react'
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from '~/renderer/components/ui/avatar'
import { NAV_ITEMS } from '~/renderer/lib/constants'
import { useNavigate } from 'react-router-dom'
import { useApp } from '~/renderer/contexts/AppContext'
import { cn } from '~/renderer/lib/utils'

interface SidebarProps {
  activeTab: string
  onTabChange: (tab: string) => void
  isCollapsed: boolean
  onToggleCollapse: () => void
}

export function Sidebar({
  activeTab,
  onTabChange,
  isCollapsed,
  onToggleCollapse,
}: SidebarProps) {
  const navigate = useNavigate()
  const { state } = useApp()

  const handleTabClick = (tabId: string) => {
    onTabChange(tabId)
    // 导航到对应路由
    const routeMap: Record<string, string> = {
      dashboard: '/dashboard',
      fuel: '/system/fuel',
      journal: '/journal',
      timeline: '/timeline',
      agent: '/agent',
    }
    navigate(routeMap[tabId] || '/dashboard')
  }

  return (
    <aside
      className={cn(
        'sidebar-glass liquid-glass h-screen border-r border-apple-border dark:border-white/5 flex flex-col z-10 transition-all duration-300 ease-in-out relative',
        isCollapsed ? 'w-20' : 'w-72'
      )}
    >
      {/* 伸缩按钮 - 顶部左侧 */}
      <div className="px-4 py-1 border-b border-apple-border dark:border-white/5">
        <button
          className={cn(
            'w-full rounded-lg flex items-center hover:bg-black/5 dark:hover:bg-white/5 text-apple-textSec dark:text-white/40 hover:text-apple-textMain dark:hover:text-white transition-all',
            isCollapsed ? 'px-2 py-3 justify-center' : 'px-4 py-3'
          )}
          onClick={onToggleCollapse}
          title={isCollapsed ? '展开侧边栏' : '收缩侧边栏'}
        >
          <div className="flex items-center justify-center">
            {isCollapsed ? (
              <PanelLeft className="w-5 h-5 shrink-0" />
            ) : (
              <PanelLeftClose className="w-5 h-5 shrink-0" />
            )}
          </div>
        </button>
      </div>

      {/* 导航菜单 */}
      <nav className="flex-1 space-y-2 p-4">
        {NAV_ITEMS.map(item => (
          <button
            className={cn(
              'w-full flex items-center justify-between rounded-xl transition-all group',
              isCollapsed ? 'px-2 py-3 justify-center' : 'px-4 py-3',
              activeTab === item.id
                ? 'bg-apple-accent/10 dark:bg-white/10 text-apple-accent dark:text-white border border-apple-accent/10 dark:border-white/10'
                : 'text-apple-textSec dark:text-white/40 hover:text-apple-textMain dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5'
            )}
            key={item.id}
            onClick={() => handleTabClick(item.id)}
            title={isCollapsed ? item.label : undefined}
          >
            <div className="flex items-center gap-3 font-medium">
              {item.icon}
              {!isCollapsed && <span>{item.label}</span>}
            </div>
            {!isCollapsed && activeTab === item.id && (
              <ChevronRight className="text-apple-accent" size={16} />
            )}
          </button>
        ))}
      </nav>

      {/* 用户信息入口 - 点击跳转到设置页 */}
      <div
        className={cn(
          'mt-auto border-t border-apple-border dark:border-white/10',
          isCollapsed ? 'p-2 pt-4' : 'p-6 pt-6'
        )}
      >
        {state.user.name ? (
          <button
            className={cn(
              'w-full flex items-center rounded-xl transition-all',
              isCollapsed
                ? 'justify-center px-2 py-2'
                : 'gap-3 px-2 hover:bg-black/5 dark:hover:bg-white/5'
            )}
            onClick={() => navigate('/settings')}
            title={isCollapsed ? '设置' : undefined}
          >
            {isCollapsed ? (
              <div className="w-11 h-11 rounded-full bg-apple-bg2 dark:bg-white/10 flex items-center justify-center shrink-0">
                <Settings
                  className="text-apple-textSec dark:text-white/40"
                  size={20}
                />
              </div>
            ) : (
              <>
                <Avatar className="w-11 h-11 rounded-full bg-gradient-to-br from-apple-accent to-blue-600 border-2 border-white dark:border-white/20 shadow-lg shrink-0">
                  <AvatarImage
                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${state.user.name}`}
                  />
                  <AvatarFallback className="bg-gradient-to-br from-apple-accent to-blue-600 text-white font-bold text-base">
                    {state.user.name.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0 text-left">
                  <div className="text-sm font-semibold truncate text-apple-textMain dark:text-white">
                    {state.user.name}
                  </div>
                  <div className="text-xs text-apple-textTer dark:text-white/40 truncate">
                    {state.user.mbti} • {state.user.lifespan}岁
                  </div>
                </div>
                <div className="w-9 h-9 flex items-center justify-center rounded-lg text-apple-textSec hover:text-apple-textMain dark:text-white/40 dark:hover:text-white hover:bg-apple-bgHover dark:hover:bg-white/10 transition-all">
                  <Settings size={18} />
                </div>
              </>
            )}
          </button>
        ) : (
          <button
            className={cn(
              'w-full flex items-center rounded-xl transition-all',
              isCollapsed
                ? 'justify-center px-2 py-2'
                : 'gap-3 px-2 hover:bg-black/5 dark:hover:bg-white/5'
            )}
            onClick={() => navigate('/settings')}
            title={isCollapsed ? '设置' : undefined}
          >
            <div className="w-11 h-11 rounded-full bg-apple-bg2 dark:bg-white/10 flex items-center justify-center shrink-0">
              <Settings
                className="text-apple-textSec dark:text-white/40"
                size={20}
              />
            </div>
            {!isCollapsed && (
              <div className="flex-1 min-w-0 text-left">
                <div className="text-sm font-semibold truncate text-apple-textMain dark:text-white">
                  设置
                </div>
                <div className="text-xs text-apple-textTer dark:text-white/40">
                  配置系统偏好
                </div>
              </div>
            )}
            {!isCollapsed && (
              <ChevronRight
                className="text-apple-textTer dark:text-white/20 shrink-0"
                size={16}
              />
            )}
          </button>
        )}
      </div>
    </aside>
  )
}
