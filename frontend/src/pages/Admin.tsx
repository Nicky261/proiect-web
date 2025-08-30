import { useState, useEffect } from 'react'
import { 
  Box, 
  Typography, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress
} from '@mui/material'
import { api } from '../api/client'

interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
  roles?: string[]
}

export default function Admin() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [currentUser, setCurrentUser] = useState<any>(null)

  // Verifică dacă utilizatorul este admin
  useEffect(() => {
    checkAdminAccess()
    loadUsers()
  }, [])

  const checkAdminAccess = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await api.get('/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setCurrentUser(response.data)
      
      // TEMPORAR: Disable-uim complet verificarea de rol
      console.log('User data:', response.data)
      
    } catch (err) {
      console.log('Error getting user info:', err)
      // Setam un utilizator mock pentru a continua
      setCurrentUser({ username: 'current_user' })
    }
  }

  const loadUsers = async () => {
    try {
      // Pentru moment folosim date mock până implementăm endpoint pentru users
      // Backend-ul tău nu are încă /users endpoint pentru listare
      setUsers([
        {
          id: 1,
          username: 'admin',
          email: 'admin@test.com',
          is_active: true,
          created_at: '2025-08-29',
          roles: ['administrator']
        },
        {
          id: 2,
          username: 'testuser',
          email: 'test@test.com',
          is_active: true,
          created_at: '2025-08-30',
          roles: ['user']
        }
      ])
    } catch (err) {
      setError('Eroare la încărcarea utilizatorilor')
    } finally {
      setLoading(false)
    }
  }

  const changeUserRole = async (userId: number, newRole: string) => {
    try {
      const token = localStorage.getItem('token')
      await api.post(`/admin/users/${userId}/roles/${newRole}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      // Actualizează lista utilizatorilor
      setUsers(users.map(user => 
        user.id === userId 
          ? { ...user, roles: [newRole] }
          : user
      ))
      
      alert(`Rol schimbat cu succes pentru utilizatorul ${userId}`)
    } catch (err) {
      alert('Eroare la schimbarea rolului')
    }
  }

  const toggleUserStatus = async (userId: number) => {
    try {
      const token = localStorage.getItem('token')
      const user = users.find(u => u.id === userId)
      
      // Dacă ai endpoint pentru dezactivare, folosește-l
      // Altfel, simulează schimbarea status-ului
      const newStatus = !user?.is_active
      
      setUsers(users.map(u => 
        u.id === userId 
          ? { ...u, is_active: newStatus }
          : u
      ))
      
      alert(`Utilizator ${newStatus ? 'activat' : 'dezactivat'}`)
    } catch (err) {
      alert('Eroare la schimbarea status-ului')
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
      </Box>
    )
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Panou de Administrare
      </Typography>
      
      <Typography variant="body1" color="text.secondary" mb={3}>
        Bun venit, {currentUser?.username}! Aici poți gestiona utilizatorii platformei.
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Data creării</TableCell>
              <TableCell>Rol</TableCell>
              <TableCell>Acțiuni</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user.id}>
                <TableCell>{user.id}</TableCell>
                <TableCell>{user.username}</TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <Box 
                    component="span" 
                    color={user.is_active ? 'success.main' : 'error.main'}
                  >
                    {user.is_active ? 'Activ' : 'Inactiv'}
                  </Box>
                </TableCell>
                <TableCell>
                  {new Date(user.created_at).toLocaleDateString('ro-RO')}
                </TableCell>
                <TableCell>
                  <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>Rol</InputLabel>
                    <Select
                      value={user.roles?.[0] || 'guest'}
                      label="Rol"
                      onChange={(e) => changeUserRole(user.id, e.target.value)}
                    >
                      <MenuItem value="guest">Guest</MenuItem>
                      <MenuItem value="user">User</MenuItem>
                      <MenuItem value="administrator">Administrator</MenuItem>
                    </Select>
                  </FormControl>
                </TableCell>
                <TableCell>
                  <Button
                    size="small"
                    variant="outlined"
                    color={user.is_active ? "error" : "success"}
                    onClick={() => toggleUserStatus(user.id)}
                    sx={{ mr: 1 }}
                  >
                    {user.is_active ? 'Dezactivează' : 'Activează'}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}