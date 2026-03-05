import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { z } from 'zod'
import { Activity, AlertCircle } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { pixelGhostApi } from '@/lib/api/pixelGhost'

const schema = z
  .object({
    variant: z.enum(['lsb', 'lsb_random', 'lsb_random_enc', 'dct']),
    action: z.enum(['encode', 'decode']),
    coverImage: z.instanceof(File).optional(),
    secretImage: z.instanceof(File).optional(),
    stegoImage: z.instanceof(File).optional(),
    key: z.string().optional(),
  })
  .superRefine((value, ctx) => {
    if (value.action === 'encode') {
      if (!value.coverImage) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Source image required', path: ['coverImage'] })
      }
      if (!value.secretImage) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Payload image required', path: ['secretImage'] })
      }
    }

    if (value.action === 'decode' && !value.stegoImage) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Target buffer required', path: ['stegoImage'] })
    }

    if ((value.variant === 'lsb_random' || value.variant === 'lsb_random_enc') && !value.key?.trim()) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Access key required', path: ['key'] })
    }
  })

type FormData = z.infer<typeof schema>

export function ImageStegoPanel() {
  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      variant: 'lsb',
      action: 'encode',
      key: '',
    },
  })

  const variant = form.watch('variant')
  const action = form.watch('action')

  const submitMutation = useMutation({
    mutationFn: async (data: FormData) => {
      if (data.action === 'encode') {
        const coverImage = data.coverImage as File
        const secretImage = data.secretImage as File

        if (data.variant === 'lsb') return pixelGhostApi.imageLsbEncode(coverImage, secretImage)
        if (data.variant === 'lsb_random') return pixelGhostApi.imageLsbRandomEncode(coverImage, secretImage, data.key ?? '')
        if (data.variant === 'lsb_random_enc') return pixelGhostApi.imageLsbRandomEncEncode(coverImage, secretImage, data.key ?? '')
        return pixelGhostApi.imageDctEncode(coverImage, secretImage)
      }

      const stegoImage = data.stegoImage as File
      if (data.variant === 'lsb') return pixelGhostApi.imageLsbDecode(stegoImage)
      if (data.variant === 'lsb_random') return pixelGhostApi.imageLsbRandomDecode(stegoImage, data.key ?? '')
      if (data.variant === 'lsb_random_enc') return pixelGhostApi.imageLsbRandomEncDecode(stegoImage, data.key ?? '')
      return pixelGhostApi.imageDctDecode(stegoImage)
    },
    onSuccess: (data) => {
      alert(`[SYSTEM_SIGNAL] TASK_ACCEPTED: ${data.task_id}`)
    },
    onError: (error: any) => {
      // Improved error handling for capacity issues
      const errorMessage = error.response?.data?.error || error.message
      alert(`[CRITICAL_FAILURE] ${errorMessage}`)
    },
  })

  return (
    <div className="space-y-0">
      <div className="mb-6 flex items-center justify-between border-b border-primary/20 pb-2">
        <h2 className="text-xl font-black uppercase italic tracking-tighter text-primary flex items-center gap-2">
          <Activity className="size-4" />
          Image_Buffer_Injection
        </h2>
        <span className="text-[10px] font-bold opacity-40">STG_PROTOCOL: v4.2.0</span>
      </div>

      <Tabs 
        value={action} 
        onValueChange={(v) => form.setValue('action', v as any)} 
        className="w-full"
      >
        <TabsList className="grid w-full grid-cols-2 mb-8 h-10">
          <TabsTrigger value="encode" className="text-xs font-black uppercase">Initialize_Encode</TabsTrigger>
          <TabsTrigger value="decode" className="text-xs font-black uppercase">Initialize_Decode</TabsTrigger>
        </TabsList>

        <form onSubmit={form.handleSubmit((values) => submitMutation.mutate(values))} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className="text-[10px] uppercase font-black opacity-60">Injection_Logic</Label>
                <select 
                  {...form.register('variant')}
                  className="w-full bg-black border border-primary/20 p-2 text-xs font-black uppercase text-primary outline-none focus:border-primary"
                >
                  <option value="lsb">Standard_LSB</option>
                  <option value="lsb_random">Randomized_Vector</option>
                  <option value="lsb_random_enc">Encrypted_Random_Vector</option>
                  <option value="dct">Frequency_Domain_DCT</option>
                </select>
              </div>

              {(variant === 'lsb_random' || variant === 'lsb_random_enc') && (
                <div className="space-y-2 animate-in slide-in-from-top-2 duration-200">
                  <Label className="text-[10px] uppercase font-black text-accent">Security_Key_Required</Label>
                  <Input 
                    placeholder="ENTER_ACCESS_KEY" 
                    className="bg-black/60 border-accent/40 text-accent font-mono text-xs h-9"
                    {...form.register('key')} 
                  />
                  {form.formState.errors.key && <p className="text-[10px] text-destructive uppercase font-bold">{form.formState.errors.key.message}</p>}
                </div>
              )}
            </div>

            <div className="space-y-4">
              <TabsContent value="encode" className="mt-0 space-y-4">
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Source_Buffer (Cover)</Label>
                  <Input
                    type="file"
                    accept="image/*"
                    className="text-[10px] font-mono bg-black/40 border-primary/20"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) form.setValue('coverImage', file, { shouldValidate: true })
                    }}
                  />
                  {form.formState.errors.coverImage && <p className="text-[10px] text-destructive uppercase font-bold">{form.formState.errors.coverImage.message}</p>}
                </div>

                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Payload_Buffer (Secret)</Label>
                  <Input
                    type="file"
                    accept="image/*"
                    className="text-[10px] font-mono bg-black/40 border-primary/20"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) form.setValue('secretImage', file, { shouldValidate: true })
                    }}
                  />
                  {form.formState.errors.secretImage && <p className="text-[10px] text-destructive uppercase font-bold">{form.formState.errors.secretImage.message}</p>}
                </div>
              </TabsContent>

              <TabsContent value="decode" className="mt-0 space-y-4">
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Target_Buffer (Stego)</Label>
                  <Input
                    type="file"
                    accept="image/*"
                    className="text-[10px] font-mono bg-black/40 border-primary/20"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) form.setValue('stegoImage', file, { shouldValidate: true })
                    }}
                  />
                  {form.formState.errors.stegoImage && <p className="text-[10px] text-destructive uppercase font-bold">{form.formState.errors.stegoImage.message}</p>}
                </div>
              </TabsContent>
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

          <Button 
            type="submit" 
            className="w-full bg-primary hover:bg-primary/90 text-black font-black uppercase h-12 shadow-[0_0_15px_rgba(255,102,0,0.3)]" 
            disabled={submitMutation.isPending}
          >
            {submitMutation.isPending ? 'PROCESSING_BUFFER...' : 'Execute_Injection_Task'}
          </Button>
        </form>
      </Tabs>
    </div>
  )
}
