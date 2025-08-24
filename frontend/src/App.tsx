import { useEffect, useState } from 'react'
import { api } from './api/client'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'

function App() {
  const [auth, setAuth] = useState<boolean>(!!localStorage.getItem('token'))

  useEffect(() => {
    // putem verifica tokenul mai tarziu
  }, [])

  return auth ? (
    <Dashboard onLogout={() => { localStorage.removeItem('token'); setAuth(false) }} />
  ) : (
    <Login onLogin={() => setAuth(true)} />
  )
}

export default App
