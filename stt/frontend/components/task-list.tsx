'use client'

import { useState } from 'react'
import { Checkbox } from './ui/checkbox'
import type { Task } from '@/types/audio'

interface TaskListProps {
  tasks: Task[]
}

export function TaskList({ tasks }: TaskListProps) {
  const [checked, setChecked] = useState<Set<number>>(new Set())

  const toggle = (idx: number) => {
    setChecked((prev) => {
      const next = new Set(prev)
      if (next.has(idx)) next.delete(idx)
      else next.add(idx)
      return next
    })
  }

  if (!tasks?.length) return <p className="text-sm text-muted-foreground">No se detectaron tareas.</p>

  return (
    <div className="space-y-2">
      {tasks.map((task, idx) => (
        <div key={idx} className="flex items-start gap-3 group">
          <Checkbox
            id={`task-${idx}`}
            checked={checked.has(idx)}
            onCheckedChange={() => toggle(idx)}
            className="mt-0.5"
          />
          <div className="flex-1 min-w-0">
            <label
              htmlFor={`task-${idx}`}
              className={`text-sm cursor-pointer ${checked.has(idx) ? 'line-through text-muted-foreground' : ''}`}
            >
              {task.task}
            </label>
            {task.deadline && (
              <p className="text-xs text-muted-foreground mt-0.5">Fecha límite: {task.deadline}</p>
            )}
            {task.responsible && (
              <p className="text-xs text-muted-foreground">Responsable: {task.responsible}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
