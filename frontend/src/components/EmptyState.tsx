import React from 'react'
import { Box, Typography, Button, useTheme, alpha } from '@mui/material'
import { SvgIconComponent } from '@mui/icons-material'

interface EmptyStateProps {
  icon: React.ReactElement<SvgIconComponent>
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
    startIcon?: React.ReactElement
  }
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  const theme = useTheme()
  
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        px: 3,
        textAlign: 'center',
        backgroundColor: theme.palette.grey[50],
        borderRadius: 3,
        border: `2px dashed ${theme.palette.grey[300]}`,
      }}
    >
      <Box
        sx={{
          width: 80,
          height: 80,
          borderRadius: '50%',
          backgroundColor: alpha(theme.palette.primary.main, 0.1),
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 3,
          '& svg': {
            fontSize: 40,
            color: theme.palette.primary.main,
          }
        }}
      >
        {icon}
      </Box>
      
      <Typography 
        variant="h6" 
        gutterBottom
        sx={{ fontWeight: 600, color: theme.palette.text.primary }}
      >
        {title}
      </Typography>
      
      {description && (
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ mb: 3, maxWidth: 400 }}
        >
          {description}
        </Typography>
      )}
      
      {action && (
        <Button
          variant="contained"
          onClick={action.onClick}
          startIcon={action.startIcon}
          sx={{ mt: 2 }}
        >
          {action.label}
        </Button>
      )}
    </Box>
  )
}

// Usage example:
// <EmptyState
//   icon={<FolderOpenIcon />}
//   title="No data yet"
//   description="Get started by adding your first item"
//   action={{
//     label: "Add Item",
//     onClick: () => console.log('Add clicked'),
//     startIcon: <AddIcon />
//   }}
// />