/**
 * PIN 相关 API
 */

import { apiRequest } from './client'
import type {
  PinVerifyRequest,
  PinChangeRequest,
  PinDeleteRequest,
  PinSetupRequest,
} from '../lib/pin/types'

export interface PinVerifyRequirements {
  has_pin: boolean
  requirements: {
    startup: boolean
    private_journal: boolean
    data_export: boolean
    settings_change: boolean
  }
}

export const pinApi = {
  /**
   * 获取 PIN 验证要求（新接口）
   */
  verifyRequirements(): Promise<Response> {
    return apiRequest('/api/pin/verify-requirements')
  },

  setup(pin: string): Promise<Response> {
    return apiRequest('/api/pin/setup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pin } as PinSetupRequest),
    })
  },

  verify(pin: string): Promise<Response> {
    return apiRequest('/api/pin/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pin } as PinVerifyRequest),
    })
  },

  change(oldPin: string, newPin: string): Promise<Response> {
    return apiRequest('/api/pin/change', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        old_pin: oldPin,
        new_pin: newPin,
      } as PinChangeRequest),
    })
  },

  delete(pin: string): Promise<Response> {
    return apiRequest('/api/pin', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pin } as PinDeleteRequest),
    })
  },
}
