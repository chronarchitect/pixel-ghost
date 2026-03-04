import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { z } from 'zod'
import { ScanEye, Activity, Loader2, Maximize2, Download } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { pixelGhostApi } from '@/lib/api/pixelGhost'

const analysisSchema = z.object({
  image: z.instanceof(File),
  bit: z.string(),
})

type AnalysisValues = z.infer<typeof analysisSchema>

export function SignalAnalysisPanel() {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null)
  
  const form = useForm<AnalysisValues>({
    resolver: zodResolver(analysisSchema),
    defaultValues: { bit: '0' },
  })

  const submitMutation = useMutation({
    mutationFn: async (values: AnalysisValues) => {
      const bitNum = parseInt(values.bit, 10)
      return pixelGhostApi.analyzeBitPlane(values.image, bitNum)
    },
    onSuccess: (data) => {
      setActiveTaskId(data.task_id)
    },
    onError: (error: any) => {
      alert(`[ANALYSIS_FAILURE] ${error.response?.data?.error || error.message}`)
    },
  })

  // Poll for status of the active task
  const statusQuery = useQuery({
    queryKey: ['analysis-status', activeTaskId],
    queryFn: () => pixelGhostApi.getTaskStatus(activeTaskId!),
    enabled: !!activeTaskId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'completed' || status === 'failed' ? false : 1000
    },
  })

  const onAnalyze = (values: AnalysisValues) => {
    setActiveTaskId(null)
    submitMutation.mutate(values)
  }

  const isProcessing = !!submitMutation.isPending || !!(statusQuery.data?.status && !['completed', 'failed'].includes(statusQuery.data.status as string))
  const isCompleted = statusQuery.data?.status === 'completed'

  return (
    <div className="space-y-0">
      <div className="mb-6 flex items-center justify-between border-b border-primary/20 pb-2">
        <h2 className="text-xl font-black uppercase italic tracking-tighter text-primary flex items-center gap-2">
          <ScanEye className="size-4" />
          Signal_Noise_Analysis
        </h2>
        <span className="text-[10px] font-bold opacity-40">ANALYSIS_MODE: BIT_PLANE_ISOLATION</span>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Left: Controls */}
        <div className="space-y-6">
          <div className="bg-primary/5 border border-primary/20 p-6 space-y-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-[10px] font-black uppercase text-primary/60 mb-2">
                <Activity className="size-3" />
                Scanner_Configuration
              </div>
              <p className="text-[10px] uppercase font-bold opacity-50 leading-relaxed mb-4">
                Bit 0 (LSB) usually contains hidden noise patterns. <br/>
                High bits (7) reveal raw visual geometry.
              </p>
            </div>

            <form onSubmit={form.handleSubmit(onAnalyze)} className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Source_Buffer</Label>
                  <Input
                    type="file"
                    accept="image/*"
                    className="text-[10px] font-mono bg-black/40 border-primary/20"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) form.setValue('image', file)
                    }}
                  />
                </div>

                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Target_Plane</Label>
                  <div className="grid grid-cols-4 gap-2">
                    {['0', '1', '2', '3', '4', '5', '6', '7'].map((b) => (
                      <label key={b}>
                        <input
                          type="radio"
                          value={b}
                          className="peer sr-only"
                          {...form.register('bit')}
                        />
                        <div className="peer-checked:bg-primary peer-checked:text-black bg-black border border-primary/20 p-2 text-center text-xs font-black cursor-pointer hover:bg-primary/10 transition-colors">
                          {b}
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-primary hover:bg-primary/90 text-black font-black uppercase h-12 shadow-[0_0_15px_rgba(255,102,0,0.3)]" 
                disabled={isProcessing}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="size-4 mr-2 animate-spin" />
                    Scanning_Signal...
                  </>
                ) : 'Initiate_Signal_Scan'}
              </Button>
            </form>
          </div>
        </div>

        {/* Right: Live Preview */}
        <div className="space-y-4">
          <div className="flex items-center justify-between text-[10px] font-black uppercase text-primary/60 px-1">
            <div className="flex items-center gap-2">
              <Maximize2 className="size-3" />
              Visualization_Output
            </div>
            {isCompleted && (
              <a 
                href={pixelGhostApi.taskResultUrl(activeTaskId!)} 
                target="_blank" 
                rel="noreferrer"
                className="hover:text-primary transition-colors flex items-center gap-1"
              >
                <Download className="size-3" />
                Export_Frame
              </a>
            )}
          </div>

          <div className="aspect-square w-full bg-black border-2 border-primary/20 relative flex items-center justify-center overflow-hidden">
            {/* Scanline overlay for preview */}
            <div className="absolute inset-0 pointer-events-none z-10 opacity-20 bg-[linear-gradient(rgba(255,102,0,0.1)_50%,transparent_50%)] bg-[length:100%_4px]"></div>
            
            {!activeTaskId && !isProcessing && (
              <div className="text-center space-y-2 opacity-20">
                <ScanEye className="size-12 mx-auto mb-4" />
                <p className="text-[10px] font-black uppercase tracking-widest">No_Data_Detected</p>
                <p className="text-[8px] uppercase">Upload image to begin scan</p>
              </div>
            )}

            {isProcessing && (
              <div className="text-center space-y-4 z-20">
                <div className="size-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto shadow-[0_0_20px_rgba(255,102,0,0.4)]"></div>
                <div className="space-y-1">
                  <p className="text-xs font-black uppercase animate-pulse">Analyzing_Noise_Pattern...</p>
                  <p className="text-[8px] font-mono opacity-50">{activeTaskId}</p>
                </div>
              </div>
            )}

            {isCompleted && activeTaskId && (
              <img 
                src={pixelGhostApi.taskResultUrl(activeTaskId)} 
                alt="Bit plane visualization" 
                className="size-full object-contain image-pixelated"
                onLoad={() => {
                  // Optional: trigger some "Scan Complete" animation
                }}
              />
            )}

            {statusQuery.data?.status === 'failed' && (
              <div className="text-destructive text-center p-6 space-y-2">
                <p className="text-xs font-black uppercase">Scan_Interrupted</p>
                <p className="text-[8px] font-mono">ERROR: SYSTEM_TASK_FAILURE</p>
              </div>
            )}
          </div>
          
          {isCompleted && (
            <div className="bg-primary/10 border-l-2 border-primary p-3">
              <p className="text-[10px] font-bold uppercase mb-1">Interpretation_Guide:</p>
              <p className="text-[9px] opacity-70 leading-normal uppercase">
                If the image appears as random salt-and-pepper noise, the source is likely clean. 
                Distinct geometric patterns or high-contrast blocks in Bit 0 suggest artificial data injection.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
