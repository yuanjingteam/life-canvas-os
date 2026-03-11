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

export interface AppAPI {
  sayHelloFromBridge(): void
  username: string | undefined
  fileOps: FileOpsAPI
}

declare global {
  interface Window {
    App: AppAPI
  }
}
