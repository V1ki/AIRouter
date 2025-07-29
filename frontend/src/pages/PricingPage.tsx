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
} from '@mui/material'
import { 
  Edit as EditIcon
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface ModelPrice {
  model_id: string
  provider_model_id: string
  input_price: number
  output_price: number
  last_updated: string | null
  provider_name: string
  model_name: string
}

interface PriceComparison {
  [family: string]: Array<{
    provider: string
    model: string
    provider_model_id: string
    input_price: number
    output_price: number
    context_window: number
  }>
}

const pricingService = {
  getAll: async (): Promise<ModelPrice[]> => {
    const { data } = await axios.get(`${API_BASE_URL}/api/pricing/`)
    return data
  },
  
  update: async (modelId: string, prices: { input_price: number; output_price: number }) => {
    const { data } = await axios.put(`${API_BASE_URL}/api/pricing/model/${modelId}`, prices)
    return data
  },
  
  
  getComparison: async (): Promise<PriceComparison> => {
    const { data } = await axios.get(`${API_BASE_URL}/api/pricing/comparison`)
    return data
  }
}

export default function PricingPage() {
  const queryClient = useQueryClient()
  const [editOpen, setEditOpen] = useState(false)
  const [editingPrice, setEditingPrice] = useState<ModelPrice | null>(null)
  const [priceForm, setPriceForm] = useState({
    input_price: 0,
    output_price: 0,
  })
  const [showComparison, setShowComparison] = useState(false)

  const { data: prices = [], isLoading } = useQuery({
    queryKey: ['prices'],
    queryFn: pricingService.getAll,
  })

  const { data: comparison = {} } = useQuery({
    queryKey: ['price-comparison'],
    queryFn: pricingService.getComparison,
    enabled: showComparison,
  })

  const updatePriceMutation = useMutation({
    mutationFn: ({ modelId, prices }: { modelId: string; prices: typeof priceForm }) =>
      pricingService.update(modelId, prices),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prices'] })
      handleClose()
    },
  })


  const handleEdit = (price: ModelPrice) => {
    setEditingPrice(price)
    setPriceForm({
      input_price: price.input_price,
      output_price: price.output_price,
    })
    setEditOpen(true)
  }

  const handleClose = () => {
    setEditOpen(false)
    setEditingPrice(null)
  }

  const handleSubmit = () => {
    if (editingPrice) {
      updatePriceMutation.mutate({
        modelId: editingPrice.model_id,
        prices: priceForm,
      })
    }
  }

  const formatPrice = (price: number) => {
    return `$${price.toFixed(4)}`
  }

  const calculateMonthlyCost = (inputPrice: number, outputPrice: number) => {
    // Assume 10M input tokens and 5M output tokens per month for estimation
    const monthlyInput = 10
    const monthlyOutput = 5
    return (inputPrice * monthlyInput) + (outputPrice * monthlyOutput)
  }

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Model Pricing</Typography>
        <Button
          variant="outlined"
          onClick={() => setShowComparison(!showComparison)}
        >
          {showComparison ? 'Hide' : 'Show'} Comparison
        </Button>
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

      {/* Edit Dialog */}
      <Dialog open={editOpen} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          Edit Pricing - {editingPrice?.model_name}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              label="Input Price (per 1M tokens)"
              type="number"
              fullWidth
              margin="normal"
              value={priceForm.input_price}
              onChange={(e) => setPriceForm({ ...priceForm, input_price: parseFloat(e.target.value) })}
              inputProps={{ step: 0.0001, min: 0 }}
            />
            <TextField
              label="Output Price (per 1M tokens)"
              type="number"
              fullWidth
              margin="normal"
              value={priceForm.output_price}
              onChange={(e) => setPriceForm({ ...priceForm, output_price: parseFloat(e.target.value) })}
              inputProps={{ step: 0.0001, min: 0 }}
            />
            <Alert severity="info" sx={{ mt: 2 }}>
              Prices are in USD per million tokens. Most models charge between $0.01 and $100 per million tokens.
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            Update Price
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}