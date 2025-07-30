import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  TextField,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  MenuItem,
  Tooltip,
  useTheme,
  alpha,
  InputAdornment,
} from '@mui/material'
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Search as SearchIcon,
  Key as KeyIcon,
} from '@mui/icons-material'
import { apiKeyService, providerService } from '../services/api'
import { PageHeader } from '../components/PageHeader'
import { EmptyState } from '../components/EmptyState'
import type { ApiKey, Provider } from '../types'

interface ApiKeyFormData {
  provider_id: string
  alias: string
  key: string
  sort_order: number
}

export default function ApiKeysPage() {
  const theme = useTheme()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [showKey, setShowKey] = useState<string | null>(null)
  const [editingApiKey, setEditingApiKey] = useState<ApiKey | null>(null)
  const [formData, setFormData] = useState<ApiKeyFormData>({
    provider_id: '',
    alias: '',
    key: '',
    sort_order: 0,
  })
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

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key)
    // You could add a toast notification here
  }

  const getProviderName = (providerId: string) => {
    return providers.find(p => p.id === providerId)?.name || 'Unknown'
  }

  const filteredKeys = apiKeys.filter(key =>
    key.alias.toLowerCase().includes(searchQuery.toLowerCase()) ||
    getProviderName(key.provider_id).toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (!isLoading && apiKeys.length === 0) {
    return (
      <Box>
        <PageHeader
          title="API Keys"
          subtitle="Manage your API keys for different providers"
          breadcrumbs={[
            { label: 'Home', path: '/' },
            { label: 'API Keys' },
          ]}
        />
        <EmptyState
          icon={<KeyIcon />}
          title="No API keys configured"
          description="Add your first API key to start using AI providers"
          action={{
            label: "Add API Key",
            onClick: () => handleOpen(),
            startIcon: <AddIcon />
          }}
        />
      </Box>
    )
  }

  return (
    <Box>
      <PageHeader
        title="API Keys"
        subtitle="Manage your API keys for different providers"
        breadcrumbs={[
          { label: 'Home', path: '/' },
          { label: 'API Keys' },
        ]}
        action={
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpen()}
          >
            Add API Key
          </Button>
        }
      />

      <Card>
        <CardContent>
          {/* Search Bar */}
          <TextField
            fullWidth
            placeholder="Search API keys..."
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

          {/* Table */}
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Provider</TableCell>
                  <TableCell>API Key</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredKeys.map((apiKey) => (
                  <TableRow 
                    key={apiKey.id}
                    sx={{
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.04),
                      },
                    }}
                  >
                    <TableCell>
                      <Typography variant="body2" fontWeight={500}>
                        {apiKey.alias}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getProviderName(apiKey.provider_id)}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography
                          variant="body2"
                          sx={{ fontFamily: 'monospace', color: theme.palette.text.secondary }}
                        >
                          {showKey === apiKey.id
                            ? apiKey.key
                            : `${apiKey.key.substring(0, 8)}${'•'.repeat(16)}`}
                        </Typography>
                        <IconButton
                          size="small"
                          onClick={() => setShowKey(showKey === apiKey.id ? null : apiKey.id)}
                        >
                          {showKey === apiKey.id ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                        <Tooltip title="Copy API Key">
                          <IconButton
                            size="small"
                            onClick={() => handleCopyKey(apiKey.key)}
                          >
                            <CopyIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={apiKey.sort_order || 0}
                        size="small"
                        sx={{
                          backgroundColor: alpha(theme.palette.info.main, 0.1),
                          color: theme.palette.info.dark,
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(apiKey.created_at).toLocaleDateString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Edit">
                        <IconButton
                          size="small"
                          onClick={() => handleOpen(apiKey)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDelete(apiKey.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Dialog */}
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
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            value={formData.alias}
            onChange={(e) => setFormData({ ...formData, alias: e.target.value })}
            sx={{ mb: 2 }}
            helperText="A friendly name to identify this API key"
          />
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
            label="API Key"
            fullWidth
            type="password"
            value={formData.key}
            onChange={(e) => setFormData({ ...formData, key: e.target.value })}
            sx={{ mb: 2 }}
            helperText="Your secret API key from the provider"
          />
          <TextField
            margin="dense"
            label="Priority Order"
            fullWidth
            type="number"
            value={formData.sort_order}
            onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) || 0 })}
            helperText="Lower values have higher priority (0 = highest)"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={!formData.alias || !formData.key || !formData.provider_id}
          >
            {editingApiKey ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}