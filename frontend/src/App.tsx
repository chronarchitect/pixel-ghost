import { ShieldCheck, Activity, Terminal, AlertTriangle } from 'lucide-react'
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
    <main className="min-h-screen bg-background text-foreground selection:bg-primary selection:text-black">
      <div className="mx-auto w-full max-w-7xl px-0 py-0 sm:px-4 sm:py-8">
        {/* NERV STYLE HEADER */}
        <header className="card-header-gradient scanline flex flex-col gap-4 border-b-2 border-primary bg-black/80 p-6 sm:flex-row sm:items-center sm:justify-between text-primary backdrop-blur-md">
          <div className="flex items-center gap-4">
            <div className="flex flex-col items-center border-2 border-primary p-2 leading-none">
              <span className="text-[10px] font-black">MAGI</span>
              <span className="text-xl font-black">01</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-4xl font-black tracking-tighter uppercase italic">MAGI // PIXELGHOST</h1>
                <Activity className="size-5 animate-pulse text-success" />
              </div>
              <p className="text-[10px] tracking-[0.3em] uppercase opacity-60 font-bold">Terminal Access Level: 1-A // Security Override Enabled</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <div className="flex flex-col items-end gap-1">
              <div className="flex items-center gap-2">
                 <span className="text-[10px] font-bold uppercase opacity-50">Consensus:</span>
                 <span className="text-xs font-black text-success">66.6% PROBABILITY</span>
              </div>
              <Badge variant={healthQuery.isSuccess ? 'success' : 'danger'} className="px-4 py-0.5 text-[10px] border-none">
                <ShieldCheck className="mr-1.5 size-3" />
                {healthQuery.isSuccess ? 'LINK ESTABLISHED' : 'CODE BLUE // OFFLINE'}
              </Badge>
            </div>
            <div className="border-l border-primary/30 pl-4">
              <ThemeToggle />
            </div>
          </div>
        </header>

        {/* EMERGENCY ALERT BAR IF OFFLINE */}
        {!healthQuery.isSuccess && !healthQuery.isLoading && (
          <div className="emergency-alert h-10 flex items-center justify-center gap-4 text-black font-black text-sm animate-pulse">
            <AlertTriangle className="size-5" />
            CRITICAL SYSTEM ERROR // RE-ESTABLISH MAGI LINK IMMEDIATELY
            <AlertTriangle className="size-5" />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 p-4">
          {/* MAIN HUD CONTENT */}
          <div className="lg:col-span-8">
            <Card className="bg-black/40 border border-primary/20">
              <CardContent className="p-0">
                <Tabs defaultValue="text" className="w-full">
                  <TabsList className="w-full justify-start rounded-none h-auto bg-black/60 p-0 border-b border-primary/30">
                    <TabsTrigger value="text" className="data-[state=active]:bg-primary data-[state=active]:text-black rounded-none border-r border-primary/20">
                      <Terminal className="size-3 mr-2" />
                      TEXT_ENC
                    </TabsTrigger>
                    <TabsTrigger value="image" className="data-[state=active]:bg-primary data-[state=active]:text-black rounded-none border-r border-primary/20">
                      <Activity className="size-3 mr-2" />
                      IMAGE_ENC
                    </TabsTrigger>
                    <TabsTrigger value="audio" className="data-[state=active]:bg-primary data-[state=active]:text-black rounded-none border-r border-primary/20">
                      <Activity className="size-3 mr-2" />
                      AUDIO_ENC
                    </TabsTrigger>
                  </TabsList>

                  <div className="p-6">
                    <TabsContent value="text" className="mt-0">
                      <TextStegoPanel />
                    </TabsContent>

                    <TabsContent value="image" className="mt-0">
                      <ImageStegoPanel />
                    </TabsContent>

                    <TabsContent value="audio" className="mt-0">
                      <AudioStegoPanel />
                    </TabsContent>
                  </div>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          {/* SIDEBAR SYSTEM MONITOR */}
          <div className="lg:col-span-4 space-y-6">
            <Card className="bg-black/40 border border-primary/20">
              <CardContent className="p-0">
                <div className="bg-primary/10 p-2 border-b border-primary/20">
                  <h2 className="text-xs font-black tracking-widest uppercase flex items-center gap-2">
                    <Terminal className="size-3" />
                    Process_Monitor
                  </h2>
                </div>
                <div className="p-4">
                  <TaskDashboard />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  )
}

export default App
