import { contextBridge, ipcRenderer } from 'electron'

declare global {
  interface Window {
    App: typeof API
    electron: typeof ElectronAPI
  }
}

const API = {
  sayHelloFromBridge: () => console.log('\nHello from bridgeAPI! 👋\n\n'),

  // 文件操作 API
  fileOps: {
    // 选择文件并复制到后端可访问目录
    selectAndCopyFile: () => ipcRenderer.invoke('file:select-and-copy'),
    // 保存导出数据到指定路径
    saveExportData: (fileData: Uint8Array, format: 'json' | 'zip') =>
      ipcRenderer.invoke('file:save-export-data', fileData, format),
    // 下载文件（读取文件并返回二进制数据）
    downloadFile: (filePath: string) =>
      ipcRenderer.invoke('file:download', filePath),
    // 选择目录
    selectDirectory: () => ipcRenderer.invoke('directory:select'),
  },

  // 通用 API 请求（通过 IPC 转发到 Python 后端）
  request: (action: string, params: any = {}) =>
    ipcRenderer.invoke('api:request', action, params),

  // 数据迁移 API
  migrate: {
    // 选择数据目录（通过系统对话框）
    selectDirectory: () => ipcRenderer.invoke('migrate:select-directory'),
    // 获取当前数据目录
    getDataDir: () => ipcRenderer.invoke('migrate:get-data-dir'),
    // 保存数据目录配置
    saveConfig: (newDataDir: string) =>
      ipcRenderer.invoke('migrate:save-config', newDataDir),
    // 重启 Python 后端
    restartBackend: () => ipcRenderer.invoke('migrate:restart-backend'),
  },
}

// Electron 事件监听 API（用于 IPC 流式事件）
const ElectronAPI = {
  // 监听事件
  on: (channel: string, callback: (event: any, data: any) => void) => {
    const listener = (event: any, data: any) => callback(event, data)
    ipcRenderer.on(channel, listener)
    return () => ipcRenderer.removeListener(channel, listener)
  },
  // 移除监听器
  removeListener: (
    channel: string,
    callback: (event: any, data: any) => void
  ) => {
    ipcRenderer.removeListener(channel, callback)
  },
  // 移除所有监听器
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel)
  },
}

contextBridge.exposeInMainWorld('App', API)
contextBridge.exposeInMainWorld('electron', ElectronAPI)
