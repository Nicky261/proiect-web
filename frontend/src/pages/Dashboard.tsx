import { useEffect, useState } from 'react'
import { api } from '../api/client'

type Me = { id: number; email: string; username: string; roles: string[] }
type Post = { id: number; title: string; content: string; is_public: boolean; author_id: number }
type FileRec = { id: number; filename: string; size: number; object_name: string }

export default function Dashboard({ onLogout }: { onLogout: () => void }) {
  const [me, setMe] = useState<Me | null>(null)
  const [posts, setPosts] = useState<Post[]>([])
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [files, setFiles] = useState<FileRec[]>([])

  useEffect(() => {
    api.get('/users/me').then(r => setMe(r.data))
    api.get('/posts').then(r => setPosts(r.data))
    api.get('/files').then(r => setFiles(r.data)).catch(() => {})
  }, [])

  const createPost = async (e: React.FormEvent) => {
    e.preventDefault()
    const res = await api.post('/posts', { title, content, is_public: true })
    setPosts([res.data, ...posts])
    setTitle('')
    setContent('')
  }

  const upload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const input = e.currentTarget.elements.namedItem('f') as HTMLInputElement
    if (!input.files || input.files.length === 0) return
    const fd = new FormData()
    fd.append('f', input.files[0])
    await api.post('/files/upload', fd)
    const list = await api.get('/files')
    setFiles(list.data)
  }

  return (
    <div style={{ maxWidth: 900, margin: '24px auto', padding: 16 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Hub Studenti</h2>
        <div>
          <span style={{ marginRight: 12 }}>
            {me ? `Salut, ${me.username} (${me.roles.join(',')})` : ''}
          </span>
          <button onClick={onLogout}>Logout</button>
        </div>
      </header>

      <section style={{ marginTop: 24 }}>
        <h3>Creaza post</h3>
        <form onSubmit={createPost} style={{ display: 'grid', gap: 8 }}>
          <input placeholder='titlu' value={title} onChange={e => setTitle(e.target.value)} />
          <textarea placeholder='continut' value={content} onChange={e => setContent(e.target.value)} />
          <button type='submit'>Publica</button>
        </form>
      </section>

      <section style={{ marginTop: 24 }}>
        <h3>Drive-ul meu</h3>
        <form onSubmit={upload}>
          <input name='f' type='file' /> <button type='submit'>Upload</button>
        </form>
        <ul>
          {files.map(f => (
            <li key={f.id}>
              {f.filename} ({f.size} bytes)
            </li>
          ))}
        </ul>
      </section>

      <section style={{ marginTop: 24 }}>
        <h3>Feed public</h3>
        {posts.map(p => (
          <article
            key={p.id}
            style={{ border: '1px solid #ccc', borderRadius: 8, padding: 12, marginBottom: 12 }}
          >
            <h4 style={{ margin: 0 }}>{p.title}</h4>
            <p>{p.content}</p>
          </article>
        ))}
      </section>
    </div>
  )
}
