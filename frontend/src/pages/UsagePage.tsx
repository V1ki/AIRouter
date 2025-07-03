import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
} from '@mui/material'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { usageService, providerService, modelService } from '../services/api'
import { format, subDays } from 'date-fns'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

export default function UsagePage() {
  const [dateRange, setDateRange] = useState('7days')
  const [groupBy, setGroupBy] = useState<'day' | 'provider' | 'model'>('day')
  
  const { startDate, endDate } = React.useMemo(() => {
    const end = new Date()
    let start = new Date()
    
    switch (dateRange) {
      case '7days':
        start = subDays(end, 7)
        break
      case '30days':
        start = subDays(end, 30)
        break
      case 'today':
        start = new Date(end.toDateString())
        break
    }
    
    return {
      startDate: start.toISOString(),
      endDate: end.toISOString(),
    }
  }, [dateRange])

  const { data: providers = [] } = useQuery({
    queryKey: ['providers'],
    queryFn: providerService.getAll,
  })

  const { data: models = [] } = useQuery({
    queryKey: ['models'],
    queryFn: modelService.getAll,
  })

  const { data: usageStats = [], isLoading } = useQuery({
    queryKey: ['usageStats', startDate, endDate, groupBy],
    queryFn: () => usageService.getStats({
      start_date: startDate,
      end_date: endDate,
      group_by: groupBy,
    }),
  })

  const { data: usageDetails = [] } = useQuery({
    queryKey: ['usageDetails', startDate, endDate],
    queryFn: () => usageService.getDetails({
      start_date: startDate,
      end_date: endDate,
    }),
  })

  const totalTokens = usageStats.reduce((sum, stat) => sum + stat.total_tokens, 0)
  const totalCost = usageStats.reduce((sum, stat) => sum + stat.total_cost, 0)

  const chartData = React.useMemo(() => {
    if (groupBy === 'day') {
      return usageStats.map(stat => ({
        date: format(new Date(stat.date), 'MMM dd'),
        tokens: stat.total_tokens,
        cost: stat.total_cost,
      }))
    } else {
      return usageStats.map(stat => ({
        name: stat.provider || stat.model || 'Unknown',
        tokens: stat.total_tokens,
        cost: stat.total_cost,
      }))
    }
  }, [usageStats, groupBy])

  const pieData = React.useMemo(() => {
    const aggregated = new Map<string, number>()
    
    usageDetails.forEach(usage => {
      const provider = providers.find(p => 
        p.id === usage.model_implementation?.provider_id
      )?.name || 'Unknown'
      
      aggregated.set(provider, (aggregated.get(provider) || 0) + usage.total_tokens)
    })
    
    return Array.from(aggregated.entries()).map(([name, value]) => ({
      name,
      value,
    }))
  }, [usageDetails, providers])

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Token Usage Statistics
      </Typography>

      <Box display="flex" gap={2} mb={3}>
        <FormControl size="small">
          <InputLabel>Date Range</InputLabel>
          <Select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            label="Date Range"
          >
            <MenuItem value="today">Today</MenuItem>
            <MenuItem value="7days">Last 7 Days</MenuItem>
            <MenuItem value="30days">Last 30 Days</MenuItem>
          </Select>
        </FormControl>
        
        <FormControl size="small">
          <InputLabel>Group By</InputLabel>
          <Select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value as any)}
            label="Group By"
          >
            <MenuItem value="day">Day</MenuItem>
            <MenuItem value="provider">Provider</MenuItem>
            <MenuItem value="model">Model</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Tokens
              </Typography>
              <Typography variant="h4">
                {totalTokens.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Cost
              </Typography>
              <Typography variant="h4">
                ${totalCost.toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {isLoading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <Grid container spacing={3}>
            <Grid item xs={12} lg={8}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  {groupBy === 'day' ? 'Usage Over Time' : 'Usage by ' + groupBy}
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  {groupBy === 'day' ? (
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="tokens"
                        stroke="#8884d8"
                        name="Tokens"
                      />
                      <Line
                        type="monotone"
                        dataKey="cost"
                        stroke="#82ca9d"
                        name="Cost ($)"
                      />
                    </LineChart>
                  ) : (
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="tokens" fill="#8884d8" name="Tokens" />
                      <Bar dataKey="cost" fill="#82ca9d" name="Cost ($)" />
                    </BarChart>
                  )}
                </ResponsiveContainer>
              </Paper>
            </Grid>
            
            <Grid item xs={12} lg={4}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Usage by Provider
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Paper>
            </Grid>
          </Grid>

          <Paper sx={{ mt: 3, p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Usage Details
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>API Key</TableCell>
                    <TableCell>Model</TableCell>
                    <TableCell align="right">Prompt Tokens</TableCell>
                    <TableCell align="right">Completion Tokens</TableCell>
                    <TableCell align="right">Total Tokens</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {usageDetails.slice(0, 10).map((usage) => {
                    const model = models.find(m => 
                      m.id === usage.model_implementation?.model_id
                    )
                    return (
                      <TableRow key={usage.timestamp}>
                        <TableCell>
                          {format(new Date(usage.timestamp), 'MMM dd HH:mm')}
                        </TableCell>
                        <TableCell>{usage.api_key?.alias || 'Unknown'}</TableCell>
                        <TableCell>{model?.name || 'Unknown'}</TableCell>
                        <TableCell align="right">{usage.prompt_tokens}</TableCell>
                        <TableCell align="right">{usage.completion_tokens}</TableCell>
                        <TableCell align="right">{usage.total_tokens}</TableCell>
                      </TableRow>
                    )
                  })}
                  {usageDetails.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        No usage data available
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </>
      )}
    </Box>
  )
}