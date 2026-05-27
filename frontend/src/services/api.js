import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120_000,
})

export async function createUser(payload) {
  const { data } = await api.post('/api/users', payload)
  return data
}

export async function uploadDocument(file, userId) {
  const form = new FormData()
  form.append('file', file)
  form.append('user_id', userId)
  const { data } = await api.post('/api/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function confirmTransactions(payload) {
  const { data } = await api.post('/api/confirm', payload)
  return data
}

export function getReportDownloadUrl(reportId) {
  return `${BASE_URL}/api/report/${reportId}`
}

export async function healthCheck() {
  const { data } = await api.get('/api/health')
  return data
}
