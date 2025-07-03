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
  MenuItem,
  Alert,
  Chip,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from '@mui/icons-material'
import { apiKeyService, providerService } from '../services/api'
import type { ApiKey, Provider } from '../types'

interface ApiKeyFormData {
  provider_id: string
  alias: string
  key: string
  sort_order: number
}

export default function ApiKeysPage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editingApiKey, setEditingApiKey] = useState<ApiKey | null>(null)
  const [formData, setFormData] = useState<ApiKeyFormData>({
    provider_id: '',
    alias: '',
    key: '',
    sort_order: 0,
  })
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({})
  const [error, setError] = useState<string | null>(null)

  const { data: apiKeys = [], isLoading } = useQuery({
    queryKey: ['apiKeys'],
    queryFn: apiKeyService.getAll,
  })

  const { data: providers = [] } = useQuery({
    queryKey: ['providers'],
    queryFn: providerService.getAll,
  })

  const createMutation = useMutation({
    mutationFn: apiKeyService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys'] })
      handleClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to create API key')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ApiKey> }) =>
      apiKeyService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys'] })
      handleClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to update API key')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: apiKeyService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiKeys'] })
    },
  })

  const handleOpen = (apiKey?: ApiKey) => {
    if (apiKey) {
      setEditingApiKey(apiKey)
      setFormData({
        provider_id: apiKey.provider_id,
        alias: apiKey.alias,
        key: apiKey.key,
        sort_order: apiKey.sort_order,
      })
    } else {
      setEditingApiKey(null)
      setFormData({
        provider_id: '',
        alias: '',
        key: '',
        sort_order: 0,
      })
    }
    setError(null)
    setOpen(true)
  }

  const handleClose = () => {
    setOpen(false)
    setEditingApiKey(null)
    setError(null)
  }

  const handleSubmit = () => {
    if (editingApiKey) {
      updateMutation.mutate({
        id: editingApiKey.id,
        data: formData,
      })
    } else {
      createMutation.mutate(formData)
    }
  }

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this API key?')) {
      deleteMutation.mutate(id)
    }
  }

  const toggleShowKey = (id: string) => {
    setShowKeys((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const maskKey = (key: string) => {
    if (key.length <= 8) return '********'
    return key.substring(0, 4) + '...' + key.substring(key.length - 4)
  }

  const getProviderName = (providerId: string) => {
    const provider = providers.find((p) => p.id === providerId)
    return provider?.name || 'Unknown'
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">API Keys</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpen()}
        >
          Add API Key
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Alias</TableCell>
              <TableCell>Provider</TableCell>
              <TableCell>Key</TableCell>
              <TableCell>Sort Order</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {apiKeys.map((apiKey) => (
              <TableRow key={apiKey.id}>
                <TableCell>{apiKey.alias}</TableCell>
                <TableCell>
                  <Chip label={getProviderName(apiKey.provider_id)} size="small" />
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {showKeys[apiKey.id] ? apiKey.key : maskKey(apiKey.key)}
                    </Typography>
                    <IconButton
                      size="small"
                      onClick={() => toggleShowKey(apiKey.id)}
                      sx={{ ml: 1 }}
                    >
                      {showKeys[apiKey.id] ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </Box>
                </TableCell>
                <TableCell>{apiKey.sort_order}</TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => handleOpen(apiKey)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(apiKey.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
            {apiKeys.length === 0 && !isLoading && (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No API keys found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
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
            select
            margin="dense"
            label="Provider"
            fullWidth
            value={formData.provider_id}
            onChange={(e) => setFormData({ ...formData, provider_id: e.target.value })}
            sx={{ mb: 2 }}
          >
            {providers.map((provider) => (
              <MenuItem key={provider.id} value={provider.id}>
                {provider.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            margin="dense"
            label="Alias"
            fullWidth
            value={formData.alias}
            onChange={(e) => setFormData({ ...formData, alias: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="API Key"
            fullWidth
            type={editingApiKey ? "password" : "text"}
            value={formData.key}
            onChange={(e) => setFormData({ ...formData, key: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Sort Order"
            fullWidth
            type="number"
            value={formData.sort_order}
            onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingApiKey ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}