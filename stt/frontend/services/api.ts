import axios from 'axios'
import type { AudioUploadResponse, AudioData, Task, ChatMessage } from '@/types/audio'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
})

export async function uploadAudio(file: File, onProgress?: (progress: number) => void): Promise<AudioUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post<AudioUploadResponse>('/audio/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    },
  })
  return response.data
}

export async function getAudio(id: string): Promise<AudioData> {
  const response = await api.get<AudioData>(`/audio/${id}`)
  return response.data
}

export async function improveText(text: string): Promise<string> {
  const response = await api.post<{ improved_text: string }>('/audio/improve', { text })
  return response.data.improved_text
}

export async function removeFillers(text: string): Promise<string> {
  const response = await api.post<{ cleaned_text: string }>('/audio/remove-fillers', { text })
  return response.data.cleaned_text
}

export async function summarize(text: string, level: 'short' | 'medium' | 'detailed' = 'medium'): Promise<string> {
  const response = await api.post<{ summary: string }>('/audio/summarize', { text, level })
  return response.data.summary
}

export async function extractTasks(text: string): Promise<Task[]> {
  const response = await api.post<{ tasks: Task[] }>('/audio/tasks', { text })
  return response.data.tasks
}

export async function extractDates(text: string): Promise<string[]> {
  const response = await api.post<{ dates: string[] }>('/audio/dates', { text })
  return response.data.dates
}

export async function extractPhones(text: string): Promise<string[]> {
  const response = await api.post<{ phones: string[] }>('/audio/phones', { text })
  return response.data.phones
}

export async function extractEmails(text: string): Promise<string[]> {
  const response = await api.post<{ emails: string[] }>('/audio/emails', { text })
  return response.data.emails
}

export async function extractLinks(text: string): Promise<string[]> {
  const response = await api.post<{ links: string[] }>('/audio/links', { text })
  return response.data.links
}

export async function extractTags(text: string): Promise<string[]> {
  const response = await api.post<{ tags: string[] }>('/audio/tags', { text })
  return response.data.tags
}

export async function chatAboutAudio(audioId: string, question: string): Promise<string> {
  const response = await api.post<{ answer: string }>(`/audio/${audioId}/chat`, {
    transcription_id: audioId,
    question,
  })
  return response.data.answer
}
