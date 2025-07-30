import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Paper,
  TextField,
  Typography,
  MenuItem,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Chip,
  Card,
  CardContent,
  Grid,
  useTheme,
  alpha,
  Tooltip,
  LinearProgress,
  InputAdornment,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Key as KeyIcon,
  CloudQueue as CloudIcon,
  Link as LinkIcon,
  Description as DescriptionIcon,
  Search as SearchIcon,
} from '@mui/icons-material'
import { providerService, apiKeyService } from '../services/api'
import { PageHeader } from '../components/PageHeader'
import { EmptyState } from '../components/EmptyState'
import type { Provider, ApiKey } from '../types'

interface ProviderFormData {
  name: string
  base_url: string
  description: string
  free_quota_type?: 'CREDIT' | 'SHARED_TOKENS' | 'PER_MODEL_TOKENS'
}

interface ApiKeyFormData {
  alias: string
  key: string
  provider_id: string
  sort_order: number
}

export default function ProvidersPage() {
  const theme = useTheme()
  const queryClient = useQueryClient()
  const [providerOpen, setProviderOpen] = useState(false)
  const [apiKeyOpen, setApiKeyOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [editingProvider, setEditingProvider] = useState<Provider | null>(null)
  const [editingApiKey, setEditingApiKey] = useState<ApiKey | null>(null)
  const [providerFormData, setProviderFormData] = useState<ProviderFormData>({
    name: '',
    base_url: '',
    description: '',
  })
  const [apiKeyFormData, setApiKeyFormData] = useState<ApiKeyFormData>({
    alias: '',
    key: '',
    provider_id: '',
    sort_order: 0,
  })
  const [error, setError] = useState<string | null>(null)
  const [expandedProvider, setExpandedProvider] = useState<string | null>(null)

  const { data: providers = [], isLoading } = useQuery({
    queryKey: ['providers'],
    queryFn: providerService.getAll,
  })

  const { data: apiKeys = [] } = useQuery({
    queryKey: ['api-keys'],
    queryFn: apiKeyService.getAll,
  })

  const createProviderMutation = useMutation({
    mutationFn: providerService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      handleProviderClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to create provider')
    },
  })

  const updateProviderMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Provider> }) =>
      providerService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      handleProviderClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to update provider')
    },
  })

  const deleteProviderMutation = useMutation({
    mutationFn: providerService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
    },
  })

  const createApiKeyMutation = useMutation({
    mutationFn: apiKeyService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      handleApiKeyClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to create API key')
    },
  })

  const updateApiKeyMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ApiKey> }) =>
      apiKeyService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
      handleApiKeyClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to update API key')
    },
  })

  const deleteApiKeyMutation = useMutation({
    mutationFn: apiKeyService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
    },
  })

  const handleProviderOpen = (provider?: Provider) => {
    if (provider) {
      setEditingProvider(provider)
      setProviderFormData({
        name: provider.name,
        base_url: provider.base_url,
        description: provider.description || '',
        free_quota_type: provider.free_quota_type,
      })
    } else {
      setEditingProvider(null)
      setProviderFormData({
        name: '',
        base_url: '',
        description: '',
      })
    }
    setError(null)
    setProviderOpen(true)
  }

  const handleProviderClose = () => {
    setProviderOpen(false)
    setEditingProvider(null)
    setError(null)
  }

  const handleProviderSubmit = () => {
    if (editingProvider) {
      updateProviderMutation.mutate({
        id: editingProvider.id,
        data: providerFormData,
      })
    } else {
      createProviderMutation.mutate(providerFormData)
    }
  }

  const handleProviderDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this provider? All associated API keys will also be deleted.')) {
      deleteProviderMutation.mutate(id)
    }
  }

  const handleApiKeyOpen = (providerId: string, apiKey?: ApiKey) => {
    if (apiKey) {
      setEditingApiKey(apiKey)
      setApiKeyFormData({
        alias: apiKey.alias,
        key: apiKey.key,
        provider_id: apiKey.provider_id,
        sort_order: apiKey.sort_order || 0,
      })
    } else {
      setEditingApiKey(null)
      setApiKeyFormData({
        alias: '',
        key: '',
        provider_id: providerId,
        sort_order: 0,
      })
    }
    setError(null)
    setApiKeyOpen(true)
  }

  const handleApiKeyClose = () => {
    setApiKeyOpen(false)
    setEditingApiKey(null)
    setError(null)
  }

  const handleApiKeySubmit = () => {
    if (editingApiKey) {
      updateApiKeyMutation.mutate({
        id: editingApiKey.id,
        data: apiKeyFormData,
      })
    } else {
      createApiKeyMutation.mutate(apiKeyFormData)
    }
  }

  const handleApiKeyDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this API key?')) {
      deleteApiKeyMutation.mutate(id)
    }
  }

  const getProviderApiKeys = (providerId: string) => {
    return apiKeys.filter(key => key.provider_id === providerId)
  }

  const handleAccordionChange = (providerId: string) => (_: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedProvider(isExpanded ? providerId : null)
  }

  const filteredProviders = providers.filter(provider =>
    provider.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    provider.base_url.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (!isLoading && providers.length === 0) {
    return (
      <Box>
        <PageHeader
          title="Providers"
          subtitle="Connect and manage AI providers"
          breadcrumbs={[
            { label: 'Home', path: '/' },
            { label: 'Providers' },
          ]}
        />
        <EmptyState
          icon={<CloudIcon />}
          title="No providers configured"
          description="Add your first AI provider to get started"
          action={{
            label: "Add Provider",
            onClick: () => handleProviderOpen(),
            startIcon: <AddIcon />
          }}
        />
      </Box>
    )
  }

  return (
    <Box>
      <PageHeader
        title="Providers"
        subtitle="Connect and manage AI providers and their API keys"
        breadcrumbs={[
          { label: 'Home', path: '/' },
          { label: 'Providers' },
        ]}
        action={
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleProviderOpen()}
          >
            Add Provider
          </Button>
        }
      />

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Total Providers
                  </Typography>
                  <Typography variant="h4" fontWeight={600}>
                    {providers.length}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    width: 56,
                    height: 56,
                    borderRadius: 2,
                    backgroundColor: alpha(theme.palette.primary.main, 0.1),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <CloudIcon color="primary" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Total API Keys
                  </Typography>
                  <Typography variant="h4" fontWeight={600}>
                    {apiKeys.length}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    width: 56,
                    height: 56,
                    borderRadius: 2,
                    backgroundColor: alpha(theme.palette.success.main, 0.1),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <KeyIcon color="success" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Active Providers
                  </Typography>
                  <Typography variant="h4" fontWeight={600}>
                    {providers.filter(p => getProviderApiKeys(p.id).length > 0).length}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    width: 56,
                    height: 56,
                    borderRadius: 2,
                    backgroundColor: alpha(theme.palette.info.main, 0.1),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <LinkIcon color="info" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Provider List */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Search providers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{ mb: 3 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          
          {filteredProviders.map((provider) => {
            const providerApiKeys = getProviderApiKeys(provider.id)
            return (
              <Accordion
                key={provider.id}
                expanded={expandedProvider === provider.id}
                onChange={handleAccordionChange(provider.id)}
                sx={{ 
                  mb: 2,
                  '&:before': { display: 'none' },
                  boxShadow: 'none',
                  border: `1px solid ${theme.palette.divider}`,
                  '&.Mui-expanded': {
                    margin: '0 0 16px 0',
                  },
                }}
              >
                <AccordionSummary 
                  expandIcon={<ExpandMoreIcon />}
                  sx={{
                    backgroundColor: expandedProvider === provider.id 
                      ? alpha(theme.palette.primary.main, 0.04)
                      : 'transparent',
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.04),
                    },
                  }}
                >
                  <Box display="flex" alignItems="center" width="100%" pr={2}>
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 2,
                        backgroundColor: alpha(theme.palette.primary.main, 0.1),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mr: 2,
                      }}
                    >
                      <CloudIcon color="primary" />
                    </Box>
                    <Box flex={1}>
                      <Typography variant="h6" fontWeight={600}>
                        {provider.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {provider.base_url}
                      </Typography>
                    </Box>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Chip
                        icon={<KeyIcon />}
                        label={`${providerApiKeys.length} Key${providerApiKeys.length !== 1 ? 's' : ''}`}
                        size="small"
                        sx={{
                          backgroundColor: providerApiKeys.length > 0 
                            ? alpha(theme.palette.success.main, 0.1)
                            : alpha(theme.palette.grey[500], 0.1),
                          color: providerApiKeys.length > 0 
                            ? theme.palette.success.dark
                            : theme.palette.text.secondary,
                        }}
                      />
                      {provider.free_quota_type && (
                        <Chip
                          label={provider.free_quota_type.replace('_', ' ')}
                          size="small"
                          sx={{
                            backgroundColor: alpha(theme.palette.secondary.main, 0.1),
                            color: theme.palette.secondary.dark,
                          }}
                        />
                      )}
                      <Tooltip title="Edit Provider">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleProviderOpen(provider)
                          }}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Provider">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleProviderDelete(provider.id)
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {provider.description && (
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {provider.description}
                    </Typography>
                  )}
                  
                  <Box>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="subtitle1" fontWeight="bold">API Keys</Typography>
                      <Button
                        size="small"
                        startIcon={<AddIcon />}
                        onClick={() => handleApiKeyOpen(provider.id)}
                      >
                        Add API Key
                      </Button>
                    </Box>
                    
                    {providerApiKeys.length === 0 ? (
                      <Box
                        sx={{
                          p: 3,
                          textAlign: 'center',
                          backgroundColor: alpha(theme.palette.grey[500], 0.04),
                          borderRadius: 2,
                          border: `1px dashed ${theme.palette.divider}`,
                        }}
                      >
                        <KeyIcon sx={{ fontSize: 40, color: theme.palette.text.disabled, mb: 1 }} />
                        <Typography variant="body2" color="text.secondary">
                          No API keys configured for this provider
                        </Typography>
                      </Box>
                    ) : (
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Name</TableCell>
                            <TableCell>Key</TableCell>
                            <TableCell>Sort Order</TableCell>
                            <TableCell align="right">Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {providerApiKeys.map((apiKey) => (
                            <TableRow key={apiKey.id}>
                              <TableCell>{apiKey.alias}</TableCell>
                              <TableCell>
                                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                  {apiKey.key.substring(0, 20)}...
                                </Typography>
                              </TableCell>
                              <TableCell>{apiKey.sort_order || 0}</TableCell>
                              <TableCell align="right">
                                <IconButton
                                  size="small"
                                  onClick={() => handleApiKeyOpen(provider.id, apiKey)}
                                >
                                  <EditIcon />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  onClick={() => handleApiKeyDelete(apiKey.id)}
                                >
                                  <DeleteIcon />
                                </IconButton>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            )
          })}
        </CardContent>
      </Card>

      {/* Provider Dialog */}
      <Dialog open={providerOpen} onClose={handleProviderClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingProvider ? 'Edit Provider' : 'Add Provider'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={providerFormData.name}
            onChange={(e) => setProviderFormData({ ...providerFormData, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Base URL"
            fullWidth
            value={providerFormData.base_url}
            onChange={(e) => setProviderFormData({ ...providerFormData, base_url: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={2}
            value={providerFormData.description}
            onChange={(e) => setProviderFormData({ ...providerFormData, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            select
            margin="dense"
            label="Free Quota Type"
            fullWidth
            value={providerFormData.free_quota_type || ''}
            onChange={(e) => setProviderFormData({ ...providerFormData, free_quota_type: e.target.value as any })}
          >
            <MenuItem value="">None</MenuItem>
            <MenuItem value="CREDIT">Credit</MenuItem>
            <MenuItem value="SHARED_TOKENS">Shared Tokens</MenuItem>
            <MenuItem value="PER_MODEL_TOKENS">Per Model Tokens</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleProviderClose}>Cancel</Button>
          <Button onClick={handleProviderSubmit} variant="contained">
            {editingProvider ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* API Key Dialog */}
      <Dialog open={apiKeyOpen} onClose={handleApiKeyClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingApiKey ? 'Edit API Key' : 'Add API Key'}
        </DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            autoFocus
            margin="dense"
            label="Alias"
            fullWidth
            value={apiKeyFormData.alias}
            onChange={(e) => setApiKeyFormData({ ...apiKeyFormData, alias: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="API Key"
            fullWidth
            type="password"
            value={apiKeyFormData.key}
            onChange={(e) => setApiKeyFormData({ ...apiKeyFormData, key: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Sort Order"
            fullWidth
            type="number"
            value={apiKeyFormData.sort_order}
            onChange={(e) => setApiKeyFormData({ ...apiKeyFormData, sort_order: parseInt(e.target.value) || 0 })}
            helperText="Lower values have higher priority"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleApiKeyClose}>Cancel</Button>
          <Button onClick={handleApiKeySubmit} variant="contained">
            {editingApiKey ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}