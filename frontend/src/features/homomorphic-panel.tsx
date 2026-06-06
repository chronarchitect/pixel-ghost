import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { z } from 'zod'
import { Shield } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { pixelGhostApi } from '@/lib/api/pixelGhost'

interface HomomorphicFormData {
  action: 'encrypt' | 'brightness' | 'decrypt';
  image?: File;
  bitlen: string;
  encryptedPng?: File;
  metadataJson?: File;
  n?: string;
  lam?: string;
  mu?: string;
  factor: string;
}

const schema = z.object({
  action: z.enum(['encrypt', 'brightness', 'decrypt']),
  image: z.instanceof(File).optional(),
  bitlen: z.string(),
  encryptedPng: z.instanceof(File).optional(),
  metadataJson: z.instanceof(File).optional(),
  n: z.string().optional(),
  lam: z.string().optional(),
  mu: z.string().optional(),
  factor: z.string(),
}).superRefine((data, ctx) => {
    if (data.action === 'encrypt') {
        if (!data.image) ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Image required', path: ['image'] })
    } else if (data.action === 'brightness') {
        if (!data.encryptedPng) ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Encrypted PNG required', path: ['encryptedPng'] })
        if (!data.metadataJson) ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Metadata JSON required', path: ['metadataJson'] })
        if (!data.n) ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Public Key N required', path: ['n'] })
    } else if (data.action === 'decrypt') {
        if (!data.encryptedPng) ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Encrypted PNG required', path: ['encryptedPng'] })
        if (!data.metadataJson) ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Metadata JSON required', path: ['metadataJson'] })
        if (!data.n) ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Public Key N required', path: ['n'] })
        if (!data.lam) ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Private Key Lambda required', path: ['lam'] })
        if (!data.mu) ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Private Key Mu required', path: ['mu'] })
    }
})

export function HomomorphicPanel() {
  const form = useForm<HomomorphicFormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      action: 'encrypt',
      bitlen: '128',
      factor: '50',
    },
  })

  const action = form.watch('action')

  const submitMutation = useMutation({
    mutationFn: async (data: HomomorphicFormData) => {
      if (data.action === 'encrypt') {
        return pixelGhostApi.homomorphicEncrypt(data.image!, parseInt(data.bitlen))
      } else if (data.action === 'brightness') {
        return pixelGhostApi.homomorphicBrightness(
          data.encryptedPng!,
          data.metadataJson!,
          data.n!,
          parseInt(data.factor)
        )
      } else {
        return pixelGhostApi.homomorphicDecrypt(
          data.encryptedPng!,
          data.metadataJson!,
          data.n!,
          data.lam!,
          data.mu!
        )
      }
    },
    onSuccess: (data) => {
      alert(`[SYSTEM_SIGNAL] TASK_ACCEPTED: ${data.task_id}`)
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.error || error.message
      alert(`[CRITICAL_FAILURE] ${errorMessage}`)
    },
  })

  return (
    <div className="space-y-0">
      <div className="mb-6 flex items-center justify-between border-b border-primary/20 pb-2">
        <h2 className="text-xl font-black uppercase italic tracking-tighter text-primary flex items-center gap-2">
          <Shield className="size-4" />
          Homomorphic_Transformation_Core
        </h2>
        <span className="text-[10px] font-bold opacity-40">PROTOCOL: PAILLIER_V2</span>
      </div>

      <Tabs 
        value={action} 
        onValueChange={(v) => form.setValue('action', v as any)} 
        className="w-full"
      >
        <TabsList className="grid w-full grid-cols-3 mb-8 h-10">
          <TabsTrigger value="encrypt" className="text-xs font-black uppercase">Encrypt</TabsTrigger>
          <TabsTrigger value="brightness" className="text-xs font-black uppercase">Brightness</TabsTrigger>
          <TabsTrigger value="decrypt" className="text-xs font-black uppercase">Decrypt</TabsTrigger>
        </TabsList>

        <form onSubmit={form.handleSubmit((values: HomomorphicFormData) => submitMutation.mutate(values))} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <TabsContent value="encrypt" className="mt-0 space-y-4">
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Source_Image</Label>
                  <Input
                    type="file"
                    accept="image/*"
                    className="text-[10px] font-mono bg-black/40 border-primary/20"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) form.setValue('image', file, { shouldValidate: true })
                    }}
                  />
                  {form.formState.errors.image && <p className="text-[10px] text-destructive uppercase font-bold">{form.formState.errors.image.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label className="text-[10px] uppercase font-black opacity-60">Key_Bit_Length</Label>
                  <Input 
                    type="number"
                    {...form.register('bitlen')}
                    className="bg-black/60 border-primary/20 font-mono text-xs h-9"
                  />
                </div>
              </TabsContent>

              {(action === 'brightness' || action === 'decrypt') && (
                <div className="space-y-4 animate-in fade-in duration-300">
                   <div className="space-y-2">
                    <Label className="text-[10px] uppercase font-black opacity-60">Encrypted_PNG</Label>
                    <Input
                      type="file"
                      accept="image/png"
                      className="text-[10px] font-mono bg-black/40 border-primary/20"
                      onChange={(e) => {
                        const file = e.target.files?.[0]
                        if (file) form.setValue('encryptedPng', file, { shouldValidate: true })
                      }}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-[10px] uppercase font-black opacity-60">Metadata_JSON</Label>
                    <Input
                      type="file"
                      accept="application/json"
                      className="text-[10px] font-mono bg-black/40 border-primary/20"
                      onChange={(e) => {
                        const file = e.target.files?.[0]
                        if (file) form.setValue('metadataJson', file, { shouldValidate: true })
                      }}
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-4">
              {(action === 'brightness' || action === 'decrypt') && (
                <div className="space-y-4 animate-in fade-in duration-300">
                  <div className="space-y-2">
                    <Label className="text-[10px] uppercase font-black opacity-60">Public_Key_N</Label>
                    <Input 
                      placeholder="N_VALUE" 
                      className="bg-black/60 border-primary/20 font-mono text-xs h-9"
                      {...form.register('n')} 
                    />
                  </div>
                </div>
              )}

              {action === 'brightness' && (
                 <div className="space-y-2 animate-in fade-in duration-300">
                    <Label className="text-[10px] uppercase font-black opacity-60">Brightness_Factor</Label>
                    <Input 
                      type="number"
                      {...form.register('factor')}
                      className="bg-black/60 border-primary/20 font-mono text-xs h-9"
                    />
                 </div>
              )}

              {action === 'decrypt' && (
                <div className="space-y-4 animate-in fade-in duration-300">
                   <div className="space-y-2">
                    <Label className="text-[10px] uppercase font-black text-accent">Private_Key_Lambda</Label>
                    <Input 
                      placeholder="LAM_VALUE" 
                      className="bg-black/60 border-accent/40 text-accent font-mono text-xs h-9"
                      {...form.register('lam')} 
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-[10px] uppercase font-black text-accent">Private_Key_Mu</Label>
                    <Input 
                      placeholder="MU_VALUE" 
                      className="bg-black/60 border-accent/40 text-accent font-mono text-xs h-9"
                      {...form.register('mu')} 
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          <Button 
            type="submit" 
            className="w-full bg-primary hover:bg-primary/90 text-black font-black uppercase h-12 shadow-[0_0_15px_rgba(255,102,0,0.3)]" 
            disabled={submitMutation.isPending}
          >
            {submitMutation.isPending ? 'EXECUTING_CRYPTOPROCESS...' : `Execute_${action}_Task`}
          </Button>
        </form>
      </Tabs>
    </div>
  )
}
