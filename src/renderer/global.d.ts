/**
 * 全局类型定义
 */

export interface FileOpsAPI {
  /**
   * 选择文件并复制到后端可访问目录
   */
  selectAndCopyFile(): Promise<{ canceled: boolean; filePath?: string }>

  /**
   * 保存导出数据到指定路径
   */
  saveExportData(
    fileData: Uint8Array,
    format: 'json' | 'zip'
  ): Promise<{ canceled: boolean; filePath?: string; success?: boolean }>

  /**
   * 下载文件（读取文件并返回二进制数据）
   */
  downloadFile(
    filePath: string
  ): Promise<{ success: boolean; data?: Buffer; error?: string }>
}

export interface MigrateAPI {
  /** 选择数据目录（通过系统对话框） */
  selectDirectory(): Promise<{ canceled: boolean; dirPath?: string }>
  /** 获取当前数据目录 */
  getDataDir(): Promise<string>
  /** 保存数据目录配置 */
  saveConfig(newDataDir: string): Promise<{ success: boolean }>
  /** 重启 Python 后端 */
  restartBackend(): Promise<{ success: boolean; error?: string }>
}

export interface AppAPI {
  sayHelloFromBridge(): void
  username: string | undefined
  fileOps: FileOpsAPI
  migrate: MigrateAPI
}

declare global {
  interface Window {
    App: AppAPI
  }
}
