const BASE = import.meta.env.VITE_API_URL ?? ''

async function request(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body !== undefined) opts.body = JSON.stringify(body)
  const res = await fetch(BASE + path, opts)
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`)
  return res.json()
}

const post = (path, body) => request('POST', path, body)
const get = (path) => request('GET', path)

export const api = {
  health: () => get('/api/health'),

  // profile + session travel with every request; server returns updated versions
  chat: (userId, displayName, message, profile, session) =>
    post('/api/chat', { user_id: userId, display_name: displayName, message, profile, session }),

  startSession: (userId, displayName, profile) =>
    post('/api/session/start', { user_id: userId, display_name: displayName, profile }),

  endSession: (userId, profile, session) =>
    post('/api/session/end', { user_id: userId, profile, session }),
}
