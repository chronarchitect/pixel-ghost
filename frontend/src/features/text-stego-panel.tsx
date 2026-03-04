import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { z } from 'zod'
import { Zap } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { pixelGhostApi } from '@/lib/api/pixelGhost'

const encodeSchema = z.object({
  image: z.instanceof(File),
  message: z.string().min(1, 'Message is required'),
  method: z.enum(['lsb', 'lsb_random', 'lsb_random_enc']),
  key: z.string().optional(),
})

const decodeSchema = z.object({
  image: z.instanceof(File),
  method: z.enum(['lsb', 'lsb_random', 'lsb_random_enc']),
  key: z.string().optional(),
})

type EncodeValues = z.infer<typeof encodeSchema>
type DecodeValues = z.infer<typeof decodeSchema>

export function TextStegoPanel() {
  const encodeForm = useForm<EncodeValues>({
    resolver: zodResolver(encodeSchema),
    defaultValues: { method: 'lsb' },
  })

  const decodeForm = useForm<DecodeValues>({
    resolver: zodResolver(decodeSchema),
    defaultValues: { method: 'lsb' },
  })

  const submitMutation = useMutation({
    mutationFn: async (values: EncodeValues | DecodeValues) => {
      if ('message' in values) {
        if (values.method === 'lsb') return pixelGhostApi.textLsbEncode(values.image, values.message)
        if (values.method === 'lsb_random') return pixelGhostApi.textLsbRandomEncode(values.image, values.message, values.key || '')
        return pixelGhostApi.textLsbRandomEncEncode(values.image, values.message, values.key || '')
      } else {
        if (values.method === 'lsb') return pixelGhostApi.textLsbDecode(values.image)
        if (values.method === 'lsb_random') return pixelGhostApi.textLsbRandomDecode(values.image, values.key || '')
        return pixelGhostApi.textLsbRandomEncDecode(values.image, values.key || '')
      }
    },
    onSuccess: (data) => {
      alert(`[MAGI_SIGNAL] TASK_ACCEPTED: ${data.task_id}`)
    },
    onError: (error: any) => {
      alert(`[CRITICAL_FAILURE] ${error.response?.data?.error || error.message}`)
    },
  })

  const onEncode = (values: EncodeValues) => submitMutation.mutate(values)
  const onDecode = (values: DecodeValues) => submitMutation.mutate(values)

  const selectedEncodeMethod = encodeForm.watch('method')
  const selectedDecodeMethod = decodeForm.watch('method')

  return (
    <div className="space-y-0">
      <div className="mb-6 flex items-center justify-between border-b border-primary/20 pb-2">
        <h2 className="text-xl font-black uppercase italic tracking-tighter text-primary flex items-center gap-2">
          <Zap className="size-4" />
          Text_Data_Injection
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
                  <Label className="text-[10px] uppercase font-black opacity-60">Cover_Image_Source</Label>
                  <div className="border border-dashed border-primary/30 p-4 bg-primary/5 flex flex-col items-center justify-center gap-2">
                    <Input
                      type="file"
                      accept="image/*"
                      className="text-[10px] font-mono"
                      onChange={(e) => {
                        const file = e.target.files?.[0]
                        if (file) encodeForm.setValue('image', file)
                      }}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Injection_Logic</Label>
                  <select 
                    {...encodeForm.register('method')}
                    className="w-full bg-black border border-primary/20 p-2 text-xs font-black uppercase text-primary outline-none focus:border-primary"
                  >
                    <option value="lsb">Standard_LSB</option>
                    <option value="lsb_random">Randomized_Vector</option>
                    <option value="lsb_random_enc">Encrypted_Random_Vector</option>
                  </select>
                </div>

                {selectedEncodeMethod !== 'lsb' && (
                  <div className="space-y-2 animate-in slide-in-from-top-2 duration-200">
                    <Label className="text-[10px] uppercase font-black text-accent">Security_Key_Required</Label>
                    <Input 
                      placeholder="ENTER_KEY_PHRASE" 
                      className="bg-black/60 border-accent/40 text-accent font-mono text-xs h-9"
                      {...encodeForm.register('key')} 
                    />
                  </div>
                )}
              </div>

              <div className="space-y-4">
                <div className="space-y-2 h-full flex flex-col">
                  <Label className="text-[10px] uppercase font-black opacity-60">Payload_Buffer</Label>
                  <Textarea 
                    placeholder="ENTER_TEXT_TO_HIDE..." 
                    className="flex-1 min-h-[150px] font-mono text-xs bg-black/40 border-primary/20 resize-none"
                    {...encodeForm.register('message')} 
                  />
                </div>
              </div>
            </div>

            <Button type="submit" className="w-full bg-primary hover:bg-primary/90 text-black font-black uppercase h-12 shadow-[0_0_15px_rgba(255,102,0,0.3)]" disabled={submitMutation.isPending}>
              {submitMutation.isPending ? 'EXECUTING_INJECTION...' : 'Execute_Task'}
            </Button>
          </form>
        </TabsContent>

        <TabsContent value="decode" className="mt-0">
          <form onSubmit={decodeForm.handleSubmit(onDecode)} className="max-w-md mx-auto space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-[10px] uppercase font-black opacity-60">Encrypted_Source</Label>
                <div className="border border-dashed border-primary/30 p-8 bg-primary/5">
                  <Input
                    type="file"
                    accept="image/*"
                    className="text-[10px] font-mono"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) decodeForm.setValue('image', file)
                    }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Extraction_Logic</Label>
                  <select 
                    {...decodeForm.register('method')}
                    className="w-full bg-black border border-primary/20 p-2 text-xs font-black uppercase text-primary outline-none"
                  >
                    <option value="lsb">Standard_LSB</option>
                    <option value="lsb_random">Randomized_Vector</option>
                    <option value="lsb_random_enc">Encrypted_Random_Vector</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Access_Key</Label>
                  <Input 
                    placeholder="KEY" 
                    className="bg-black/60 border-primary/20 font-mono text-xs h-9"
                    disabled={selectedDecodeMethod === 'lsb'}
                    {...decodeForm.register('key')} 
                  />
                </div>
              </div>
            </div>

            <Button type="submit" className="w-full bg-primary hover:bg-primary/90 text-black font-black uppercase h-12" disabled={submitMutation.isPending}>
              {submitMutation.isPending ? 'EXTRACTING_PAYLOAD...' : 'Run_Extraction'}
            </Button>
          </form>
        </TabsContent>
      </Tabs>
    </div>
  )
}
