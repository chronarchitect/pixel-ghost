import { apiClient } from '@/lib/api/client'
import type {
  SubmitTaskResponse,
  TaskListResponse,
  TaskStatusResponse,
} from '@/lib/api/types'

function buildFormData(fields: Record<string, string | Blob>) {
  const formData = new FormData()
  for (const [key, value] of Object.entries(fields)) {
    formData.append(key, value)
  }
  return formData
}

async function postTask(path: string, fields: Record<string, string | Blob>) {
  const { data } = await apiClient.post<SubmitTaskResponse>(path, buildFormData(fields), {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}

export const pixelGhostApi = {
  health: async () => {
    const { data } = await apiClient.get<{ message: string }>('/')
    return data
  },

  listTasks: async () => {
    const { data } = await apiClient.get<TaskListResponse>('/tasks')
    return data
  },

  getTaskStatus: async (taskId: string) => {
    const { data } = await apiClient.get<TaskStatusResponse>(`/task/status/${taskId}`)
    return data
  },

  taskResultUrl: (taskId: string) => `${apiClient.defaults.baseURL}/task/result/${taskId}`,

  textLsbEncode: (image: File, message: string) => postTask('/text/lsb/encode', { image, message }),
  textLsbDecode: (image: File) => postTask('/text/lsb/decode', { image }),
  textLsbRandomEncode: (image: File, message: string, key: string) => postTask('/text/lsb_random/encode', { image, message, key }),
  textLsbRandomDecode: (image: File, key: string) => postTask('/text/lsb_random/decode', { image, key }),
  textLsbRandomEncEncode: (image: File, message: string, key: string) =>
    postTask('/text/lsb_random_enc/encode', { image, message, key }),
  textLsbRandomEncDecode: (image: File, key: string) => postTask('/text/lsb_random_enc/decode', { image, key }),

  imageLsbEncode: (cover_image: File, secret_image: File) => postTask('/image/lsb/encode', { cover_image, secret_image }),
  imageLsbDecode: (stego_image: File) => postTask('/image/lsb/decode', { stego_image }),
  imageLsbRandomEncode: (cover_image: File, secret_image: File, key: string) =>
    postTask('/image/lsb_random/encode', { cover_image, secret_image, key }),
  imageLsbRandomDecode: (stego_image: File, key: string) => postTask('/image/lsb_random/decode', { stego_image, key }),
  imageLsbRandomEncEncode: (cover_image: File, secret_image: File, key: string) =>
    postTask('/image/lsb_random_enc/encode', { cover_image, secret_image, key }),
  imageLsbRandomEncDecode: (stego_image: File, key: string) => postTask('/image/lsb_random_enc/decode', { stego_image, key }),

  imageDctEncode: (cover_image: File, secret_image: File) => postTask('/image/dct/encode', { cover_image, secret_image }),
  imageDctDecode: (image: File) => postTask('/image/dct/decode', { image }),
}
