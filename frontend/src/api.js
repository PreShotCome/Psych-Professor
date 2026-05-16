const BASE = import.meta.env.VITE_API_URL ?? ''

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== undefined) opts.body = JSON.stringify(body)
  const res = await fetch(BASE + path, opts)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status}: ${text}`)
  }
  return res.json()
}

const get = (path) => request('GET', path)
const post = (path, body) => request('POST', path, body)

export const api = {
  health: () => get('/api/health'),
  chat: (userId, displayName, message) =>
    post('/api/chat', { user_id: userId, display_name: displayName, message }),
  startSession: (userId, displayName) =>
    post('/api/session/start', { user_id: userId, display_name: displayName }),
  endSession: (userId) =>
    post('/api/session/end', { user_id: userId }),
  getProfile: (userId) => get(`/api/profile/${userId}`),
  getSession: (userId) => get(`/api/session/${userId}`),
}
