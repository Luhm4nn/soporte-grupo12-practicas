'use client'

import { Navbar } from '@/components/navbar'
import { AudioPlayer } from '@/components/audio-player'
import { TranscriptionView } from '@/components/transcription-view'
import { ActionBar } from '@/components/action-bar'
import { TagsChips } from '@/components/tags-chips'
import { AIPanel } from '@/components/ai-panel'
import { ChatInterface } from '@/components/chat-interface'
import { SkeletonCard } from '@/components/skeleton-card'
import { useAudio } from '@/hooks/use-audio'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { FileText, MessageSquare } from 'lucide-react'
import { motion } from 'framer-motion'

export default function AudioPage({ params }: { params: { id: string } }) {
  const { id } = params
  const { data: audio, isLoading, error } = useAudio(id)

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 py-8 px-4">
          <SkeletonCard />
        </main>
      </div>
    )
  }

  if (error || !audio) {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <p className="text-muted-foreground">Audio no encontrado</p>
        </main>
      </div>
    )
  }

  if (audio.status === 'pending' || audio.status === 'processing') {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 py-8 px-4">
          <div className="max-w-3xl mx-auto text-center space-y-4">
            <SkeletonCard />
            <p className="text-sm text-muted-foreground animate-pulse">
              Procesando audio...
            </p>
          </div>
        </main>
      </div>
    )
  }

  if (audio.status === 'failed') {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center space-y-2">
            <p className="text-destructive font-medium">Error al procesar el audio</p>
            <p className="text-sm text-muted-foreground">{audio.error_message}</p>
          </div>
        </main>
      </div>
    )
  }

  const transcriptionText = audio.transcription_text || ''
  const audioUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/audio/file/${audio.id}`

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 py-8 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-3xl mx-auto space-y-6"
        >
          <div>
            <h1 className="text-xl font-semibold truncate">{audio.original_name}</h1>
            {audio.duration && (
              <p className="text-sm text-muted-foreground">
                Duración: {Math.floor(audio.duration / 60)}:{(audio.duration % 60).toFixed(0).padStart(2, '0')}
                {audio.language && ` · Idioma: ${audio.language}`}
              </p>
            )}
          </div>

          <TagsChips tags={audio.tags || []} />

          <div className="p-4 sm:p-6 rounded-xl border bg-card">
            <AudioPlayer src={audioUrl} />
          </div>

          <Tabs defaultValue="transcription">
            <TabsList>
              <TabsTrigger value="transcription">
                <FileText className="h-4 w-4 mr-1.5" />
                Transcripción
              </TabsTrigger>
              <TabsTrigger value="chat">
                <MessageSquare className="h-4 w-4 mr-1.5" />
                Preguntar sobre este audio
              </TabsTrigger>
            </TabsList>

            <TabsContent value="transcription" className="space-y-6 mt-6">
              <div className="p-4 sm:p-6 rounded-xl border bg-card">
                <TranscriptionView text={transcriptionText} />
              </div>

              <ActionBar text={transcriptionText} />

              <div>
                <h2 className="text-sm font-medium mb-3">Funciones de IA</h2>
                <AIPanel transcription={transcriptionText} audioId={id} />
              </div>
            </TabsContent>

            <TabsContent value="chat" className="mt-6">
              <ChatInterface audioId={id} />
            </TabsContent>
          </Tabs>
        </motion.div>
      </main>
    </div>
  )
}
