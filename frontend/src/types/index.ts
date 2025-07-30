export interface Provider {
  id: string
  name: string
  base_url: string
  description?: string
  free_quota_type?: 'CREDIT' | 'SHARED_TOKENS' | 'PER_MODEL_TOKENS'
}

export interface ApiKey {
  id: string
  provider_id: string
  alias: string
  key: string
  sort_order: number
  created_at: string
  provider?: Provider
}

export interface Model {
  id: string
  name: string
  description?: string
  capabilities: string[]
  family: string
  implementations?: ModelImplementation[]
}

export interface ModelImplementation {
  id: string
  provider_id: string
  model_id: string
  provider_model_id: string
  version?: string
  context_window?: number
  pricing_info?: {
    input_price?: number
    output_price?: number
  }
  is_available: boolean
  custom_parameters?: Record<string, any>
  sort_order: number
  provider?: Provider
  model?: Model
}

export interface Usage {
  api_key_id: string
  model_implementation_id: string
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  timestamp: string
  api_key?: ApiKey
  model_implementation?: ModelImplementation
}

export interface FreeQuota {
  id: string
  provider_id: string
  model_implementation_id?: string
  amount: number
  reset_period: 'NEVER' | 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY'
}

export interface UsageStats {
  total_tokens: number
  total_cost: number
  request_count?: number
  date: string
  provider?: string
  model?: string
}