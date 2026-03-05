import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { z } from 'zod'
import { Activity, AlertCircle } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { pixelGhostApi } from '@/lib/api/pixelGhost'

const encodeSchema = z.object({
  audio_file: z.instanceof(File, { message: 'Source WAV buffer required' }),
  message: z.string().min(1, 'Payload buffer cannot be empty'),
})

const decodeSchema = z.object({
  audio_file: z.instanceof(File, { message: 'Stego WAV buffer required' }),
})

type EncodeValues = z.infer<typeof encodeSchema>
type DecodeValues = z.infer<typeof decodeSchema>

export function AudioStegoPanel() {
  const encodeForm = useForm<EncodeValues>({
    resolver: zodResolver(encodeSchema),
  })

  const decodeForm = useForm<DecodeValues>({
    resolver: zodResolver(decodeSchema),
  })

  const submitMutation = useMutation({
    mutationFn: async (values: EncodeValues | DecodeValues) => {
      if ('message' in values) {
        return pixelGhostApi.audioLsbEncode(values.audio_file, values.message)
      }
      return pixelGhostApi.audioLsbDecode(values.audio_file)
    },
    onSuccess: (data) => {
      alert(`[SYSTEM_SIGNAL] TASK_ACCEPTED: ${data.task_id}`)
    },
  })

  const onEncode = (values: EncodeValues) => submitMutation.mutate(values)
  const onDecode = (values: DecodeValues) => submitMutation.mutate(values)

  return (
    <div className="space-y-0">
      <div className="mb-6 flex items-center justify-between border-b border-primary/20 pb-2">
        <h2 className="text-xl font-black uppercase italic tracking-tighter text-primary flex items-center gap-2">
          <Activity className="size-4" />
          Audio_Buffer_Injection
        </h2>
        <span className="text-[10px] font-bold opacity-40">STG_PROTOCOL: v4.2.0</span>
      </div>

      <Tabs defaultValue="encode" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-8 h-10">
          <TabsTrigger value="encode" className="text-xs font-black uppercase">Initialize_Encode</TabsTrigger>
          <TabsTrigger value="decode" className="text-xs font-black uppercase">Initialize_Decode</TabsTrigger>
        </TabsList>

        <TabsContent value="encode" className="mt-0">
          <form onSubmit={encodeForm.handleSubmit(onEncode)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Source_Audio (WAV)</Label>
                  <Input
                    type="file"
                    accept=".wav"
                    className="text-[10px] font-mono bg-black/40 border-primary/20"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) encodeForm.setValue('audio_file', file, { shouldValidate: true })
                    }}
                  />
                  {encodeForm.formState.errors.audio_file && <p className="text-[10px] text-destructive uppercase font-bold mt-1">{encodeForm.formState.errors.audio_file.message}</p>}
                </div>
              </div>

              <div className="space-y-4">
                <div className="space-y-2 h-full flex flex-col">
                  <Label className="text-[10px] uppercase font-black opacity-60">Payload_Buffer</Label>
                  <Textarea 
                    placeholder="ENTER_TEXT_TO_HIDE..." 
                    className="flex-1 min-h-[120px] font-mono text-xs bg-black/40 border-primary/20 resize-none"
                    {...encodeForm.register('message')} 
                  />
                  {encodeForm.formState.errors.message && <p className="text-[10px] text-destructive uppercase font-bold mt-1">{encodeForm.formState.errors.message.message}</p>}
                </div>
              </div>
            </div>

            {submitMutation.isError && (
              <div className="bg-destructive/10 border-l-2 border-destructive p-3 flex items-start gap-3">
                <AlertCircle className="size-4 text-destructive shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-[10px] font-black text-destructive uppercase tracking-widest">Execution_Halt</p>
                  <p className="text-[9px] text-destructive/80 font-bold uppercase leading-tight">
                    {((submitMutation.error as any)?.response?.data?.error) || "SYSTEM_TASK_FAILURE: UNKNOWN_EXCEPTION"}
                  </p>
                </div>
              </div>
            )}

            <Button type="submit" className="w-full bg-primary hover:bg-primary/90 text-black font-black uppercase h-12 shadow-[0_0_15px_rgba(255,102,0,0.3)]" disabled={submitMutation.isPending}>
              {submitMutation.isPending ? 'PROCESSING_BUFFER...' : 'Execute_Injection_Task'}
            </Button>
          </form>
        </TabsContent>

        <TabsContent value="decode" className="mt-0">
          <form onSubmit={decodeForm.handleSubmit(onDecode)} className="max-w-md mx-auto space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-[10px] uppercase font-black opacity-60">Stego_Source (WAV)</Label>
                <div className="border border-dashed border-primary/30 p-8 bg-primary/5">
                  <Input
                    type="file"
                    accept=".wav"
                    className="text-[10px] font-mono"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) decodeForm.setValue('audio_file', file, { shouldValidate: true })
                    }}
                  />
                  {decodeForm.formState.errors.audio_file && <p className="text-[10px] text-destructive uppercase font-bold mt-2 text-center">{decodeForm.formState.errors.audio_file.message}</p>}
                </div>
              </div>
            </div>

            {submitMutation.isError && (
              <div className="bg-destructive/10 border-l-2 border-destructive p-3 flex items-start gap-3">
                <AlertCircle className="size-4 text-destructive shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-[10px] font-black text-destructive uppercase tracking-widest">Extraction_Halt</p>
                  <p className="text-[9px] text-destructive/80 font-bold uppercase leading-tight">
                    {((submitMutation.error as any)?.response?.data?.error) || "SYSTEM_TASK_FAILURE: UNKNOWN_EXCEPTION"}
                  </p>
                </div>
              </div>
            )}

            <Button type="submit" className="w-full bg-primary hover:bg-primary/90 text-black font-black uppercase h-12" disabled={submitMutation.isPending}>
              {submitMutation.isPending ? 'EXTRACTING_PAYLOAD...' : 'Run_Extraction'}
            </Button>
          </form>
        </TabsContent>
      </Tabs>
    </div>
  )
}
