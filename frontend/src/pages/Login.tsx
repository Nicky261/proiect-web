import { useState } from 'react'
import { api } from '../api/client'

export default function Login({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    const data = new URLSearchParams()
    data.append('username', username)
    data.append('password', password)
    try {
      const res = await api.post('/auth/login', data)
      localStorage.setItem('token', res.data.access_token)
      onLogin()
    } catch (err) {
      alert('Login failed')
    }
  }

  return (
    <form
      onSubmit={submit}
      style={{ display: 'grid', gap: 12, maxWidth: 320, margin: '64px auto' }}
    >
      <h2>Login</h2>
      <input
        placeholder='username'
        value={username}
        onChange={e => setUsername(e.target.value)}
      />
      <input
        placeholder='password'
        type='password'
        value={password}
        onChange={e => setPassword(e.target.value)}
      />
      <button type='submit'>Sign in</button>
    </form>
  )
}
