import { useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { pixelGhostApi } from '@/lib/api/pixelGhost'

const schema = z
  .object({
    variant: z.enum(['lsb', 'lsb_random', 'lsb_random_enc']),
    action: z.enum(['encode', 'decode']),
    image: z.instanceof(File, { message: 'Image is required' }),
    message: z.string().optional(),
    key: z.string().optional(),
  })
  .superRefine((value, ctx) => {
    if (value.action === 'encode' && !value.message?.trim()) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Message is required for encode', path: ['message'] })
    }
    if (value.variant !== 'lsb' && !value.key?.trim()) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Key is required for random variants', path: ['key'] })
    }
  })

type FormData = z.infer<typeof schema>

export function TextStegoPanel() {
  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      variant: 'lsb',
      action: 'encode',
      message: '',
      key: '',
    },
  })

  const variant = form.watch('variant')
  const action = form.watch('action')

  const submitMutation = useMutation({
    mutationFn: async (data: FormData) => {
      if (data.variant === 'lsb' && data.action === 'encode') return pixelGhostApi.textLsbEncode(data.image, data.message ?? '')
      if (data.variant === 'lsb' && data.action === 'decode') return pixelGhostApi.textLsbDecode(data.image)
      if (data.variant === 'lsb_random' && data.action === 'encode') return pixelGhostApi.textLsbRandomEncode(data.image, data.message ?? '', data.key ?? '')
      if (data.variant === 'lsb_random' && data.action === 'decode') return pixelGhostApi.textLsbRandomDecode(data.image, data.key ?? '')
      if (data.variant === 'lsb_random_enc' && data.action === 'encode') return pixelGhostApi.textLsbRandomEncEncode(data.image, data.message ?? '', data.key ?? '')
      return pixelGhostApi.textLsbRandomEncDecode(data.image, data.key ?? '')
    },
  })

  const submittedTaskId = submitMutation.data?.task_id

  const title = useMemo(() => {
    const mode = action === 'encode' ? 'Encode' : 'Decode'
    const algo = variant.replaceAll('_', ' ').toUpperCase()
    return `${mode} text with ${algo}`
  }, [variant, action])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Text Steganography</CardTitle>
        <CardDescription>{title}</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={form.handleSubmit((values) => submitMutation.mutate(values))}>
          <div className="grid gap-2 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="text-variant">Algorithm</Label>
              <select id="text-variant" className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm" {...form.register('variant')}>
                <option value="lsb">LSB</option>
                <option value="lsb_random">LSB Random</option>
                <option value="lsb_random_enc">LSB Random + Encryption</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="text-action">Action</Label>
              <select id="text-action" className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm" {...form.register('action')}>
                <option value="encode">Encode</option>
                <option value="decode">Decode</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="text-image">Image</Label>
            <Input
              id="text-image"
              type="file"
              accept="image/*"
              onChange={(event) => {
                const file = event.target.files?.[0]
                if (file) form.setValue('image', file, { shouldValidate: true })
              }}
            />
            {form.formState.errors.image && <p className="text-sm text-destructive">{form.formState.errors.image.message}</p>}
          </div>

          {action === 'encode' && (
            <div className="space-y-2">
              <Label htmlFor="text-message">Secret message</Label>
              <Textarea id="text-message" rows={4} placeholder="Type hidden message..." {...form.register('message')} />
              {form.formState.errors.message && <p className="text-sm text-destructive">{form.formState.errors.message.message}</p>}
            </div>
          )}

          {variant !== 'lsb' && (
            <div className="space-y-2">
              <Label htmlFor="text-key">Key</Label>
              <Input id="text-key" placeholder="Encryption/randomization key" {...form.register('key')} />
              {form.formState.errors.key && <p className="text-sm text-destructive">{form.formState.errors.key.message}</p>}
            </div>
          )}

          {submitMutation.isError && <p className="text-sm text-destructive">Failed to submit task. Check API availability and try again.</p>}

          {submittedTaskId && (
            <p className="text-sm text-muted-foreground">
              Task submitted: <span className="font-mono">{submittedTaskId}</span>
            </p>
          )}

          <Button type="submit" disabled={submitMutation.isPending}>
            {submitMutation.isPending ? 'Submitting...' : 'Submit task'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
