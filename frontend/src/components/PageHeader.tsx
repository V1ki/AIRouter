import React from 'react'
import { Box, Typography, Breadcrumbs, Link, Button, Skeleton } from '@mui/material'
import { NavigateNext as NavigateNextIcon } from '@mui/icons-material'
import { Link as RouterLink } from 'react-router-dom'

interface BreadcrumbItem {
  label: string
  path?: string
}

interface PageHeaderProps {
  title: string
  subtitle?: string
  breadcrumbs?: BreadcrumbItem[]
  action?: React.ReactNode
  loading?: boolean
}

export function PageHeader({ 
  title, 
  subtitle, 
  breadcrumbs = [], 
  action,
  loading = false 
}: PageHeaderProps) {
  if (loading) {
    return (
      <Box mb={4}>
        <Skeleton variant="text" width={200} height={16} sx={{ mb: 2 }} />
        <Skeleton variant="text" width={300} height={40} sx={{ mb: 1 }} />
        <Skeleton variant="text" width={400} height={20} />
      </Box>
    )
  }

  return (
    <Box mb={4}>
      {breadcrumbs.length > 0 && (
        <Breadcrumbs 
          separator={<NavigateNextIcon fontSize="small" />} 
          sx={{ mb: 2 }}
        >
          {breadcrumbs.map((crumb, index) => {
            const isLast = index === breadcrumbs.length - 1
            return isLast || !crumb.path ? (
              <Typography 
                key={crumb.label} 
                color="text.primary" 
                variant="body2"
                sx={{ fontWeight: isLast ? 600 : 400 }}
              >
                {crumb.label}
              </Typography>
            ) : (
              <Link
                key={crumb.label}
                component={RouterLink}
                to={crumb.path}
                color="inherit"
                variant="body2"
                sx={{ 
                  textDecoration: 'none',
                  '&:hover': {
                    textDecoration: 'underline'
                  }
                }}
              >
                {crumb.label}
              </Link>
            )
          })}
        </Breadcrumbs>
      )}
      
      <Box 
        display="flex" 
        justifyContent="space-between" 
        alignItems="flex-start"
        flexWrap="wrap"
        gap={2}
      >
        <Box>
          <Typography 
            variant="h4" 
            gutterBottom
            sx={{ 
              fontWeight: 700,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {title}
          </Typography>
          {subtitle && (
            <Typography 
              variant="body1" 
              color="text.secondary"
              sx={{ maxWidth: 600 }}
            >
              {subtitle}
            </Typography>
          )}
        </Box>
        {action && <Box>{action}</Box>}
      </Box>
    </Box>
  )
}

// Usage example:
// <PageHeader
//   title="Dashboard"
//   subtitle="Welcome back! Here's what's happening with your AI Router today."
//   breadcrumbs={[
//     { label: 'Home', path: '/' },
//     { label: 'Dashboard' }
//   ]}
//   action={
//     <Button variant="contained" startIcon={<AddIcon />}>
//       Add New
//     </Button>
//   }
// />