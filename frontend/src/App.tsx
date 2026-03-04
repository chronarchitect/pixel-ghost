import { ShieldCheck, Activity, Terminal, AlertTriangle, Ghost, ScanEye } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

import { ThemeToggle } from '@/components/theme-toggle'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AudioStegoPanel } from '@/features/audio-stego-panel'
import { ImageStegoPanel } from '@/features/image-stego-panel'
import { SignalAnalysisPanel } from '@/features/signal-analysis-panel'
import { TaskDashboard } from '@/features/task-dashboard'
import { TextStegoPanel } from '@/features/text-stego-panel'
import { pixelGhostApi } from '@/lib/api/pixelGhost'

function PixelGhostIcon() {
  return (
    <div className="relative size-10 bg-primary flex items-center justify-center p-1 shadow-[0_0_15px_rgba(255,102,0,0.5)]">
      <div className="size-full bg-black flex items-center justify-center">
        <Ghost className="size-6 text-primary" strokeWidth={3} />
      </div>
      {/* Decorative pixel corners */}
      <div className="absolute -top-1 -left-1 size-2 bg-primary"></div>
      <div className="absolute -bottom-1 -right-1 size-2 bg-primary"></div>
    </div>
  )
}

function App() {
  const healthQuery = useQuery({
    queryKey: ['health'],
    queryFn: pixelGhostApi.health,
    refetchInterval: 10000,
  })

  return (
    <main className="min-h-screen bg-background text-foreground selection:bg-primary selection:text-black font-mono">
      <div className="mx-auto w-full max-w-7xl px-0 py-0 sm:px-4 sm:py-8">
        {/* PIXEL-GHOST INDUSTRIAL HEADER */}
        <header className="card-header-gradient scanline flex flex-col gap-4 border-b-2 border-primary bg-black/80 p-6 sm:flex-row sm:items-center sm:justify-between text-primary backdrop-blur-md">
          <div className="flex items-center gap-5">
            <PixelGhostIcon />
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-4xl font-black tracking-tighter uppercase italic">PIXEL-GHOST</h1>
                <Activity className="size-5 animate-pulse text-success" />
              </div>
              <p className="text-[10px] tracking-[0.3em] uppercase opacity-60 font-bold">Encrypted Data Injection Interface // SECURE_NODE_01</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <div className="flex flex-col items-end gap-1">
              <div className="flex items-center gap-2">
                 <span className="text-[10px] font-bold uppercase opacity-50">Signal_Strength:</span>
                 <span className="text-xs font-black text-success">STABLE // 99.9%</span>
              </div>
              <Badge variant={healthQuery.isSuccess ? 'success' : 'danger'} className="px-4 py-0.5 text-[10px] border-none">
                <ShieldCheck className="mr-1.5 size-3" />
                {healthQuery.isSuccess ? 'ENCRYPTION_LINK_ACTIVE' : 'INTERFACE_OFFLINE'}
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
            CONNECTION_FAILURE // SYSTEM_INTEGRITY_COMPROMISED
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
                    <TabsTrigger value="analysis" className="data-[state=active]:bg-primary data-[state=active]:text-black rounded-none border-r border-primary/20">
                      <ScanEye className="size-3 mr-2" />
                      SIGNAL_ANALYSIS
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

                    <TabsContent value="analysis" className="mt-0">
                      <SignalAnalysisPanel />
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
