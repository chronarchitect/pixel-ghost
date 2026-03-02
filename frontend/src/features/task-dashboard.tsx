import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
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
    <Card>
      <CardHeader>
        <CardTitle>Task Monitor</CardTitle>
        <CardDescription>Live queue + status tracking + result download links</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="track-id">Track task by ID</Label>
          <div className="flex flex-col gap-2 sm:flex-row">
            <Input id="track-id" placeholder="Paste task ID" value={selectedTaskId} onChange={(event) => setSelectedTaskId(event.target.value.trim())} />
            <Button variant="secondary" onClick={() => statusQuery.refetch()} disabled={!selectedTaskId}>
              Refresh status
            </Button>
            {selectedTaskId && (
              <Button variant="outline" asChild>
                <a href={pixelGhostApi.taskResultUrl(selectedTaskId)} target="_blank" rel="noreferrer">
                  Open result
                </a>
              </Button>
            )}
          </div>
          {statusQuery.data && (
            <div className="pt-2">
              <Badge variant={statusVariant(statusQuery.data.status)}>{statusQuery.data.status}</Badge>
            </div>
          )}
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold">Recent tasks</h3>
            <Button variant="ghost" size="sm" onClick={() => tasksQuery.refetch()}>
              Reload
            </Button>
          </div>

          {tasksQuery.isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : tasks.length === 0 ? (
            <p className="text-sm text-muted-foreground">No tasks yet.</p>
          ) : (
            <ul className="space-y-2">
              {tasks.map((task) => (
                <li key={task.id} className="flex flex-col gap-2 rounded-lg border p-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-mono text-xs sm:text-sm">{task.id}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={statusVariant(task.status)}>{task.status}</Badge>
                    <Button variant="outline" size="sm" asChild>
                      <a href={pixelGhostApi.taskResultUrl(task.id)} target="_blank" rel="noreferrer">
                        Result
                      </a>
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setSelectedTaskId(task.id)
                      }}
                    >
                      Track
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
