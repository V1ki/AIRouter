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

export interface ModelQuickAddRequest {
  name: string
  description?: string
  capabilities: string[]
  family: string
  provider_id: string
  provider_model_id: string
  version?: string
  context_window?: number
  pricing_info?: {
    input_price?: number
    output_price?: number
  }
  is_available: boolean
  sort_order: number
}

export interface ModelQuickAddResponse {
  model: Model
  implementation: ModelImplementation
  model_existed: boolean
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

  quickAdd: async (request: ModelQuickAddRequest): Promise<ModelQuickAddResponse> => {
    const { data } = await api.post('/models/quick-add', request)
    return data
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

export interface LiteLLMModelOption {
  litellm_key: string
  model_id: string
  input_price: number
  output_price: number
  max_tokens?: number
  max_input_tokens?: number
  litellm_provider?: string
}

export const pricingService = {
  searchLiteLLMModels: async (params: {
    search?: string
    provider_name?: string
    limit?: number
  }): Promise<{ count: number; models: LiteLLMModelOption[] }> => {
    const { data } = await api.get('/pricing/litellm/models', { params })
    return data
  },

  lookupLiteLLMPrice: async (
    providerModelId: string,
    providerName?: string
  ): Promise<{
    provider_model_id: string
    provider_name?: string
    pricing: {
      input_price: number
      output_price: number
      max_tokens?: number
      max_input_tokens?: number
      litellm_provider?: string
    }
  }> => {
    const { data } = await api.get(`/pricing/litellm/lookup/${encodeURIComponent(providerModelId)}`, {
      params: providerName ? { provider_name: providerName } : undefined,
    })
    return data
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