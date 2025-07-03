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
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material'
import { providerService } from '../services/api'
import type { Provider } from '../types'

interface ProviderFormData {
  name: string
  base_url: string
  description: string
  free_quota_type?: 'CREDIT' | 'SHARED_TOKENS' | 'PER_MODEL_TOKENS'
}

export default function ProvidersPage() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [editingProvider, setEditingProvider] = useState<Provider | null>(null)
  const [formData, setFormData] = useState<ProviderFormData>({
    name: '',
    base_url: '',
    description: '',
  })
  const [error, setError] = useState<string | null>(null)

  const { data: providers = [], isLoading } = useQuery({
    queryKey: ['providers'],
    queryFn: providerService.getAll,
  })

  const createMutation = useMutation({
    mutationFn: providerService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      handleClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to create provider')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Provider> }) =>
      providerService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
      handleClose()
    },
    onError: (error: any) => {
      setError(error.response?.data?.detail || 'Failed to update provider')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: providerService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] })
    },
  })

  const handleOpen = (provider?: Provider) => {
    if (provider) {
      setEditingProvider(provider)
      setFormData({
        name: provider.name,
        base_url: provider.base_url,
        description: provider.description || '',
        free_quota_type: provider.free_quota_type,
      })
    } else {
      setEditingProvider(null)
      setFormData({
        name: '',
        base_url: '',
        description: '',
      })
    }
    setError(null)
    setOpen(true)
  }

  const handleClose = () => {
    setOpen(false)
    setEditingProvider(null)
    setError(null)
  }

  const handleSubmit = () => {
    if (editingProvider) {
      updateMutation.mutate({
        id: editingProvider.id,
        data: formData,
      })
    } else {
      createMutation.mutate(formData)
    }
  }

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this provider?')) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Providers</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpen()}
        >
          Add Provider
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Base URL</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Free Quota Type</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {providers.map((provider) => (
              <TableRow key={provider.id}>
                <TableCell>{provider.name}</TableCell>
                <TableCell>{provider.base_url}</TableCell>
                <TableCell>{provider.description || '-'}</TableCell>
                <TableCell>{provider.free_quota_type || '-'}</TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => handleOpen(provider)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(provider.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
            {providers.length === 0 && !isLoading && (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No providers found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
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
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Base URL"
            fullWidth
            value={formData.base_url}
            onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            multiline
            rows={2}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            sx={{ mb: 2 }}
          />
          <TextField
            select
            margin="dense"
            label="Free Quota Type"
            fullWidth
            value={formData.free_quota_type || ''}
            onChange={(e) => setFormData({ ...formData, free_quota_type: e.target.value as any })}
          >
            <MenuItem value="">None</MenuItem>
            <MenuItem value="CREDIT">Credit</MenuItem>
            <MenuItem value="SHARED_TOKENS">Shared Tokens</MenuItem>
            <MenuItem value="PER_MODEL_TOKENS">Per Model Tokens</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingProvider ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}