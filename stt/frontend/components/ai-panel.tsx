'use client'

import { useState } from 'react'
import {
  Sparkles, MessageSquare, Eraser, ListTodo, Calendar,
  Phone, Mail, Link, Tags, ChevronDown, ChevronUp,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'
import * as api from '@/services/api'
import type { Task } from '@/types/audio'
import { motion, AnimatePresence } from 'framer-motion'
import { TaskList } from './task-list'
import { DataList } from './data-list'

interface AIPanelProps {
  transcription: string
  audioId: string | null
}

type FeatureResult =
  | { type: 'text'; content: string }
  | { type: 'tasks'; content: Task[] }
  | { type: 'list'; content: string[] }

interface ActiveFeature {
  label: string
  loading: boolean
  result: FeatureResult | null
}

export function AIPanel({ transcription, audioId }: AIPanelProps) {
  const [activeFeature, setActiveFeature] = useState<ActiveFeature | null>(null)

  const features = [
    {
      id: 'improve',
      label: 'Mejorar redacción',
      icon: Sparkles,
      action: async () => {
        const result = await api.improveText(transcription)
        return { type: 'text' as const, content: result }
      },
    },
    {
      id: 'fillers',
      label: 'Eliminar muletillas',
      icon: Eraser,
      action: async () => {
        const result = await api.removeFillers(transcription)
        return { type: 'text' as const, content: result }
      },
    },
    {
      id: 'summary-short',
      label: 'Resumen corto',
      icon: MessageSquare,
      action: async () => {
        const result = await api.summarize(transcription, 'short')
        return { type: 'text' as const, content: result }
      },
    },
    {
      id: 'summary-medium',
      label: 'Resumen medio',
      icon: MessageSquare,
      action: async () => {
        const result = await api.summarize(transcription, 'medium')
        return { type: 'text' as const, content: result }
      },
    },
    {
      id: 'summary-detailed',
      label: 'Resumen detallado',
      icon: MessageSquare,
      action: async () => {
        const result = await api.summarize(transcription, 'detailed')
        return { type: 'text' as const, content: result }
      },
    },
    {
      id: 'tasks',
      label: 'Extraer tareas',
      icon: ListTodo,
      action: async () => {
        const result = await api.extractTasks(transcription)
        return { type: 'tasks' as const, content: result }
      },
    },
    {
      id: 'dates',
      label: 'Detectar fechas',
      icon: Calendar,
      action: async () => {
        const result = await api.extractDates(transcription)
        return { type: 'list' as const, content: result }
      },
    },
    {
      id: 'phones',
      label: 'Detectar teléfonos',
      icon: Phone,
      action: async () => {
        const result = await api.extractPhones(transcription)
        return { type: 'list' as const, content: result }
      },
    },
    {
      id: 'emails',
      label: 'Detectar emails',
      icon: Mail,
      action: async () => {
        const result = await api.extractEmails(transcription)
        return { type: 'list' as const, content: result }
      },
    },
    {
      id: 'links',
      label: 'Detectar links',
      icon: Link,
      action: async () => {
        const result = await api.extractLinks(transcription)
        return { type: 'list' as const, content: result }
      },
    },
    {
      id: 'tags',
      label: 'Etiquetas automáticas',
      icon: Tags,
      action: async () => {
        const result = await api.extractTags(transcription)
        return { type: 'list' as const, content: result }
      },
    },
  ]

  const runFeature = async (feature: typeof features[0]) => {
    setActiveFeature({ label: feature.label, loading: true, result: null })
    try {
      const result = await feature.action()
      setActiveFeature({ label: feature.label, loading: false, result })
      toast.success(`${feature.label} completado`)
    } catch {
      setActiveFeature(null)
      toast.error(`Error al ejecutar ${feature.label}`)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {features.map((feature) => (
          <button
            key={feature.id}
            onClick={() => runFeature(feature)}
            disabled={activeFeature?.loading}
            className={cn(
              'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium',
              'border bg-card hover:bg-secondary transition-colors disabled:opacity-50',
            )}
          >
            <feature.icon className="h-4 w-4" />
            {feature.label}
          </button>
        ))}
      </div>

      <AnimatePresence>
        {activeFeature && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="p-4 rounded-xl border bg-card">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm font-medium">{activeFeature.label}</p>
                <button
                  onClick={() => setActiveFeature(null)}
                  className="p-1 rounded-md hover:bg-secondary transition-colors"
                >
                  <ChevronUp className="h-4 w-4" />
                </button>
              </div>

              {activeFeature.loading ? (
                <div className="space-y-2">
                  <div className="h-4 w-full shimmer rounded" />
                  <div className="h-4 w-3/4 shimmer rounded" />
                </div>
              ) : activeFeature.result?.type === 'text' ? (
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{activeFeature.result.content}</p>
              ) : activeFeature.result?.type === 'tasks' ? (
                <TaskList tasks={activeFeature.result.content} />
              ) : activeFeature.result?.type === 'list' ? (
                <DataList items={activeFeature.result.content} />
              ) : null}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
