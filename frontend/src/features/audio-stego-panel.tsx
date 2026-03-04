import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { z } from 'zod'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { pixelGhostApi } from '@/lib/api/pixelGhost'

const encodeSchema = z.object({
  audio_file: z.instanceof(File),
  message: z.string().min(1, 'Message is required'),
})

const decodeSchema = z.object({
  audio_file: z.instanceof(File),
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
      alert(`Task submitted! ID: ${data.task_id}`)
    },
    onError: (error: any) => {
      alert(`Error: ${error.response?.data?.error || error.message}`)
    },
  })

  const onEncode = (values: EncodeValues) => submitMutation.mutate(values)
  const onDecode = (values: DecodeValues) => submitMutation.mutate(values)

  return (
    <Card className="border-none shadow-none bg-transparent">
      <CardHeader className="px-0">
        <CardTitle className="text-xl uppercase tracking-tight">Audio Steganography</CardTitle>
        <CardDescription>Hide text messages inside WAV audio files</CardDescription>
      </CardHeader>
      <CardContent className="px-0">
        <Tabs defaultValue="encode" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="encode">Encode</TabsTrigger>
            <TabsTrigger value="decode">Decode</TabsTrigger>
          </TabsList>

          <TabsContent value="encode">
            <form onSubmit={encodeForm.handleSubmit(onEncode)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="encode-audio">Cover Audio (WAV)</Label>
                <Input
                  id="encode-audio"
                  type="file"
                  accept=".wav"
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    if (file) encodeForm.setValue('audio_file', file)
                  }}
                />
                {encodeForm.formState.errors.audio_file && (
                  <p className="text-xs text-destructive">{encodeForm.formState.errors.audio_file.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="encode-message">Secret Message</Label>
                <Textarea id="encode-message" placeholder="Type your hidden message here..." {...encodeForm.register('message')} />
                {encodeForm.formState.errors.message && (
                  <p className="text-xs text-destructive">{encodeForm.formState.errors.message.message}</p>
                )}
              </div>

              <Button type="submit" className="w-full" disabled={submitMutation.isPending}>
                {submitMutation.isPending ? 'Processing...' : 'Embed Message'}
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="decode">
            <form onSubmit={decodeForm.handleSubmit(onDecode)} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="decode-audio">Stego Audio (WAV)</Label>
                <Input
                  id="decode-audio"
                  type="file"
                  accept=".wav"
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    if (file) decodeForm.setValue('audio_file', file)
                  }}
                />
                {decodeForm.formState.errors.audio_file && (
                  <p className="text-xs text-destructive">{decodeForm.formState.errors.audio_file.message}</p>
                )}
              </div>

              <Button type="submit" className="w-full" disabled={submitMutation.isPending}>
                {submitMutation.isPending ? 'Processing...' : 'Extract Message'}
              </Button>
            </form>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
