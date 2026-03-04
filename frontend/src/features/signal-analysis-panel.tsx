import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { z } from 'zod'
import { ScanEye, Activity } from 'lucide-react'

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
      alert(`[SIGNAL_ANALYSIS] TASK_QUEUED: ${data.task_id}\n\nTrack this task in the monitor to download the visualization.`)
    },
    onError: (error: any) => {
      alert(`[ANALYSIS_FAILURE] ${error.response?.data?.error || error.message}`)
    },
  })

  const onAnalyze = (values: AnalysisValues) => submitMutation.mutate(values)

  return (
    <div className="space-y-0">
      <div className="mb-6 flex items-center justify-between border-b border-primary/20 pb-2">
        <h2 className="text-xl font-black uppercase italic tracking-tighter text-primary flex items-center gap-2">
          <ScanEye className="size-4" />
          Signal_Noise_Analysis
        </h2>
        <span className="text-[10px] font-bold opacity-40">ANALYSIS_MODE: BIT_PLANE_ISOLATION</span>
      </div>

      <div className="max-w-2xl mx-auto">
        <div className="bg-primary/5 border border-primary/20 p-6 space-y-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-[10px] font-black uppercase text-primary/60 mb-2">
              <Activity className="size-3" />
              Scanner_Configuration
            </div>
            <p className="text-xs opacity-70 leading-relaxed mb-4">
              Select a bit plane to isolate. Bit 0 (Least Significant Bit) is commonly used for hidden data. 
              Higher bits (7) contain more visual information of the original image.
            </p>
          </div>

          <form onSubmit={form.handleSubmit(onAnalyze)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Source_Image</Label>
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
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Target_Bit_Plane (0-7)</Label>
                  <div className="flex gap-2 flex-wrap">
                    {['0', '1', '2', '3', '4', '5', '6', '7'].map((b) => (
                      <label key={b} className="flex-1 min-w-[40px]">
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
            </div>

            <Button 
              type="submit" 
              className="w-full bg-primary hover:bg-primary/90 text-black font-black uppercase h-12 shadow-[0_0_15px_rgba(255,102,0,0.3)]" 
              disabled={submitMutation.isPending}
            >
              {submitMutation.isPending ? 'SCANNING_SIGNAL...' : 'Initiate_Signal_Scan'}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
