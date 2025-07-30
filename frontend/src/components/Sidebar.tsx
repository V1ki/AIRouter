import React from 'react'
import { 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  Typography,
  Divider,
  useTheme,
  alpha,
  Avatar,
  Chip
} from '@mui/material'
import { Link, useLocation } from 'react-router-dom'
import { 
  Dashboard as DashboardIcon,
  Layers as LayersIcon
} from '@mui/icons-material'

export interface NavItem {
  text: string
  icon: React.ReactElement
  path: string
  badge?: {
    label: string
    color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  }
}

interface SidebarProps {
  open: boolean
  onClose?: () => void
  variant?: 'permanent' | 'persistent' | 'temporary'
  navItems: NavItem[]
  width?: number
}

export function Sidebar({ 
  open, 
  onClose, 
  variant = 'permanent', 
  navItems,
  width = 280 
}: SidebarProps) {
  const theme = useTheme()
  const location = useLocation()

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo Section */}
      <Box sx={{ p: 3, pb: 2 }}>
        <Box display="flex" alignItems="center" gap={2}>
          <Avatar
            sx={{
              width: 48,
              height: 48,
              bgcolor: theme.palette.primary.main,
              fontSize: '1.5rem',
              fontWeight: 700,
            }}
          >
            <LayersIcon />
          </Avatar>
          <Box>
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 700,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              AI Router
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Management Console
            </Typography>
          </Box>
        </Box>
      </Box>

      <Divider sx={{ mx: 2 }} />

      {/* Navigation Items */}
      <List sx={{ flex: 1, pt: 2, px: 2 }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                component={Link}
                to={item.path}
                selected={isActive}
                sx={{
                  borderRadius: 2,
                  py: 1.5,
                  transition: 'all 0.2s ease',
                  '&.Mui-selected': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.08),
                    color: theme.palette.primary.main,
                    '& .MuiListItemIcon-root': {
                      color: theme.palette.primary.main,
                    },
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.12),
                    },
                  },
                  '&:hover': {
                    backgroundColor: alpha(theme.palette.primary.main, 0.04),
                  },
                }}
              >
                <ListItemIcon 
                  sx={{ 
                    minWidth: 40,
                    color: isActive ? 'inherit' : theme.palette.text.secondary,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  primaryTypographyProps={{
                    fontWeight: isActive ? 600 : 400,
                    fontSize: '0.875rem',
                  }}
                />
                {item.badge && (
                  <Chip
                    label={item.badge.label}
                    size="small"
                    color={item.badge.color || 'default'}
                    sx={{ 
                      height: 20,
                      fontSize: '0.75rem',
                      fontWeight: 600,
                    }}
                  />
                )}
              </ListItemButton>
            </ListItem>
          )
        })}
      </List>

      {/* Footer Section */}
      <Divider sx={{ mx: 2 }} />
      <Box sx={{ p: 2 }}>
        <Box
          sx={{
            p: 2,
            borderRadius: 2,
            backgroundColor: alpha(theme.palette.primary.main, 0.04),
            border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
          }}
        >
          <Typography variant="caption" color="text.secondary" display="block">
            Need help?
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              color: theme.palette.primary.main,
              fontWeight: 600,
              cursor: 'pointer',
              '&:hover': {
                textDecoration: 'underline',
              }
            }}
          >
            View Documentation
          </Typography>
        </Box>
      </Box>
    </Box>
  )

  return (
    <Drawer
      variant={variant}
      open={open}
      onClose={onClose}
      sx={{
        width: width,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: width,
          boxSizing: 'border-box',
          borderRight: `1px solid ${theme.palette.divider}`,
          backgroundColor: theme.palette.background.paper,
        },
      }}
    >
      {drawer}
    </Drawer>
  )
}

// Usage example:
// <Sidebar
//   open={true}
//   variant="permanent"
//   navItems={[
//     { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
//     { text: 'Providers', icon: <CloudIcon />, path: '/providers', badge: { label: '3', color: 'primary' } },
//   ]}
// />