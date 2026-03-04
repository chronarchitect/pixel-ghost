import { ShieldCheck } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

import { ThemeToggle } from '@/components/theme-toggle'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AudioStegoPanel } from '@/features/audio-stego-panel'
import { ImageStegoPanel } from '@/features/image-stego-panel'
import { TaskDashboard } from '@/features/task-dashboard'
import { TextStegoPanel } from '@/features/text-stego-panel'
import { pixelGhostApi } from '@/lib/api/pixelGhost'

function App() {
  const healthQuery = useQuery({
    queryKey: ['health'],
    queryFn: pixelGhostApi.health,
    refetchInterval: 10000,
  })

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto w-full max-w-6xl space-y-6 px-4 py-8 md:px-6">
        <header className="card-header-gradient scanline flex flex-col gap-4 rounded-xl border-none p-6 sm:flex-row sm:items-center sm:justify-between text-white shadow-[0_0_20px_rgba(168,255,0,0.1)]">
          <div>
            <div className="flex items-center gap-2">
              <div className="size-3 bg-success animate-pulse rounded-full shadow-[0_0_10px_#a8ff00]"></div>
              <h1 className="text-3xl font-black tracking-tighter uppercase italic">PixelGhost // Eva-01</h1>
            </div>
            <p className="text-xs tracking-widest uppercase opacity-80 mt-1">Nerv / Steganography Control System</p>
          </div>

          <div className="flex items-center gap-4">
            <Badge variant={healthQuery.isSuccess ? 'success' : 'danger'} className="shadow-lg border border-white/20 px-4 py-1">
              <ShieldCheck className="mr-1.5 size-4" />
              {healthQuery.isSuccess ? 'SYSTEM ONLINE' : 'SYSTEM OFFLINE'}
            </Badge>
            <div className="rounded-full bg-black/40 p-1 backdrop-blur-md border border-white/10">
              <ThemeToggle />
            </div>
          </div>
        </header>

        <Card>
          <CardContent className="pt-6">
            <Tabs defaultValue="text" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="text">Text</TabsTrigger>
                <TabsTrigger value="image">Image</TabsTrigger>
                <TabsTrigger value="audio">Audio</TabsTrigger>
                <TabsTrigger value="tasks">Tasks</TabsTrigger>
              </TabsList>

              <TabsContent value="text">
                <TextStegoPanel />
              </TabsContent>

              <TabsContent value="image">
                <ImageStegoPanel />
              </TabsContent>

              <TabsContent value="audio">
                <AudioStegoPanel />
              </TabsContent>

              <TabsContent value="tasks">
                <TaskDashboard />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}

export default App
