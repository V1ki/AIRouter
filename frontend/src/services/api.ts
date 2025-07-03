import axios from 'axios'
import type {
  Provider,
  ApiKey,
  Model,
  ModelImplementation,
  Usage,
  UsageStats,
} from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const providerService = {
  getAll: async (): Promise<Provider[]> => {
    const { data } = await api.get('/providers')
    return data
  },
  
  create: async (provider: Omit<Provider, 'id'>): Promise<Provider> => {
    const { data } = await api.post('/providers', provider)
    return data
  },
  
  update: async (id: string, provider: Partial<Provider>): Promise<Provider> => {
    const { data } = await api.put(`/providers/${id}`, provider)
    return data
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`/providers/${id}`)
  },
}

export const apiKeyService = {
  getAll: async (): Promise<ApiKey[]> => {
    const { data } = await api.get('/api-keys')
    return data
  },
  
  create: async (apiKey: Omit<ApiKey, 'id'>): Promise<ApiKey> => {
    const { data } = await api.post('/api-keys', apiKey)
    return data
  },
  
  update: async (id: string, apiKey: Partial<ApiKey>): Promise<ApiKey> => {
    const { data } = await api.put(`/api-keys/${id}`, apiKey)
    return data
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`/api-keys/${id}`)
  },
}

export const modelService = {
  getAll: async (): Promise<Model[]> => {
    const { data } = await api.get('/models')
    return data
  },
  
  create: async (model: Omit<Model, 'id'>): Promise<Model> => {
    const { data } = await api.post('/models', model)
    return data
  },
  
  update: async (id: string, model: Partial<Model>): Promise<Model> => {
    const { data } = await api.put(`/models/${id}`, model)
    return data
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`/models/${id}`)
  },
}

export const modelImplementationService = {
  getAll: async (): Promise<ModelImplementation[]> => {
    const { data } = await api.get('/model-implementations')
    return data
  },
  
  create: async (impl: Omit<ModelImplementation, 'id'>): Promise<ModelImplementation> => {
    const { data } = await api.post('/model-implementations', impl)
    return data
  },
  
  update: async (id: string, impl: Partial<ModelImplementation>): Promise<ModelImplementation> => {
    const { data } = await api.put(`/model-implementations/${id}`, impl)
    return data
  },
  
  delete: async (id: string): Promise<void> => {
    await api.delete(`/model-implementations/${id}`)
  },
}

export const usageService = {
  getStats: async (params?: {
    start_date?: string
    end_date?: string
    group_by?: 'day' | 'provider' | 'model'
  }): Promise<UsageStats[]> => {
    const { data } = await api.get('/usage/stats', { params })
    return data
  },
  
  getDetails: async (params?: {
    start_date?: string
    end_date?: string
    api_key_id?: string
    model_implementation_id?: string
  }): Promise<Usage[]> => {
    const { data } = await api.get('/usage', { params })
    return data
  },
}