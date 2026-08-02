'use client'

import { useQuery } from '@tanstack/react-query'
import { getAudio } from '@/services/api'
import type { AudioData } from '@/types/audio'

export function useAudio(id: string | null) {
  return useQuery<AudioData>({
    queryKey: ['audio', id],
    queryFn: () => getAudio(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      const data = query.state.data
      if (data?.status === 'completed' || data?.status === 'failed') return false
      return 2000
    },
  })
}
