'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { Mic, Square, RotateCcw, Send, Loader2 } from 'lucide-react'
import { cn, formatDuration } from '@/lib/utils'
import { motion } from 'framer-motion'

interface AudioRecorderProps {
  onRecord: (file: File) => void
  disabled?: boolean
}

type RecorderStatus = 'idle' | 'recording' | 'recorded'

const MIME_TYPES = [
  'audio/webm;codecs=opus',
  'audio/webm',
  'audio/mp4',
]

export function AudioRecorder({ onRecord, disabled }: AudioRecorderProps) {
  const [status, setStatus] = useState<RecorderStatus>('idle')
  const [error, setError] = useState<string | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }, [])

  const cleanupStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop())
    streamRef.current = null
  }, [])

  useEffect(() => {
    return () => {
      stopTimer()
      cleanupStream()
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [stopTimer, cleanupStream, previewUrl])

  const startRecording = async () => {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const mimeType = MIME_TYPES.find((type) => MediaRecorder.isTypeSupported(type)) || ''
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)

      chunksRef.current = []
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || 'audio/webm' })
        const url = URL.createObjectURL(blob)
        if (previewUrl) URL.revokeObjectURL(previewUrl)
        setPreviewUrl(url)
        setStatus('recorded')
      }

      mediaRecorderRef.current = recorder
      recorder.start()
      setElapsed(0)
      setStatus('recording')
      timerRef.current = setInterval(() => setElapsed((prev) => prev + 1), 1000)
    } catch (err) {
      setError(
        err instanceof DOMException && err.name === 'NotAllowedError'
          ? 'Permiso de micrófono denegado. Habilitalo y volvé a intentar.'
          : 'No se pudo acceder al micrófono.',
      )
    }
  }

  const stopRecording = () => {
    stopTimer()
    mediaRecorderRef.current?.stop()
    cleanupStream()
  }

  const discard = () => {
    stopTimer()
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
    }
    setElapsed(0)
    setStatus('idle')
  }

  const submit = async () => {
    if (!previewUrl) return
    const blob = await fetch(previewUrl).then((r) => r.blob())
    const ext = blob.type.includes('mp4') ? 'm4a' : 'webm'
    const file = new File([blob], `grabacion-${Date.now()}.${ext}`, { type: blob.type })
    setSubmitting(true)
    onRecord(file)
  }

  const formatted = formatDuration(elapsed)

  return (
    <div className="flex flex-col items-center justify-center w-full max-w-xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full flex flex-col items-center gap-6 p-10 rounded-2xl border-2 border-dashed border-muted-foreground/25"
      >
        <div className="text-center space-y-1">
          <p className="text-lg font-medium">Grabá un audio</p>
          <p className="text-sm text-muted-foreground">
            {status === 'recording'
              ? 'Estás grabando...'
              : status === 'recorded'
                ? 'Escuchá y enviá tu grabación'
                : 'Apretá el botón y empezá a hablar'}
          </p>
        </div>

        {status === 'recording' && (
          <div className="flex items-center gap-2 text-sm font-mono">
            <span className="h-2.5 w-2.5 rounded-full bg-destructive animate-pulse" />
            {formatted}
          </div>
        )}

        {status === 'idle' && (
          <button
            onClick={startRecording}
            disabled={disabled}
            className={cn(
              'group relative flex h-20 w-20 items-center justify-center rounded-full bg-primary text-primary-foreground transition-all',
              'hover:scale-105 active:scale-95 disabled:opacity-50 disabled:pointer-events-none',
            )}
            aria-label="Comenzar a grabar"
          >
            <Mic className="h-9 w-9" />
            <span className="absolute inset-0 rounded-full ring-4 ring-primary/30 animate-ping" style={{ animationDuration: '2.5s' }} />
          </button>
        )}

        {status === 'recording' && (
          <button
            onClick={stopRecording}
            disabled={disabled}
            className="flex h-20 w-20 items-center justify-center rounded-full bg-destructive text-white transition-all hover:scale-105 active:scale-95"
            aria-label="Detener grabación"
          >
            <Square className="h-8 w-8 fill-current" />
          </button>
        )}

        {status === 'recorded' && previewUrl && (
          <div className="w-full space-y-4">
            <audio controls src={previewUrl} className="w-full" />
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={discard}
                className="flex items-center gap-2 px-4 py-2 rounded-lg border text-sm hover:bg-muted transition-colors"
              >
                <RotateCcw className="h-4 w-4" />
                Volver a grabar
              </button>
              <button
                onClick={submit}
                disabled={submitting || disabled}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm hover:opacity-90 transition-opacity disabled:opacity-50 disabled:pointer-events-none"
              >
                {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                Transcribir
              </button>
            </div>
          </div>
        )}

        {error && (
          <p className="text-sm text-destructive text-center">{error}</p>
        )}
      </motion.div>
    </div>
  )
}
