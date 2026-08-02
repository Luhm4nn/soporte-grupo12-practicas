'use client'

import { motion } from 'framer-motion'

const TAG_COLORS: Record<string, string> = {
  Trabajo: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  Facultad: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
  Personal: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  Cliente: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
  Ventas: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
  Compras: 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300',
  Urgente: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  Recordatorio: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-300',
  Reunión: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
  Ideas: 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-300',
}

interface TagsChipsProps {
  tags: string[]
}

export function TagsChips({ tags }: TagsChipsProps) {
  if (!tags?.length) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-wrap gap-2"
    >
      {tags.map((tag) => (
        <span
          key={tag}
          className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${TAG_COLORS[tag] || 'bg-secondary text-secondary-foreground'}`}
        >
          {tag}
        </span>
      ))}
    </motion.div>
  )
}
