'use client'

import { cn } from '@/lib/utils'

export function SkeletonCard() {
  return (
    <div className="w-full max-w-3xl mx-auto space-y-4 p-6">
      <div className="h-8 w-48 shimmer rounded-lg" />
      <div className="h-40 shimmer rounded-xl" />
      <div className="space-y-2">
        <div className="h-4 w-full shimmer rounded" />
        <div className="h-4 w-3/4 shimmer rounded" />
        <div className="h-4 w-5/6 shimmer rounded" />
        <div className="h-4 w-2/3 shimmer rounded" />
      </div>
      <div className="flex gap-2">
        <div className="h-8 w-20 shimmer rounded-lg" />
        <div className="h-8 w-24 shimmer rounded-lg" />
        <div className="h-8 w-16 shimmer rounded-lg" />
      </div>
    </div>
  )
}
