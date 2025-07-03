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
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import { modelService, modelImplementationService, providerService } from '../services/api'
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
  const queryClient = useQueryClient()
  const [modelOpen, setModelOpen] = useState(false)
  const [implOpen, setImplOpen] = useState(false)
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

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Models & Implementations</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleModelOpen()}
        >
          Add Model
        </Button>
      </Box>

      {models.length === 0 && !modelsLoading ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="textSecondary">No models found. Add a model to get started.</Typography>
        </Paper>
      ) : (
        <Box>
          {models.map((model) => {
            const modelImplementations = getModelImplementations(model.id)
            return (
              <Accordion
                key={model.id}
                expanded={expandedModel === model.id}
                onChange={handleAccordionChange(model.id)}
                sx={{ mb: 1 }}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" width="100%" pr={2}>
                    <Box flex={1}>
                      <Typography variant="h6">{model.name}</Typography>
                      <Box display="flex" gap={1} mt={0.5}>
                        <Chip label={model.family} size="small" color="primary" />
                        {model.capabilities.map((cap) => (
                          <Chip key={cap} label={cap} size="small" variant="outlined" />
                        ))}
                      </Box>
                    </Box>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Chip
                        icon={<SettingsIcon />}
                        label={`${modelImplementations.length} Implementation${modelImplementations.length !== 1 ? 's' : ''}`}
                        size="small"
                        color={modelImplementations.length > 0 ? 'success' : 'default'}
                      />
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleModelOpen(model)
                        }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleModelDelete(model.id)
                        }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  {model.description && (
                    <Typography variant="body2" color="textSecondary" paragraph>
                      {model.description}
                    </Typography>
                  )}
                  
                  <Box>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                      <Typography variant="subtitle1" fontWeight="bold">Implementations</Typography>
                      <Button
                        size="small"
                        startIcon={<AddIcon />}
                        onClick={() => handleImplOpen(model.id)}
                      >
                        Add Implementation
                      </Button>
                    </Box>
                    
                    {modelImplementations.length === 0 ? (
                      <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="body2" color="textSecondary">
                          No implementations configured for this model
                        </Typography>
                      </Paper>
                    ) : (
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Provider</TableCell>
                            <TableCell>Provider Model ID</TableCell>
                            <TableCell>Context Window</TableCell>
                            <TableCell>Pricing</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell align="right">Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {modelImplementations.map((impl) => {
                            const provider = providers.find(p => p.id === impl.provider_id)
                            return (
                              <TableRow key={impl.id}>
                                <TableCell>{provider?.name || 'Unknown'}</TableCell>
                                <TableCell>
                                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                    {impl.provider_model_id}
                                  </Typography>
                                </TableCell>
                                <TableCell>{impl.context_window?.toLocaleString() || '-'}</TableCell>
                                <TableCell>
                                  {impl.pricing_info?.input_price && impl.pricing_info?.output_price ? (
                                    <Typography variant="caption">
                                      In: ${impl.pricing_info.input_price}/1M<br />
                                      Out: ${impl.pricing_info.output_price}/1M
                                    </Typography>
                                  ) : '-'}
                                </TableCell>
                                <TableCell>
                                  <Chip
                                    label={impl.is_available ? 'Available' : 'Unavailable'}
                                    color={impl.is_available ? 'success' : 'default'}
                                    size="small"
                                  />
                                </TableCell>
                                <TableCell align="right">
                                  <IconButton
                                    size="small"
                                    onClick={() => handleImplOpen(model.id, impl)}
                                  >
                                    <EditIcon />
                                  </IconButton>
                                  <IconButton
                                    size="small"
                                    onClick={() => handleImplDelete(impl.id)}
                                  >
                                    <DeleteIcon />
                                  </IconButton>
                                </TableCell>
                              </TableRow>
                            )
                          })}
                        </TableBody>
                      </Table>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            )
          })}
        </Box>
      )}

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