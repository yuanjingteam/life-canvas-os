import { contextBridge, ipcRenderer } from 'electron'

declare global {
  interface Window {
    App: typeof API
  }
}

const API = {
  sayHelloFromBridge: () => console.log('\nHello from bridgeAPI! 👋\n\n'),
  username: process.env.USER,
  // 文件操作 API
  fileOps: {
    // 选择文件并复制到后端可访问目录
    selectAndCopyFile: () => ipcRenderer.invoke('file:select-and-copy'),
    // 保存导出数据到指定路径
    saveExportData: (fileData: Uint8Array, format: 'json' | 'zip') =>
      ipcRenderer.invoke('file:save-export-data', fileData, format),
  },
}

contextBridge.exposeInMainWorld('App', API)
