import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Terminal, Download, Crosshair, Loader2 } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { pixelGhostApi } from '@/lib/api/pixelGhost'

function statusVariant(status: string) {
  if (status === 'completed') return 'success' as const
  if (status === 'failed') return 'danger' as const
  if (status === 'processing') return 'warning' as const
  return 'secondary' as const
}

export function TaskDashboard() {
  const [selectedTaskId, setSelectedTaskId] = useState('')

  const tasksQuery = useQuery({
    queryKey: ['tasks'],
    queryFn: pixelGhostApi.listTasks,
    refetchInterval: 5000,
  })

  const statusQuery = useQuery({
    queryKey: ['task-status', selectedTaskId],
    queryFn: () => pixelGhostApi.getTaskStatus(selectedTaskId),
    enabled: selectedTaskId.length > 0,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'completed' || status === 'failed' ? false : 3000
    },
  })

  const tasks = useMemo(() => tasksQuery.data?.tasks ?? [], [tasksQuery.data])

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-[10px] font-black uppercase text-primary/60">
          <Crosshair className="size-3" />
          Task_Targeting_Systems
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="track-id" className="text-[10px] uppercase font-bold opacity-50">Manual Input_ID</Label>
          <div className="flex flex-col gap-2">
            <Input 
              id="track-id" 
              placeholder="PASTE_ID_HERE" 
              className="font-mono text-xs bg-black/40 border-primary/20 h-8"
              value={selectedTaskId} 
              onChange={(event) => setSelectedTaskId(event.target.value.trim())} 
            />
            <div className="flex gap-2">
              <Button 
                variant="secondary" 
                size="sm" 
                className="h-7 text-[10px] font-black uppercase flex-1"
                onClick={() => statusQuery.refetch()} 
                disabled={!selectedTaskId}
              >
                Query_Status
              </Button>
              {selectedTaskId && (
                <Button variant="outline" size="sm" className="h-7 text-[10px] font-black uppercase flex-1 border-primary/40" asChild>
                  <a href={pixelGhostApi.taskResultUrl(selectedTaskId)} target="_blank" rel="noreferrer">
                    <Download className="size-3 mr-1" />
                    Download
                  </a>
                </Button>
              )}
            </div>
          </div>
          {statusQuery.data && (
            <div className="pt-2 flex items-center justify-between border-t border-primary/10 mt-2">
              <span className="text-[10px] uppercase font-bold opacity-50">Current_Status:</span>
              <Badge variant={statusVariant(statusQuery.data.status)} className="text-[10px] font-black border-none uppercase">
                {statusQuery.data.status}
              </Badge>
            </div>
          )}
        </div>
      </div>

      <div className="space-y-4 pt-4 border-t border-primary/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-[10px] font-black uppercase text-primary/60">
            <Terminal className="size-3" />
            Live_Queue_Buffer
          </div>
          {tasksQuery.isFetching && <Loader2 className="size-3 animate-spin text-primary" />}
        </div>

        {tasksQuery.isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-8 w-full bg-primary/5" />
            <Skeleton className="h-8 w-full bg-primary/5" />
            <Skeleton className="h-8 w-full bg-primary/5" />
          </div>
        ) : tasks.length === 0 ? (
          <p className="text-[10px] uppercase font-bold opacity-30 text-center py-4 border border-dashed border-primary/10">No active processes detected.</p>
        ) : (
          <ul className="space-y-1 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
            {tasks.slice().reverse().map((task) => (
              <li key={task.id} className="group flex items-center justify-between gap-3 rounded-none border-l-2 border-primary/20 bg-primary/5 p-2 hover:bg-primary/10 transition-colors">
                <div className="min-w-0">
                  <p className="font-mono text-[10px] truncate opacity-80">{task.id}</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={statusVariant(task.status)} className="text-[8px] h-4 px-1 font-black border-none uppercase">
                    {task.status.substring(0, 4)}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-5 text-primary/40 hover:text-primary hover:bg-transparent"
                    onClick={() => {
                      setSelectedTaskId(task.id)
                    }}
                  >
                    <Crosshair className="size-3" />
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
