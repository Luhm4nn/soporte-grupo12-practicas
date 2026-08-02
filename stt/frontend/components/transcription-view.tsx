'use client'

import { motion } from 'framer-motion'

interface TranscriptionViewProps {
  text: string
}

export function TranscriptionView({ text }: TranscriptionViewProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="prose prose-sm dark:prose-invert max-w-none"
    >
      <p className="text-base leading-relaxed whitespace-pre-wrap select-text">
        {text}
      </p>
    </motion.div>
  )
}
