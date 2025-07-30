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
  Chip,
  Alert,
  MenuItem,
  FormControlLabel,
  Switch,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Card,
  CardContent,
  Grid,
  useTheme,
  alpha,
  Tooltip,
  InputAdornment,
  Collapse,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Settings as SettingsIcon,
  ModelTraining as ModelIcon,
  Search as SearchIcon,
  AttachMoney as MoneyIcon,
  Memory as MemoryIcon,
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material'
import { modelService, modelImplementationService, providerService } from '../services/api'
import { PageHeader } from '../components/PageHeader'
import { EmptyState } from '../components/EmptyState'
import { ModelCard } from '../components/ModelCard'
import type { Model, ModelImplementation } from '../types'

interface ModelFormData {
  name: string
  description: string
  capabilities: string[]
  family: string
}

interface ImplementationFormData {
  provider_id: string
  model_id: string
  provider_model_id: string
  version: string
  context_window: number
  pricing_info: {
    input_price?: number
    output_price?: number
  }
  is_available: boolean
  sort_order: number
}

export default function ModelsPage() {
  const theme = useTheme()
  const queryClient = useQueryClient()
  const [modelOpen, setModelOpen] = useState(false)
  const [implOpen, setImplOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [editingModel, setEditingModel] = useState<Model | null>(null)
  const [editingImpl, setEditingImpl] = useState<ModelImplementation | null>(null)
  const [modelFormData, setModelFormData] = useState<ModelFormData>({
    name: '',
    description: '',
    capabilities: [],
    family: '',
  })
  const [implFormData, setImplFormData] = useState<ImplementationFormData>({
    provider_id: '',
    model_id: '',
    provider_model_id: '',
    version: '',
    context_window: 4096,
    pricing_info: {},
    is_available: true,
    sort_order: 0,
  })
  const [error, setError] = useState<string | null>(null)
  const [capabilityInput, setCapabilityInput] = useState('')
  const [expandedModel, setExpandedModel] = useState<string | null>(null)

  const { data: models = [], isLoading: modelsLoading } = useQuery({
    queryKey: ['models'],
    queryFn: modelService.getAll,
  })

  const { data: implementations = [] } = useQuery({
    queryKey: ['implementations'],
    queryFn: modelImplementationService.getAll,
  })

  const { data: providers = [] } = useQuery({
    queryKey: ['providers'],
    queryFn: providerService.getAll,
  })

  const createModelMutation = useMutation({
    mutationFn: modelService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
      handleModelClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to create model')
    },
  })

  const updateModelMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Model> }) =>
      modelService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
      handleModelClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to update model')
    },
  })

  const deleteModelMutation = useMutation({
    mutationFn: modelService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
    },
  })

  const createImplMutation = useMutation({
    mutationFn: modelImplementationService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['implementations'] })
      handleImplClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to create implementation')
    },
  })

  const updateImplMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ModelImplementation> }) =>
      modelImplementationService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['implementations'] })
      handleImplClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to update implementation')
    },
  })

  const deleteImplMutation = useMutation({
    mutationFn: modelImplementationService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['implementations'] })
    },
  })

  const handleModelOpen = (model?: Model) => {
    if (model) {
      setEditingModel(model)
      setModelFormData({
        name: model.name,
        description: model.description || '',
        capabilities: model.capabilities,
        family: model.family,
      })
    } else {
      setEditingModel(null)
      setModelFormData({
        name: '',
        description: '',
        capabilities: [],
        family: '',
      })
    }
    setError(null)
    setModelOpen(true)
  }

  const handleModelClose = () => {
    setModelOpen(false)
    setEditingModel(null)
    setError(null)
  }

  const handleModelSubmit = () => {
    if (editingModel) {
      updateModelMutation.mutate({
        id: editingModel.id,
        data: modelFormData,
      })
    } else {
      createModelMutation.mutate(modelFormData)
    }
  }

  const handleModelDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this model? All associated implementations will also be deleted.')) {
      deleteModelMutation.mutate(id)
    }
  }

  const handleImplOpen = (modelId: string, impl?: ModelImplementation) => {
    if (impl) {
      setEditingImpl(impl)
      setImplFormData({
        provider_id: impl.provider_id,
        model_id: impl.model_id,
        provider_model_id: impl.provider_model_id,
        version: impl.version || '',
        context_window: impl.context_window || 4096,
        pricing_info: impl.pricing_info || {},
        is_available: impl.is_available,
        sort_order: impl.sort_order || 0,
      })
    } else {
      setEditingImpl(null)
      setImplFormData({
        provider_id: '',
        model_id: modelId,
        provider_model_id: '',
        version: '',
        context_window: 4096,
        pricing_info: {},
        is_available: true,
        sort_order: 0,
      })
    }
    setError(null)
    setImplOpen(true)
  }

  const handleImplClose = () => {
    setImplOpen(false)
    setEditingImpl(null)
    setError(null)
  }

  const handleImplSubmit = () => {
    if (editingImpl) {
      updateImplMutation.mutate({
        id: editingImpl.id,
        data: implFormData,
      })
    } else {
      createImplMutation.mutate(implFormData)
    }
  }

  const handleImplDelete = (id: string) => {
    if (window.confirm('Delete this implementation?')) {
      deleteImplMutation.mutate(id)
    }
  }

  const addCapability = () => {
    if (capabilityInput && !modelFormData.capabilities.includes(capabilityInput)) {
      setModelFormData({
        ...modelFormData,
        capabilities: [...modelFormData.capabilities, capabilityInput],
      })
      setCapabilityInput('')
    }
  }

  const removeCapability = (cap: string) => {
    setModelFormData({
      ...modelFormData,
      capabilities: modelFormData.capabilities.filter(c => c !== cap),
    })
  }

  const getModelImplementations = (modelId: string) => {
    return implementations.filter(impl => impl.model_id === modelId)
  }

  const handleAccordionChange = (modelId: string) => (_: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedModel(isExpanded ? modelId : null)
  }

  const filteredModels = models.filter(model =>
    model.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    model.family.toLowerCase().includes(searchQuery.toLowerCase()) ||
    model.capabilities.some(cap => cap.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  if (!modelsLoading && models.length === 0) {
    return (
      <Box>
        <PageHeader
          title="Models"
          subtitle="Configure AI models and their provider implementations"
          breadcrumbs={[
            { label: 'Home', path: '/' },
            { label: 'Models' },
          ]}
        />
        <EmptyState
          icon={<ModelIcon />}
          title="No models configured"
          description="Add your first AI model to get started"
          action={{
            label: "Add Model",
            onClick: () => handleModelOpen(),
            startIcon: <AddIcon />
          }}
        />
      </Box>
    )
  }

  return (
    <Box>
      <PageHeader
        title="Models"
        subtitle="Configure AI models and their provider implementations"
        breadcrumbs={[
          { label: 'Home', path: '/' },
          { label: 'Models' },
        ]}
        action={
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleModelOpen()}
          >
            Add Model
          </Button>
        }
      />

      {/* Search Bar */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Search models by name, family, or capabilities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </CardContent>
      </Card>

      {/* Models Grid */}
      <Grid container spacing={3}>
        {filteredModels.map((model) => {
          const modelImplementations = getModelImplementations(model.id)
          const availableImplementations = modelImplementations.filter(impl => impl.is_available)
          
          return (
            <Grid item xs={12} key={model.id}>
              <Box>
                <ModelCard
                  name={model.name}
                  family={model.family}
                  capabilities={model.capabilities}
                  description={model.description}
                  implementationCount={modelImplementations.length}
                  availableCount={availableImplementations.length}
                  isExpanded={expandedModel === model.id}
                  onEdit={() => handleModelOpen(model)}
                  onDelete={() => handleModelDelete(model.id)}
                  onClick={() => handleAccordionChange(model.id)(null as any, expandedModel !== model.id)}
                />
                
                <Collapse in={expandedModel === model.id}>
                  <Card sx={{ mt: 2, ml: 7, border: `1px solid ${theme.palette.divider}` }}>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                        <Typography variant="h6" fontWeight={600}>
                          Provider Implementations
                        </Typography>
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<AddIcon />}
                          onClick={() => handleImplOpen(model.id)}
                        >
                          Add Implementation
                        </Button>
                      </Box>
                    
                      {modelImplementations.length === 0 ? (
                        <Box
                          sx={{
                            p: 3,
                            textAlign: 'center',
                            backgroundColor: alpha(theme.palette.grey[500], 0.04),
                            borderRadius: 2,
                            border: `1px dashed ${theme.palette.divider}`,
                          }}
                        >
                          <SettingsIcon sx={{ fontSize: 40, color: theme.palette.text.disabled, mb: 1 }} />
                          <Typography variant="body2" color="text.secondary">
                            No implementations configured for this model
                          </Typography>
                        </Box>
                      ) : (
                        <Grid container spacing={2}>
                          {modelImplementations.map((impl) => {
                            const provider = providers.find(p => p.id === impl.provider_id)
                            return (
                              <Grid item xs={12} md={6} key={impl.id}>
                                <Paper
                                  sx={{
                                    p: 2,
                                    border: `1px solid ${impl.is_available ? theme.palette.success.light : theme.palette.divider}`,
                                    backgroundColor: impl.is_available 
                                      ? alpha(theme.palette.success.main, 0.04) 
                                      : theme.palette.background.paper,
                                  }}
                                >
                                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                                    <Box>
                                      <Typography variant="subtitle1" fontWeight={600}>
                                        {provider?.name || 'Unknown'}
                                      </Typography>
                                      <Typography 
                                        variant="body2" 
                                        sx={{ 
                                          fontFamily: 'monospace',
                                          color: theme.palette.text.secondary,
                                        }}
                                      >
                                        {impl.provider_model_id}
                                      </Typography>
                                    </Box>
                                    <Box display="flex" gap={0.5}>
                                      <Tooltip title="Edit">
                                        <IconButton
                                          size="small"
                                          onClick={() => handleImplOpen(model.id, impl)}
                                        >
                                          <EditIcon fontSize="small" />
                                        </IconButton>
                                      </Tooltip>
                                      <Tooltip title="Delete">
                                        <IconButton
                                          size="small"
                                          color="error"
                                          onClick={() => handleImplDelete(impl.id)}
                                        >
                                          <DeleteIcon fontSize="small" />
                                        </IconButton>
                                      </Tooltip>
                                    </Box>
                                  </Box>
                                  
                                  <Box display="flex" gap={2} mb={1}>
                                    {impl.context_window && (
                                      <Box display="flex" alignItems="center" gap={0.5}>
                                        <MemoryIcon sx={{ fontSize: 16, color: theme.palette.text.secondary }} />
                                        <Typography variant="caption" color="text.secondary">
                                          {impl.context_window.toLocaleString()} tokens
                                        </Typography>
                                      </Box>
                                    )}
                                    {impl.version && (
                                      <Typography variant="caption" color="text.secondary">
                                        v{impl.version}
                                      </Typography>
                                    )}
                                  </Box>
                                  
                                  {(impl.pricing_info?.input_price || impl.pricing_info?.output_price) && (
                                    <Box 
                                      sx={{ 
                                        mt: 1, 
                                        p: 1, 
                                        backgroundColor: alpha(theme.palette.info.main, 0.08),
                                        borderRadius: 1,
                                      }}
                                    >
                                      <Box display="flex" alignItems="center" gap={0.5} mb={0.5}>
                                        <MoneyIcon sx={{ fontSize: 16, color: theme.palette.info.main }} />
                                        <Typography variant="caption" fontWeight={600} color="info.dark">
                                          Pricing per 1M tokens
                                        </Typography>
                                      </Box>
                                      <Box display="flex" gap={2}>
                                        {impl.pricing_info?.input_price && (
                                          <Typography variant="caption">
                                            Input: ${impl.pricing_info.input_price}
                                          </Typography>
                                        )}
                                        {impl.pricing_info?.output_price && (
                                          <Typography variant="caption">
                                            Output: ${impl.pricing_info.output_price}
                                          </Typography>
                                        )}
                                      </Box>
                                    </Box>
                                  )}
                                  
                                  <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                                    <Chip
                                      label={impl.is_available ? 'Available' : 'Unavailable'}
                                      size="small"
                                      color={impl.is_available ? 'success' : 'default'}
                                      icon={impl.is_available ? <CheckIcon /> : <CancelIcon />}
                                    />
                                    <Typography variant="caption" color="text.secondary">
                                      Priority: {impl.sort_order || 0}
                                    </Typography>
                                  </Box>
                                </Paper>
                              </Grid>
                            )
                          })}
                        </Grid>
                      )}
                    </CardContent>
                  </Card>
                </Collapse>
              </Box>
            </Grid>
          )
        })}
      </Grid>

      {/* Model Dialog */}
      <Dialog open={modelOpen} onClose={handleModelClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editingModel ? 'Edit Model' : 'Add Model'}</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <TextField
            margin="dense"
            label="Name"
            fullWidth
            value={modelFormData.name}
            onChange={(e) => setModelFormData({ ...modelFormData, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Family"
            fullWidth
            value={modelFormData.family}
            onChange={(e) => setModelFormData({ ...modelFormData, family: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={2}
            value={modelFormData.description}
            onChange={(e) => setModelFormData({ ...modelFormData, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <Box mb={2}>
            <Typography variant="subtitle2" gutterBottom>Capabilities</Typography>
            <Box display="flex" gap={1} mb={1}>
              <TextField
                size="small"
                value={capabilityInput}
                onChange={(e) => setCapabilityInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addCapability()
                  }
                }}
                placeholder="Add capability"
              />
              <Button size="small" onClick={addCapability}>Add</Button>
            </Box>
            <Box display="flex" gap={1} flexWrap="wrap">
              {modelFormData.capabilities.map((cap) => (
                <Chip
                  key={cap}
                  label={cap}
                  onDelete={() => removeCapability(cap)}
                  size="small"
                />
              ))}
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleModelClose}>Cancel</Button>
          <Button onClick={handleModelSubmit} variant="contained">
            {editingModel ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Implementation Dialog */}
      <Dialog open={implOpen} onClose={handleImplClose} maxWidth="sm" fullWidth>
        <DialogTitle>{editingImpl ? 'Edit Implementation' : 'Add Implementation'}</DialogTitle>
        <DialogContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <TextField
            select
            margin="dense"
            label="Provider"
            fullWidth
            value={implFormData.provider_id}
            onChange={(e) => setImplFormData({ ...implFormData, provider_id: e.target.value })}
            sx={{ mb: 2 }}
          >
            {providers.map((provider) => (
              <MenuItem key={provider.id} value={provider.id}>{provider.name}</MenuItem>
            ))}
          </TextField>
          <TextField
            margin="dense"
            label="Provider Model ID"
            fullWidth
            value={implFormData.provider_model_id}
            onChange={(e) => setImplFormData({ ...implFormData, provider_model_id: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Version"
            fullWidth
            value={implFormData.version}
            onChange={(e) => setImplFormData({ ...implFormData, version: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Context Window"
            fullWidth
            type="number"
            value={implFormData.context_window}
            onChange={(e) => setImplFormData({ ...implFormData, context_window: parseInt(e.target.value) || 0 })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Input Price (per 1M tokens)"
            fullWidth
            type="number"
            value={implFormData.pricing_info.input_price || ''}
            onChange={(e) => setImplFormData({
              ...implFormData,
              pricing_info: { ...implFormData.pricing_info, input_price: parseFloat(e.target.value) || undefined }
            })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Output Price (per 1M tokens)"
            fullWidth
            type="number"
            value={implFormData.pricing_info.output_price || ''}
            onChange={(e) => setImplFormData({
              ...implFormData,
              pricing_info: { ...implFormData.pricing_info, output_price: parseFloat(e.target.value) || undefined }
            })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Sort Order"
            fullWidth
            type="number"
            value={implFormData.sort_order}
            onChange={(e) => setImplFormData({ ...implFormData, sort_order: parseInt(e.target.value) || 0 })}
            helperText="Lower values have higher priority"
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={
              <Switch
                checked={implFormData.is_available}
                onChange={(e) => setImplFormData({ ...implFormData, is_available: e.target.checked })}
              />
            }
            label="Available"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleImplClose}>Cancel</Button>
          <Button onClick={handleImplSubmit} variant="contained">
            {editingImpl ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}