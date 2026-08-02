'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { Play, Pause, SkipBack, SkipForward, ChevronDown } from 'lucide-react'
import { cn, formatDuration } from '@/lib/utils'

const SPEEDS = [0.75, 1, 1.25, 1.5, 2]

interface AudioPlayerProps {
  src: string
  onReady?: () => void
}

export function AudioPlayer({ src, onReady }: AudioPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const wavesurferRef = useRef<any>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [speed, setSpeed] = useState(1)
  const [showSpeedMenu, setShowSpeedMenu] = useState(false)

  useEffect(() => {
    let mounted = true
    const init = async () => {
      const WaveSurfer = (await import('wavesurfer.js')).default
      if (!containerRef.current || !mounted) return

      const ws = WaveSurfer.create({
        container: containerRef.current,
        waveColor: 'hsl(var(--muted-foreground) / 0.3)',
        progressColor: 'hsl(var(--primary))',
        cursorColor: 'transparent',
        barWidth: 3,
        barGap: 2,
        barRadius: 3,
        height: 64,
        normalize: true,
        backend: 'WebAudio',
      })

      ws.load(src)

      ws.on('ready', () => {
        if (!mounted) return
        setDuration(ws.getDuration())
        onReady?.()
      })

      ws.on('audioprocess', () => {
        if (!mounted) return
        setCurrentTime(ws.getCurrentTime())
      })

      ws.on('play', () => mounted && setIsPlaying(true))
      ws.on('pause', () => mounted && setIsPlaying(false))

      wavesurferRef.current = ws
    }

    init()

    return () => {
      mounted = false
      wavesurferRef.current?.destroy()
    }
  }, [src])

  const togglePlay = useCallback(() => {
    wavesurferRef.current?.playPause()
  }, [])

  const skip = useCallback((seconds: number) => {
    const ws = wavesurferRef.current
    if (ws) {
      const newTime = Math.max(0, Math.min(ws.getCurrentTime() + seconds, ws.getDuration()))
      ws.setTime(newTime)
      setCurrentTime(newTime)
    }
  }, [])

  const changeSpeed = useCallback((newSpeed: number) => {
    setSpeed(newSpeed)
    wavesurferRef.current?.setPlaybackRate(newSpeed)
    setShowSpeedMenu(false)
  }, [])

  return (
    <div className="w-full space-y-3">
      <div ref={containerRef} className="w-full" />

      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-1">
          <button
            onClick={() => skip(-10)}
            className="p-2 rounded-lg hover:bg-secondary transition-colors"
            title="Retroceder 10s"
          >
            <SkipBack className="h-4 w-4" />
          </button>

          <button
            onClick={togglePlay}
            className="p-3 rounded-full bg-primary text-primary-foreground hover:opacity-90 transition-all"
          >
            {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
          </button>

          <button
            onClick={() => skip(10)}
            className="p-2 rounded-lg hover:bg-secondary transition-colors"
            title="Adelantar 10s"
          >
            <SkipForward className="h-4 w-4" />
          </button>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground tabular-nums">
          <span>{formatDuration(currentTime)}</span>
          <span>/</span>
          <span>{formatDuration(duration)}</span>
        </div>

        <div className="relative">
          <button
            onClick={() => setShowSpeedMenu(!showSpeedMenu)}
            className="px-2 py-1 rounded-lg text-xs font-medium hover:bg-secondary transition-colors flex items-center gap-1"
          >
            {speed}x
            <ChevronDown className="h-3 w-3" />
          </button>
          {showSpeedMenu && (
            <div className="absolute bottom-full right-0 mb-1 p-1 rounded-lg border bg-card shadow-lg">
              {SPEEDS.map((s) => (
                <button
                  key={s}
                  onClick={() => changeSpeed(s)}
                  className={cn(
                    'block w-full px-3 py-1.5 text-xs rounded-md transition-colors text-left',
                    speed === s ? 'bg-primary text-primary-foreground' : 'hover:bg-secondary',
                  )}
                >
                  {s}x
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
