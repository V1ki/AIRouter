import React from 'react'
import { Routes, Route } from 'react-router-dom'
import {
  AppBar,
  Box,
  IconButton,
  Toolbar,
  Typography,
  Container,
  useTheme,
  useMediaQuery,
  Avatar,
  Tooltip,
  Badge,
} from '@mui/material'
import {
  Menu as MenuIcon,
  CloudQueue as ProvidersIcon,
  ModelTraining as ModelsIcon,
  Analytics as UsageIcon,
  Dashboard as DashboardIcon,
  AttachMoney as PricingIcon,
  VpnKey as ApiKeyIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import { Sidebar, NavItem } from './components/Sidebar'
import ProvidersPage from './pages/ProvidersPage'
import ModelsPage from './pages/ModelsPage'
import UsagePage from './pages/UsagePage'
import DashboardPage from './pages/DashboardPage'
import PricingPage from './pages/PricingPage'
import ApiKeysPage from './pages/ApiKeysPage'

const drawerWidth = 280

const navItems: NavItem[] = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Providers', icon: <ProvidersIcon />, path: '/providers' },
  { text: 'API Keys', icon: <ApiKeyIcon />, path: '/api-keys' },
  { text: 'Models', icon: <ModelsIcon />, path: '/models' },
  { text: 'Pricing', icon: <PricingIcon />, path: '/pricing' },
  { text: 'Usage Analytics', icon: <UsageIcon />, path: '/usage' },
]

export default function App() {
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: theme.palette.background.default }}>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          backgroundColor: theme.palette.background.paper,
          borderBottom: `1px solid ${theme.palette.divider}`,
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box display="flex" alignItems="center">
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { md: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography 
              variant="h6" 
              noWrap 
              component="div"
              sx={{ 
                fontWeight: 600,
                color: theme.palette.text.primary,
              }}
            >
              Welcome back!
            </Typography>
          </Box>
          
          <Box display="flex" alignItems="center" gap={1}>
            <Tooltip title="Notifications">
              <IconButton size="large" color="inherit">
                <Badge badgeContent={3} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Settings">
              <IconButton size="large" color="inherit">
                <SettingsIcon />
              </IconButton>
            </Tooltip>
            
            <Tooltip title="Profile">
              <IconButton size="large" sx={{ ml: 1 }}>
                <Avatar 
                  sx={{ 
                    width: 36, 
                    height: 36,
                    bgcolor: theme.palette.primary.main,
                  }}
                >
                  U
                </Avatar>
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>
      
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Sidebar
          open={!isMobile || mobileOpen}
          onClose={handleDrawerToggle}
          variant={isMobile ? 'temporary' : 'permanent'}
          navItems={navItems}
          width={drawerWidth}
        />
      </Box>
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
        }}
      >
        <Toolbar />
        <Container 
          maxWidth="xl" 
          sx={{ 
            py: 4,
            px: { xs: 2, sm: 3, md: 4 },
          }}
        >
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/providers" element={<ProvidersPage />} />
            <Route path="/api-keys" element={<ApiKeysPage />} />
            <Route path="/models" element={<ModelsPage />} />
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="/usage" element={<UsagePage />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  )
}