import React from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Container,
} from '@mui/material'
import {
  Menu as MenuIcon,
  CloudQueue as ProvidersIcon,
  ModelTraining as ModelsIcon,
  Analytics as UsageIcon,
  Dashboard as DashboardIcon,
  AttachMoney as PricingIcon,
} from '@mui/icons-material'
import ProvidersPage from './pages/ProvidersPage'
import ModelsPage from './pages/ModelsPage'
import UsagePage from './pages/UsagePage'
import DashboardPage from './pages/DashboardPage'
import PricingPage from './pages/PricingPage'

const drawerWidth = 240

interface NavItem {
  text: string
  icon: React.ReactElement
  path: string
}

const navItems: NavItem[] = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Providers & Keys', icon: <ProvidersIcon />, path: '/providers' },
  { text: 'Models & Implementations', icon: <ModelsIcon />, path: '/models' },
  { text: 'Pricing', icon: <PricingIcon />, path: '/pricing' },
  { text: 'Usage', icon: <UsageIcon />, path: '/usage' },
]

export default function App() {
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const location = useLocation()

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap>
          AI Router
        </Typography>
      </Toolbar>
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={Link}
              to={item.path}
              selected={location.pathname === item.path}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  )

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            AI Router Management
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar />
        <Container maxWidth="lg">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/providers" element={<ProvidersPage />} />
            <Route path="/models" element={<ModelsPage />} />
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="/usage" element={<UsagePage />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  )
}