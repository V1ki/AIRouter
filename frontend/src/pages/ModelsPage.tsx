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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Chip,
  Alert,
  Tabs,
  Tab,
  MenuItem,
  FormControlLabel,
  Switch,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material'
import { modelService, modelImplementationService, providerService } from '../services/api'
import type { Model, ModelImplementation, Provider } from '../types'

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
  const [tab, setTab] = useState(0)
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

  const { data: models = [], isLoading: modelsLoading } = useQuery({
    queryKey: ['models'],
    queryFn: modelService.getAll,
  })

  const { data: implementations = [], isLoading: implLoading } = useQuery({
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

  const handleImplOpen = (impl?: ModelImplementation) => {
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
        sort_order: impl.sort_order,
      })
    } else {
      setEditingImpl(null)
      setImplFormData({
        provider_id: '',
        model_id: '',
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

  const addCapability = () => {
    if (capabilityInput && !modelFormData.capabilities.includes(capabilityInput)) {
      setModelFormData({
        ...modelFormData,
        capabilities: [...modelFormData.capabilities, capabilityInput],
      })
      setCapabilityInput('')
    }
  }

  const removeCapability = (capability: string) => {
    setModelFormData({
      ...modelFormData,
      capabilities: modelFormData.capabilities.filter(c => c !== capability),
    })
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Models & Implementations
      </Typography>

      <Paper sx={{ mb: 2 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)}>
          <Tab label="Models" />
          <Tab label="Implementations" />
        </Tabs>
      </Paper>

      {tab === 0 && (
        <Box>
          <Box display="flex" justifyContent="flex-end" mb={2}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleModelOpen()}
            >
              Add Model
            </Button>
          </Box>

          {models.map((model) => (
            <Accordion key={model.id}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box display="flex" alignItems="center" width="100%">
                  <Typography sx={{ flexGrow: 1 }}>
                    {model.name} - <Chip label={model.family} size="small" />
                  </Typography>
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
                      if (window.confirm('Delete this model?')) {
                        deleteModelMutation.mutate(model.id)
                      }
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="textSecondary" paragraph>
                  {model.description || 'No description'}
                </Typography>
                <Box mb={2}>
                  <Typography variant="subtitle2">Capabilities:</Typography>
                  <Box display="flex" gap={1} flexWrap="wrap" mt={1}>
                    {model.capabilities.map((cap) => (
                      <Chip key={cap} label={cap} size="small" />
                    ))}
                  </Box>
                </Box>
              </AccordionDetails>
            </Accordion>
          ))}
        </Box>
      )}

      {tab === 1 && (
        <Box>
          <Box display="flex" justifyContent="flex-end" mb={2}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleImplOpen()}
            >
              Add Implementation
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Model</TableCell>
                  <TableCell>Provider</TableCell>
                  <TableCell>Provider Model ID</TableCell>
                  <TableCell>Version</TableCell>
                  <TableCell>Context Window</TableCell>
                  <TableCell>Pricing</TableCell>
                  <TableCell>Available</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {implementations.map((impl) => {
                  const model = models.find(m => m.id === impl.model_id)
                  const provider = providers.find(p => p.id === impl.provider_id)
                  return (
                    <TableRow key={impl.id}>
                      <TableCell>{model?.name || 'Unknown'}</TableCell>
                      <TableCell>{provider?.name || 'Unknown'}</TableCell>
                      <TableCell>{impl.provider_model_id}</TableCell>
                      <TableCell>{impl.version || '-'}</TableCell>
                      <TableCell>{impl.context_window || '-'}</TableCell>
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
                          label={impl.is_available ? 'Yes' : 'No'}
                          color={impl.is_available ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <IconButton size="small" onClick={() => handleImplOpen(impl)}>
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => {
                            if (window.confirm('Delete this implementation?')) {
                              deleteImplMutation.mutate(impl.id)
                            }
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  )}
                )}
              </TableBody>
            </Table>
          </TableContainer>
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
                onKeyPress={(e) => e.key === 'Enter' && addCapability()}
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
            label="Model"
            fullWidth
            value={implFormData.model_id}
            onChange={(e) => setImplFormData({ ...implFormData, model_id: e.target.value })}
            sx={{ mb: 2 }}
          >
            {models.map((model) => (
              <MenuItem key={model.id} value={model.id}>{model.name}</MenuItem>
            ))}
          </TextField>
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