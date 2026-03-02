import { useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Cover image is required', path: ['coverImage'] })
      }
      if (!value.secretImage) {
        ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Secret image is required', path: ['secretImage'] })
      }
    }

    if (value.action === 'decode' && !value.stegoImage) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Stego image is required', path: ['stegoImage'] })
    }

    if ((value.variant === 'lsb_random' || value.variant === 'lsb_random_enc') && !value.key?.trim()) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Key is required for random variants', path: ['key'] })
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
  })

  const title = useMemo(() => {
    const mode = action === 'encode' ? 'Encode image-in-image' : 'Decode hidden image'
    return `${mode} • ${variant.toUpperCase().replaceAll('_', ' ')}`
  }, [variant, action])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Image Steganography</CardTitle>
        <CardDescription>{title}</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-4" onSubmit={form.handleSubmit((values) => submitMutation.mutate(values))}>
          <div className="grid gap-2 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="image-variant">Algorithm</Label>
              <select id="image-variant" className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm" {...form.register('variant')}>
                <option value="lsb">LSB</option>
                <option value="lsb_random">LSB Random</option>
                <option value="lsb_random_enc">LSB Random + Encryption</option>
                <option value="dct">DCT</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="image-action">Action</Label>
              <select id="image-action" className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm" {...form.register('action')}>
                <option value="encode">Encode</option>
                <option value="decode">Decode</option>
              </select>
            </div>
          </div>

          {action === 'encode' ? (
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="cover-image">Cover image</Label>
                <Input
                  id="cover-image"
                  type="file"
                  accept="image/*"
                  onChange={(event) => {
                    const file = event.target.files?.[0]
                    if (file) form.setValue('coverImage', file, { shouldValidate: true })
                  }}
                />
                {form.formState.errors.coverImage && <p className="text-sm text-destructive">{form.formState.errors.coverImage.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="secret-image">Secret image</Label>
                <Input
                  id="secret-image"
                  type="file"
                  accept="image/*"
                  onChange={(event) => {
                    const file = event.target.files?.[0]
                    if (file) form.setValue('secretImage', file, { shouldValidate: true })
                  }}
                />
                {form.formState.errors.secretImage && <p className="text-sm text-destructive">{form.formState.errors.secretImage.message}</p>}
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <Label htmlFor="stego-image">Stego image</Label>
              <Input
                id="stego-image"
                type="file"
                accept="image/*"
                onChange={(event) => {
                  const file = event.target.files?.[0]
                  if (file) form.setValue('stegoImage', file, { shouldValidate: true })
                }}
              />
              {form.formState.errors.stegoImage && <p className="text-sm text-destructive">{form.formState.errors.stegoImage.message}</p>}
            </div>
          )}

          {(variant === 'lsb_random' || variant === 'lsb_random_enc') && (
            <div className="space-y-2">
              <Label htmlFor="image-key">Key</Label>
              <Input id="image-key" placeholder="Encryption/randomization key" {...form.register('key')} />
              {form.formState.errors.key && <p className="text-sm text-destructive">{form.formState.errors.key.message}</p>}
            </div>
          )}

          {submitMutation.isError && <p className="text-sm text-destructive">Failed to submit task. Check API availability and try again.</p>}

          {submitMutation.data?.task_id && (
            <p className="text-sm text-muted-foreground">
              Task submitted: <span className="font-mono">{submitMutation.data.task_id}</span>
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
