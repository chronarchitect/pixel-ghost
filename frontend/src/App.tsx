import { ShieldCheck } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

import { ThemeToggle } from '@/components/theme-toggle'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
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
        <header className="card-header-gradient flex flex-col gap-4 rounded-xl border-none p-6 sm:flex-row sm:items-center sm:justify-between text-white">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">PixelGhost</h1>
            <p className="text-sm opacity-90">Secure Steganography Control Center</p>
          </div>

          <div className="flex items-center gap-3">
            <Badge variant={healthQuery.isSuccess ? 'success' : 'danger'} className="shadow-lg border-none">
              <ShieldCheck className="mr-1.5 size-4" />
              {healthQuery.isSuccess ? 'API Online' : 'API Offline'}
            </Badge>
            <div className="rounded-full bg-white/20 p-0.5 backdrop-blur-sm">
              <ThemeToggle />
            </div>
          </div>
        </header>

        <Card>
          <CardContent className="pt-6">
            <Tabs defaultValue="text" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="text">Text</TabsTrigger>
                <TabsTrigger value="image">Image</TabsTrigger>
                <TabsTrigger value="tasks">Tasks</TabsTrigger>
              </TabsList>

              <TabsContent value="text">
                <TextStegoPanel />
              </TabsContent>

              <TabsContent value="image">
                <ImageStegoPanel />
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
