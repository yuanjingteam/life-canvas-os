/**
 * 日记相关 API
 */

import { API_BASE_URL } from './config';

export interface JournalCreateRequest {
  title: string;
  content: string;
  mood: string;
  tags: string[];
  linkedDimensions: string[];
  isPrivate: boolean;
  attachments: string[];
}

export interface JournalUpdateRequest extends Partial<JournalCreateRequest> {}

export const journalApi = {
  list(): Promise<Response> {
    return fetch(`${API_BASE_URL}/api/journals`);
  },

  get(id: string): Promise<Response> {
    return fetch(`${API_BASE_URL}/api/journals/${id}`);
  },

  create(data: JournalCreateRequest): Promise<Response> {
    return fetch(`${API_BASE_URL}/api/journals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  update(id: string, data: JournalUpdateRequest): Promise<Response> {
    return fetch(`${API_BASE_URL}/api/journals/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  delete(id: string): Promise<Response> {
    return fetch(`${API_BASE_URL}/api/journals/${id}`, {
      method: 'DELETE',
    });
  },
};
