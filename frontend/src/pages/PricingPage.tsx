import { useState } from 'react'
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  Tooltip,
  CircularProgress,
  Card,
  CardContent,
  Grid,
  Snackbar,
  FormControlLabel,
  Checkbox,
} from '@mui/material'
import {
  Edit as EditIcon,
  Sync as SyncIcon,
  Preview as PreviewIcon,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  pricingService,
  type ModelPrice,
  type SyncPreviewDetail,
} from '../services/api'

const SOURCE_CHIP_CONFIG: Record<string, { label: string; color: 'primary' | 'secondary' | 'default' | 'info' | 'warning' }> = {
  litellm: { label: 'LiteLLM', color: 'primary' },
  manual: { label: 'Manual', color: 'secondary' },
  config: { label: 'Config', color: 'default' },
  bulk_update: { label: 'Bulk', color: 'info' },
}

export default function PricingPage() {
  const queryClient = useQueryClient()

  // Edit dialog state
  const [editOpen, setEditOpen] = useState(false)
  const [editingPrice, setEditingPrice] = useState<ModelPrice | null>(null)
  const [priceForm, setPriceForm] = useState({ input_price: 0, output_price: 0 })

  // Sync dialog state
  const [syncPreviewOpen, setSyncPreviewOpen] = useState(false)
  const [syncOnlyMissing, setSyncOnlyMissing] = useState(false)

  // Comparison toggle
  const [showComparison, setShowComparison] = useState(false)

  // Snackbar
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' }>({
    open: false,
    message: '',
    severity: 'success',
  })

  // Queries
  const { data: prices = [], isLoading } = useQuery({
    queryKey: ['prices'],
    queryFn: pricingService.getAll,
  })

  const { data: comparison = {} } = useQuery({
    queryKey: ['price-comparison'],
    queryFn: pricingService.getComparison,
    enabled: showComparison,
  })

  const {
    data: syncPreview,
    isLoading: isPreviewLoading,
    refetch: refetchPreview,
  } = useQuery({
    queryKey: ['sync-preview'],
    queryFn: pricingService.previewSync,
    enabled: false,
  })

  // Mutations
  const updatePriceMutation = useMutation({
    mutationFn: ({ modelId, prices }: { modelId: string; prices: { input_price: number; output_price: number } }) =>
      pricingService.update(modelId, prices),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prices'] })
      setSnackbar({ open: true, message: 'Price updated successfully', severity: 'success' })
      handleCloseEdit()
    },
    onError: () => {
      setSnackbar({ open: true, message: 'Failed to update price', severity: 'error' })
    },
  })

  const syncMutation = useMutation({
    mutationFn: (params: { only_missing?: boolean }) => pricingService.syncFromLiteLLM(params),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['prices'] })
      setSyncPreviewOpen(false)
      setSnackbar({
        open: true,
        message: `Sync complete: ${result.updated_count} updated, ${result.skipped_count} skipped, ${result.not_found_count} not found`,
        severity: 'success',
      })
    },
    onError: () => {
      setSnackbar({ open: true, message: 'Failed to sync from LiteLLM', severity: 'error' })
    },
  })

  // Handlers
  const handleEdit = (price: ModelPrice) => {
    setEditingPrice(price)
    setPriceForm({ input_price: price.input_price, output_price: price.output_price })
    setEditOpen(true)
  }

  const handleCloseEdit = () => {
    setEditOpen(false)
    setEditingPrice(null)
  }

  const handleSubmitEdit = () => {
    if (editingPrice) {
      updatePriceMutation.mutate({ modelId: editingPrice.model_id, prices: priceForm })
    }
  }

  const handleOpenSyncPreview = async () => {
    setSyncPreviewOpen(true)
    refetchPreview()
  }

  const handleConfirmSync = () => {
    syncMutation.mutate({ only_missing: syncOnlyMissing })
  }

  const formatPrice = (price: number) => `$${price.toFixed(4)}`

  const calculateMonthlyCost = (inputPrice: number, outputPrice: number) => {
    // Assume 10M input tokens and 5M output tokens per month
    return inputPrice * 10 + outputPrice * 5
  }

  const getSourceChip = (updatedBy: string | null) => {
    if (!updatedBy) return null
    const config = SOURCE_CHIP_CONFIG[updatedBy] || { label: updatedBy, color: 'default' as const }
    return <Chip label={config.label} size="small" color={config.color} variant="outlined" />
  }

  // Separate preview details into categories
  const changedModels = syncPreview?.details.filter((d) => d.price_changed) ?? []
  const matchedNoChange = syncPreview?.details.filter((d) => d.has_litellm_price && !d.price_changed) ?? []
  const notFoundModels = syncPreview?.details.filter((d) => !d.has_litellm_price) ?? []

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Model Pricing</Typography>
        <Box display="flex" gap={1}>
          <Button variant="outlined" startIcon={<SyncIcon />} onClick={handleOpenSyncPreview}>
            Sync from LiteLLM
          </Button>
          <Button variant="outlined" onClick={() => setShowComparison(!showComparison)}>
            {showComparison ? 'Hide' : 'Show'} Comparison
          </Button>
        </Box>
      </Box>

      {/* Price Comparison */}
      {showComparison && (
        <Box mb={4}>
          <Typography variant="h5" gutterBottom>
            Price Comparison by Model Family
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(comparison).map(([family, models]) => (
              <Grid item xs={12} md={6} key={family}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {family.toUpperCase()} Family
                    </Typography>
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Provider</TableCell>
                            <TableCell>Model</TableCell>
                            <TableCell align="right">Input</TableCell>
                            <TableCell align="right">Output</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {models.map((model, index) => (
                            <TableRow key={index}>
                              <TableCell>{model.provider}</TableCell>
                              <TableCell>{model.model}</TableCell>
                              <TableCell align="right">{formatPrice(model.input_price)}</TableCell>
                              <TableCell align="right">{formatPrice(model.output_price)}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Main Price Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Provider</TableCell>
              <TableCell>Model</TableCell>
              <TableCell>Model ID</TableCell>
              <TableCell align="right">Input Price</TableCell>
              <TableCell align="right">Output Price</TableCell>
              <TableCell align="right">Est. Monthly Cost</TableCell>
              <TableCell>Source</TableCell>
              <TableCell>Last Updated</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {prices.map((price) => {
              const monthlyCost = calculateMonthlyCost(price.input_price, price.output_price)
              return (
                <TableRow key={price.model_id}>
                  <TableCell>{price.provider_name}</TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      {price.model_name}
                      {price.input_price === 0 && price.output_price === 0 && (
                        <Chip label="FREE" size="small" color="success" />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                      {price.provider_model_id}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {formatPrice(price.input_price)}
                    <Typography variant="caption" display="block" color="text.secondary">
                      per 1M tokens
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {formatPrice(price.output_price)}
                    <Typography variant="caption" display="block" color="text.secondary">
                      per 1M tokens
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Based on 10M input + 5M output tokens/month">
                      <Box>
                        {formatPrice(monthlyCost)}
                        <Typography variant="caption" display="block" color="text.secondary">
                          estimated
                        </Typography>
                      </Box>
                    </Tooltip>
                  </TableCell>
                  <TableCell>{getSourceChip(price.updated_by)}</TableCell>
                  <TableCell>
                    {price.last_updated ? (
                      new Date(price.last_updated).toLocaleDateString()
                    ) : (
                      <Typography variant="caption" color="text.secondary">
                        Never
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton size="small" onClick={() => handleEdit(price)}>
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Edit Price Dialog */}
      <Dialog open={editOpen} onClose={handleCloseEdit} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Pricing - {editingPrice?.model_name}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              label="Input Price (per 1M tokens)"
              type="number"
              fullWidth
              margin="normal"
              value={priceForm.input_price}
              onChange={(e) => setPriceForm({ ...priceForm, input_price: parseFloat(e.target.value) || 0 })}
              inputProps={{ step: 0.0001, min: 0 }}
            />
            <TextField
              label="Output Price (per 1M tokens)"
              type="number"
              fullWidth
              margin="normal"
              value={priceForm.output_price}
              onChange={(e) => setPriceForm({ ...priceForm, output_price: parseFloat(e.target.value) || 0 })}
              inputProps={{ step: 0.0001, min: 0 }}
            />
            <Alert severity="info" sx={{ mt: 2 }}>
              Prices are in USD per million tokens. This will mark the source as "Manual".
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEdit}>Cancel</Button>
          <Button onClick={handleSubmitEdit} variant="contained" disabled={updatePriceMutation.isPending}>
            Update Price
          </Button>
        </DialogActions>
      </Dialog>

      {/* LiteLLM Sync Preview Dialog */}
      <Dialog open={syncPreviewOpen} onClose={() => setSyncPreviewOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <PreviewIcon />
            Sync Pricing from LiteLLM
          </Box>
        </DialogTitle>
        <DialogContent>
          {isPreviewLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : syncPreview ? (
            <Box>
              {/* Summary */}
              <Grid container spacing={2} sx={{ mb: 3, mt: 1 }}>
                <Grid item xs={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h5">{syncPreview.total_models}</Typography>
                    <Typography variant="caption" color="text.secondary">Total Models</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h5" color="primary">{syncPreview.matched_in_litellm}</Typography>
                    <Typography variant="caption" color="text.secondary">Found in LiteLLM</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h5" color="warning.main">{syncPreview.would_change}</Typography>
                    <Typography variant="caption" color="text.secondary">Would Change</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={3}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h5" color="text.secondary">{syncPreview.not_found_in_litellm}</Typography>
                    <Typography variant="caption" color="text.secondary">Not Found</Typography>
                  </Paper>
                </Grid>
              </Grid>

              <FormControlLabel
                control={<Checkbox checked={syncOnlyMissing} onChange={(e) => setSyncOnlyMissing(e.target.checked)} />}
                label="Only update models without existing pricing"
                sx={{ mb: 2 }}
              />

              {/* Changed models table */}
              {changedModels.length > 0 && (
                <Box mb={3}>
                  <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Price Changes ({changedModels.length})
                  </Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Provider</TableCell>
                          <TableCell>Model</TableCell>
                          <TableCell align="right">Current Input</TableCell>
                          <TableCell align="right">New Input</TableCell>
                          <TableCell align="right">Current Output</TableCell>
                          <TableCell align="right">New Output</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {changedModels.map((d: SyncPreviewDetail) => (
                          <TableRow key={d.model_implementation_id}>
                            <TableCell>{d.provider_name}</TableCell>
                            <TableCell>{d.model_name ?? d.provider_model_id}</TableCell>
                            <TableCell align="right">{formatPrice(d.current_input_price)}</TableCell>
                            <TableCell align="right" sx={{ color: 'warning.main', fontWeight: 'bold' }}>
                              {formatPrice(d.litellm_input_price ?? 0)}
                            </TableCell>
                            <TableCell align="right">{formatPrice(d.current_output_price)}</TableCell>
                            <TableCell align="right" sx={{ color: 'warning.main', fontWeight: 'bold' }}>
                              {formatPrice(d.litellm_output_price ?? 0)}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}

              {/* Matched but no change */}
              {matchedNoChange.length > 0 && (
                <Box mb={3}>
                  <Typography variant="subtitle1" gutterBottom color="text.secondary">
                    Already Up-to-date ({matchedNoChange.length})
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {matchedNoChange.map((d) => d.model_name ?? d.provider_model_id).join(', ')}
                  </Typography>
                </Box>
              )}

              {/* Not found */}
              {notFoundModels.length > 0 && (
                <Box>
                  <Typography variant="subtitle1" gutterBottom color="text.secondary">
                    Not Found in LiteLLM ({notFoundModels.length})
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {notFoundModels.map((d) => d.provider_model_id).join(', ')}
                  </Typography>
                </Box>
              )}
            </Box>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSyncPreviewOpen(false)}>Cancel</Button>
          <Button
            onClick={handleConfirmSync}
            variant="contained"
            startIcon={<SyncIcon />}
            disabled={syncMutation.isPending || isPreviewLoading || (syncPreview?.would_change === 0 && !syncOnlyMissing)}
          >
            {syncMutation.isPending ? 'Syncing...' : `Sync ${syncOnlyMissing ? '(Missing Only)' : 'All'}`}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={5000}
        onClose={() => setSnackbar((s) => ({ ...s, open: false }))}
      >
        <Alert
          onClose={() => setSnackbar((s) => ({ ...s, open: false }))}
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}
