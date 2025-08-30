import { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { api } from './api/client'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Admin from './pages/Admin'

function App() {
  const [auth, setAuth] = useState<boolean>(!!localStorage.getItem('token'))

  useEffect(() => {
    // putem verifica tokenul mai tarziu
  }, [])

  const handleLogin = () => setAuth(true)
  const handleLogout = () => {
    localStorage.removeItem('token')
    setAuth(false)
  }

  return (
    <Router>
      <Routes>
        {/* Rute publice */}
        <Route 
          path="/login" 
          element={auth ? <Navigate to="/dashboard" replace /> : <Login onLogin={handleLogin} />} 
        />
        <Route 
          path="/register" 
          element={auth ? <Navigate to="/dashboard" replace /> : <Register />} 
        />
        
        {/* Rute protejate */}
        <Route 
          path="/dashboard" 
          element={auth ? <Dashboard onLogout={handleLogout} /> : <Navigate to="/login" replace />} 
        />
        <Route 
          path="/admin" 
          element={auth ? <Admin /> : <Navigate to="/login" replace />} 
        />
        
        {/* Redirect default */}
        <Route 
          path="/" 
          element={<Navigate to={auth ? "/dashboard" : "/login"} replace />} 
        />
      </Routes>
    </Router>
  )
}

export default App