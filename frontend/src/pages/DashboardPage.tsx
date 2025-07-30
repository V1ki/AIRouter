import React from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  useTheme,
  alpha,
  LinearProgress,
} from '@mui/material'
import {
  CloudQueue as ProvidersIcon,
  VpnKey as ApiKeysIcon,
  ModelTraining as ModelsIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  DataUsage as DataUsageIcon,
  Timeline as TimelineIcon,
  AccountTree as AccountTreeIcon,
} from '@mui/icons-material'
import { providerService, apiKeyService, modelService, usageService } from '../services/api'
import { StatCard } from '../components/StatCard'
import { PageHeader } from '../components/PageHeader'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

// Mock data for charts
const mockUsageData = [
  { date: 'Mon', tokens: 45000 },
  { date: 'Tue', tokens: 52000 },
  { date: 'Wed', tokens: 48000 },
  { date: 'Thu', tokens: 61000 },
  { date: 'Fri', tokens: 55000 },
  { date: 'Sat', tokens: 42000 },
  { date: 'Sun', tokens: 38000 },
]

const mockModelUsage = [
  { model: 'GPT-4', usage: 35 },
  { model: 'Claude 3', usage: 28 },
  { model: 'GPT-3.5', usage: 20 },
  { model: 'Llama 2', usage: 12 },
  { model: 'Others', usage: 5 },
]

export default function DashboardPage() {
  const theme = useTheme()
  
  const { data: providers = [], isLoading: providersLoading } = useQuery({
    queryKey: ['providers'],
    queryFn: providerService.getAll,
  })

  const { data: apiKeys = [], isLoading: apiKeysLoading } = useQuery({
    queryKey: ['apiKeys'],
    queryFn: apiKeyService.getAll,
  })

  const { data: models = [], isLoading: modelsLoading } = useQuery({
    queryKey: ['models'],
    queryFn: modelService.getAll,
  })

  const { data: usageStats = [], isLoading: usageLoading } = useQuery({
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
  const activeProviders = providers.filter(p => apiKeys.some(k => k.provider_id === p.id)).length
  const totalRequests = usageStats.reduce((sum, stat) => sum + (stat.request_count || 0), 0)

  return (
    <Box>
      <PageHeader
        title="Dashboard"
        subtitle="Monitor your AI Router performance and usage at a glance"
        breadcrumbs={[
          { label: 'Home', path: '/' },
          { label: 'Dashboard' },
        ]}
      />
      
      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Active Providers"
            value={activeProviders}
            icon={<ProvidersIcon />}
            color="primary"
            trend={{ value: 12.5, label: "from last week" }}
            loading={providersLoading}
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="API Keys"
            value={apiKeys.length}
            icon={<ApiKeysIcon />}
            color="success"
            trend={{ value: 8.2, label: "from last week" }}
            loading={apiKeysLoading}
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Active Models"
            value={models.length}
            icon={<ModelsIcon />}
            color="warning"
            loading={modelsLoading}
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Requests Today"
            value={totalRequests.toLocaleString()}
            icon={<SpeedIcon />}
            color="info"
            trend={{ value: -5.4, label: "from yesterday" }}
            loading={usageLoading}
          />
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Token Usage Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Box>
                  <Typography variant="h6" gutterBottom fontWeight={600}>
                    Token Usage Trend
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Daily token consumption over the last 7 days
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center" gap={1}>
                  <TimelineIcon color="primary" />
                  <Typography variant="h5" fontWeight={700} color="primary">
                    {todayTokens.toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    tokens today
                  </Typography>
                </Box>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={mockUsageData}>
                  <defs>
                    <linearGradient id="tokenGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                  <XAxis 
                    dataKey="date" 
                    stroke={theme.palette.text.secondary}
                    style={{ fontSize: '0.875rem' }}
                  />
                  <YAxis 
                    stroke={theme.palette.text.secondary}
                    style={{ fontSize: '0.875rem' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: theme.palette.background.paper,
                      border: `1px solid ${theme.palette.divider}`,
                      borderRadius: 8,
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="tokens" 
                    stroke={theme.palette.primary.main} 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#tokenGradient)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Model Usage Distribution */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box mb={3}>
                <Typography variant="h6" gutterBottom fontWeight={600}>
                  Model Usage Distribution
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Percentage breakdown by model
                </Typography>
              </Box>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={mockModelUsage} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                  <XAxis type="number" stroke={theme.palette.text.secondary} />
                  <YAxis 
                    dataKey="model" 
                    type="category" 
                    stroke={theme.palette.text.secondary}
                    width={60}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: theme.palette.background.paper,
                      border: `1px solid ${theme.palette.divider}`,
                      borderRadius: 8,
                    }}
                    formatter={(value: any) => `${value}%`}
                  />
                  <Bar 
                    dataKey="usage" 
                    fill={theme.palette.secondary.main}
                    radius={[0, 8, 8, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Status */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                System Health
              </Typography>
              <Box sx={{ mt: 3 }}>
                {[
                  { label: 'API Gateway', status: 'operational', value: 99.9 },
                  { label: 'Provider Connections', status: 'operational', value: 100 },
                  { label: 'Response Time', status: 'warning', value: 85 },
                  { label: 'Error Rate', status: 'operational', value: 98.5 },
                ].map((item) => (
                  <Box key={item.label} sx={{ mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Typography variant="body2" fontWeight={500}>
                        {item.label}
                      </Typography>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Box
                          sx={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            backgroundColor: item.status === 'operational' 
                              ? theme.palette.success.main 
                              : theme.palette.warning.main,
                          }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {item.value}%
                        </Typography>
                      </Box>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={item.value} 
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        backgroundColor: alpha(theme.palette.primary.main, 0.1),
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 3,
                          backgroundColor: item.status === 'operational' 
                            ? theme.palette.success.main 
                            : theme.palette.warning.main,
                        },
                      }}
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Recent Activity
              </Typography>
              <Box sx={{ mt: 3 }}>
                {[
                  { time: '2 min ago', action: 'New API key created for OpenAI', type: 'key' },
                  { time: '15 min ago', action: 'Model gpt-4-turbo updated', type: 'model' },
                  { time: '1 hour ago', action: 'Provider Anthropic connected', type: 'provider' },
                  { time: '3 hours ago', action: 'Usage limit alert triggered', type: 'alert' },
                ].map((activity, index) => (
                  <Box 
                    key={index} 
                    sx={{ 
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 2,
                      mb: 2,
                      pb: 2,
                      borderBottom: index < 3 ? `1px solid ${theme.palette.divider}` : 'none',
                    }}
                  >
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: 2,
                        backgroundColor: alpha(
                          activity.type === 'key' ? theme.palette.success.main :
                          activity.type === 'model' ? theme.palette.info.main :
                          activity.type === 'provider' ? theme.palette.primary.main :
                          theme.palette.warning.main,
                          0.1
                        ),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {
                        activity.type === 'key' ? <ApiKeysIcon fontSize="small" color="success" /> :
                        activity.type === 'model' ? <ModelsIcon fontSize="small" color="info" /> :
                        activity.type === 'provider' ? <ProvidersIcon fontSize="small" color="primary" /> :
                        <TrendingUpIcon fontSize="small" color="warning" />
                      }
                    </Box>
                    <Box flex={1}>
                      <Typography variant="body2" fontWeight={500}>
                        {activity.action}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {activity.time}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}