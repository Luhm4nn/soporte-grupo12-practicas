'use client'

import { useState } from 'react'
import { uploadAudio } from '@/services/api'

interface UploadState {
  uploading: boolean
  progress: number
  audioId: string | null
  error: string | null
}

export function useUpload() {
  const [state, setState] = useState<UploadState>({
    uploading: false,
    progress: 0,
    audioId: null,
    error: null,
  })

  const upload = async (file: File) => {
    setState({ uploading: true, progress: 0, audioId: null, error: null })
    try {
      const result = await uploadAudio(file, (progress) => {
        setState((prev) => ({ ...prev, progress }))
      })
      setState({ uploading: false, progress: 100, audioId: result.id, error: null })
      return result.id
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Upload failed'
      setState({ uploading: false, progress: 0, audioId: null, error: message })
      return null
    }
  }

  const reset = () => {
    setState({ uploading: false, progress: 0, audioId: null, error: null })
  }

  return { ...state, upload, reset }
}
