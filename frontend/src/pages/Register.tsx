import { useState } from 'react'
import { api } from '../api/client'

export default function Register() {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/auth/register', { email, username, password })
      alert('Registered! Now login.')
    } catch (err) {
      alert('Register failed')
    }
  }

  return (
    <form
      onSubmit={submit}
      style={{ display: 'grid', gap: 12, maxWidth: 360, margin: '64px auto' }}
    >
      <h2>Register</h2>
      <input
        placeholder='email'
        value={email}
        onChange={e => setEmail(e.target.value)}
      />
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
      <button type='submit'>Create account</button>
    </form>
  )
}
