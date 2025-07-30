import React from 'react'
import { Card, CardContent, Box, Typography, useTheme, alpha, Skeleton } from '@mui/material'
import { TrendingUp, TrendingDown } from '@mui/icons-material'

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ReactElement
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  trend?: {
    value: number
    label: string
  }
  loading?: boolean
}

export function StatCard({ 
  title, 
  value, 
  icon, 
  color = 'primary',
  trend,
  loading = false 
}: StatCardProps) {
  const theme = useTheme()
  const colorValue = theme.palette[color].main

  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box display="flex" alignItems="flex-start" justifyContent="space-between">
            <Box flex={1}>
              <Skeleton variant="text" width="60%" height={20} />
              <Skeleton variant="text" width="80%" height={40} sx={{ mt: 1 }} />
              <Skeleton variant="text" width="40%" height={16} sx={{ mt: 2 }} />
            </Box>
            <Skeleton variant="circular" width={56} height={56} />
          </Box>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card 
      sx={{ 
        height: '100%',
        background: `linear-gradient(135deg, ${alpha(colorValue, 0.08)} 0%, ${alpha(colorValue, 0.02)} 100%)`,
        borderColor: alpha(colorValue, 0.2),
        transition: 'all 0.3s ease-in-out',
        cursor: 'pointer',
        '&:hover': {
          borderColor: colorValue,
          transform: 'translateY(-4px)',
        }
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="flex-start" justifyContent="space-between">
          <Box flex={1}>
            <Typography 
              variant="body2" 
              color="text.secondary" 
              gutterBottom
              sx={{ fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.5px' }}
            >
              {title}
            </Typography>
            <Typography 
              variant="h4" 
              sx={{ 
                fontWeight: 700,
                color: 'text.primary',
                mt: 1,
                mb: trend ? 2 : 0
              }}
            >
              {value}
            </Typography>
            {trend && (
              <Box display="flex" alignItems="center" gap={0.5}>
                {trend.value >= 0 ? (
                  <TrendingUp sx={{ fontSize: 16, color: 'success.main' }} />
                ) : (
                  <TrendingDown sx={{ fontSize: 16, color: 'error.main' }} />
                )}
                <Typography
                  variant="body2"
                  sx={{
                    color: trend.value >= 0 ? 'success.main' : 'error.main',
                    fontWeight: 600
                  }}
                >
                  {Math.abs(trend.value)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {trend.label}
                </Typography>
              </Box>
            )}
          </Box>
          <Box
            sx={{
              backgroundColor: alpha(colorValue, 0.1),
              borderRadius: 3,
              width: 56,
              height: 56,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: colorValue,
              '& svg': {
                fontSize: 28
              }
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

// Usage example:
// <StatCard
//   title="Total Revenue"
//   value="$12,543"
//   icon={<AttachMoneyIcon />}
//   color="success"
//   trend={{ value: 12.5, label: "from last month" }}
// />