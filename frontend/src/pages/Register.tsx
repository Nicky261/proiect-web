import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function Register() {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/auth/register', { email, username, password })
      alert('Cont creat cu succes! Acum te poți loga.')
      navigate('/login')
    } catch (err) {
      alert('Înregistrarea a eșuat')
    }
  }

  return (
    <form
      onSubmit={submit}
      style={{ display: 'grid', gap: 12, maxWidth: 360, margin: '64px auto' }}
    >
      <h2>Înregistrare</h2>
      <input
        placeholder='Email'
        type='email'
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
      />
      <input
        placeholder='Username'
        value={username}
        onChange={e => setUsername(e.target.value)}
        required
      />
      <input
        placeholder='Parolă'
        type='password'
        value={password}
        onChange={e => setPassword(e.target.value)}
        required
      />
      <button type='submit'>Creează cont</button>
      
      <div style={{ textAlign: 'center', marginTop: '16px' }}>
        <Link to="/login">Ai deja cont? Loghează-te</Link>
      </div>
    </form>
  )
}