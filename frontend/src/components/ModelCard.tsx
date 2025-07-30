import React from 'react'
import {
  Card,
  CardContent,
  Box,
  Typography,
  Chip,
  IconButton,
  useTheme,
  alpha,
  Tooltip,
  LinearProgress,
} from '@mui/material'
import {
  ModelTraining as ModelIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material'

interface ModelCardProps {
  name: string
  family: string
  capabilities: string[]
  description?: string
  implementationCount: number
  availableCount: number
  onEdit: () => void
  onDelete: () => void
  onClick: () => void
  isExpanded?: boolean
}

export function ModelCard({
  name,
  family,
  capabilities,
  description,
  implementationCount,
  availableCount,
  onEdit,
  onDelete,
  onClick,
  isExpanded = false,
}: ModelCardProps) {
  const theme = useTheme()
  const availabilityRate = implementationCount > 0 ? (availableCount / implementationCount) * 100 : 0

  return (
    <Card
      sx={{
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        border: `1px solid ${isExpanded ? theme.palette.primary.main : theme.palette.divider}`,
        backgroundColor: isExpanded ? alpha(theme.palette.primary.main, 0.04) : 'transparent',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: theme.shadows[4],
          borderColor: theme.palette.primary.main,
        },
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box display="flex" alignItems="flex-start" justifyContent="space-between">
          <Box flex={1}>
            {/* Header */}
            <Box display="flex" alignItems="center" gap={2} mb={2}>
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  backgroundColor: alpha(theme.palette.primary.main, 0.1),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <ModelIcon color="primary" />
              </Box>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  {name}
                </Typography>
                <Chip 
                  label={family} 
                  size="small" 
                  sx={{
                    backgroundColor: alpha(theme.palette.secondary.main, 0.1),
                    color: theme.palette.secondary.dark,
                    fontWeight: 500,
                  }}
                />
              </Box>
            </Box>

            {/* Description */}
            {description && (
              <Typography 
                variant="body2" 
                color="text.secondary" 
                sx={{ mb: 2, maxWidth: '80%' }}
              >
                {description}
              </Typography>
            )}

            {/* Capabilities */}
            <Box display="flex" gap={0.5} flexWrap="wrap" mb={2}>
              {capabilities.map((cap) => (
                <Chip
                  key={cap}
                  label={cap}
                  size="small"
                  variant="outlined"
                  sx={{
                    borderColor: alpha(theme.palette.primary.main, 0.3),
                    fontSize: '0.75rem',
                  }}
                />
              ))}
            </Box>

            {/* Stats */}
            <Box>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                <Typography variant="caption" color="text.secondary" fontWeight={500}>
                  Implementation Availability
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {availableCount} of {implementationCount} available
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={availabilityRate}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: alpha(theme.palette.grey[500], 0.1),
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 3,
                    backgroundColor: 
                      availabilityRate === 100 ? theme.palette.success.main :
                      availabilityRate >= 50 ? theme.palette.warning.main :
                      theme.palette.error.main,
                  },
                }}
              />
            </Box>

            {/* Implementation Summary */}
            <Box display="flex" gap={2} mt={2}>
              <Box display="flex" alignItems="center" gap={0.5}>
                <SettingsIcon sx={{ fontSize: 16, color: theme.palette.text.secondary }} />
                <Typography variant="caption" color="text.secondary">
                  {implementationCount} Implementation{implementationCount !== 1 ? 's' : ''}
                </Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={0.5}>
                <CheckIcon sx={{ fontSize: 16, color: theme.palette.success.main }} />
                <Typography variant="caption" color="text.secondary">
                  {availableCount} Available
                </Typography>
              </Box>
              {implementationCount - availableCount > 0 && (
                <Box display="flex" alignItems="center" gap={0.5}>
                  <CancelIcon sx={{ fontSize: 16, color: theme.palette.error.main }} />
                  <Typography variant="caption" color="text.secondary">
                    {implementationCount - availableCount} Unavailable
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>

          {/* Actions */}
          <Box display="flex" flexDirection="column" gap={0.5}>
            <Tooltip title="Edit Model">
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation()
                  onEdit()
                }}
                sx={{
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.1),
                  },
                }}
              >
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete Model">
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete()
                }}
                sx={{
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.error.main, 0.1),
                    color: theme.palette.error.main,
                  },
                }}
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

// Usage example:
// <ModelCard
//   name="GPT-4"
//   family="OpenAI"
//   capabilities={['text-generation', 'code-generation', 'chat']}
//   description="Most capable GPT-4 model"
//   implementationCount={3}
//   availableCount={2}
//   onEdit={() => console.log('Edit')}
//   onDelete={() => console.log('Delete')}
//   onClick={() => console.log('Click')}
// />