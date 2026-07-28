import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

export const uploadFile = (file, docType) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('doc_type', docType)
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const analyzeContent = (data) => {
  return api.post('/analyze', data)
}

export const exportTestCases = (data) => {
  return api.post('/export', data, {
    responseType: 'blob'
  })
}

export const getTemplates = () => {
  return api.get('/templates')
}

export default api