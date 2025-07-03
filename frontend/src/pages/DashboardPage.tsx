import React from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  CircularProgress,
} from '@mui/material'
import {
  CloudQueue as ProvidersIcon,
  VpnKey as ApiKeysIcon,
  ModelTraining as ModelsIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material'
import { providerService, apiKeyService, modelService, usageService } from '../services/api'

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactElement
  color: string
}

function StatCard({ title, value, icon, color }: StatCardProps) {
  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4">{value}</Typography>
          </Box>
          <Box
            sx={{
              backgroundColor: color,
              borderRadius: '50%',
              width: 56,
              height: 56,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

export default function DashboardPage() {
  const { data: providers = [] } = useQuery({
    queryKey: ['providers'],
    queryFn: providerService.getAll,
  })

  const { data: apiKeys = [] } = useQuery({
    queryKey: ['apiKeys'],
    queryFn: apiKeyService.getAll,
  })

  const { data: models = [] } = useQuery({
    queryKey: ['models'],
    queryFn: modelService.getAll,
  })

  const { data: usageStats = [] } = useQuery({
    queryKey: ['usageStats', 'today'],
    queryFn: () => {
      const today = new Date().toISOString().split('T')[0]
      return usageService.getStats({
        start_date: today,
        end_date: today,
      })
    },
  })

  const todayTokens = usageStats.reduce((sum, stat) => sum + stat.total_tokens, 0)

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Providers"
            value={providers.length}
            icon={<ProvidersIcon />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="API Keys"
            value={apiKeys.length}
            icon={<ApiKeysIcon />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Models"
            value={models.length}
            icon={<ModelsIcon />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Tokens Today"
            value={todayTokens.toLocaleString()}
            icon={<TrendingUpIcon />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Quick Stats
      </Typography>
      
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1" paragraph>
          Welcome to AI Router Management Interface. Use the navigation menu to manage providers,
          API keys, models, and view usage statistics.
        </Typography>
        
        <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
          Recent Activity
        </Typography>
        <Typography variant="body2" color="textSecondary">
          No recent activity to display.
        </Typography>
      </Paper>
    </Box>
  )
}