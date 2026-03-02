import type { components } from '@/lib/api/schema'

export type ApiTaskStatus = 'queued' | 'processing' | 'completed' | 'failed' | 'not_found'

export interface TaskSummary {
  id: string
  status: ApiTaskStatus | string
}

export interface SubmitTaskResponse {
  task_id: string
}

export interface TaskListResponse {
  tasks: TaskSummary[]
}

export interface TaskStatusResponse {
  task_id: string
  status: ApiTaskStatus | string
}

export type ValidationError = components['schemas']['HTTPValidationError']

export type TextLSBEncodeBody = components['schemas']['Body_encode_text_in_image_text_lsb_encode_post']
export type TextLSBDecodeBody = components['schemas']['Body_decode_text_from_image_text_lsb_decode_post']
export type TextLSBRandomEncodeBody = components['schemas']['Body_lsb_random_encode_text_in_image_text_lsb_random_encode_post']
export type TextLSBRandomDecodeBody = components['schemas']['Body_lsb_random_decode_text_from_image_text_lsb_random_decode_post']
export type TextLSBRandomEncEncodeBody = components['schemas']['Body_lsb_random_enc_encode_text_in_image_text_lsb_random_enc_encode_post']
export type TextLSBRandomEncDecodeBody = components['schemas']['Body_lsb_random_enc_decode_text_from_image_text_lsb_random_enc_decode_post']

export type ImageLSBEncodeBody = components['schemas']['Body_encode_image_in_image_image_lsb_encode_post']
export type ImageLSBDecodeBody = components['schemas']['Body_decode_image_from_image_image_lsb_decode_post']
export type ImageLSBRandomEncodeBody = components['schemas']['Body_encode_image_in_image_random_image_lsb_random_encode_post']
export type ImageLSBRandomDecodeBody = components['schemas']['Body_decode_image_from_image_random_image_lsb_random_decode_post']
export type ImageLSBRandomEncEncodeBody = components['schemas']['Body_encode_image_in_image_encrypted_image_lsb_random_enc_encode_post']
export type ImageLSBRandomEncDecodeBody = components['schemas']['Body_decode_image_from_image_encrypted_image_lsb_random_enc_decode_post']
export type ImageDctEncodeBody = components['schemas']['Body_dct_encode_image_image_dct_encode_post']
export type ImageDctDecodeBody = components['schemas']['Body_dct_decode_image_image_dct_decode_post']
