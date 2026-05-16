import { useState } from 'react'

export default function Setup({ onComplete }) {
  const [name, setName] = useState('')
  const [userId, setUserId] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    const id = userId.trim() || name.trim().toLowerCase().replace(/\s+/g, '_')
    const displayName = name.trim()
    if (!id || !displayName) return
    localStorage.setItem('userId', id)
    localStorage.setItem('displayName', displayName)
    onComplete()
  }

  return (
    <div className="setup">
      <svg className="setup-icon" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <rect width="100" height="100" rx="22" fill="#0f0f1e"/>
        <circle cx="50" cy="50" r="36" fill="none" stroke="#7c3aed" strokeWidth="3" opacity="0.6"/>
        <ellipse cx="50" cy="50" rx="22" ry="14" fill="none" stroke="#a78bfa" strokeWidth="2.5"/>
        <circle cx="50" cy="50" r="9" fill="#7c3aed"/>
        <circle cx="50" cy="50" r="4" fill="#080813"/>
        <circle cx="53" cy="47" r="2" fill="#e0d0ff" opacity="0.7"/>
        <line x1="14" y1="50" x2="28" y2="50" stroke="#06b6d4" strokeWidth="1.5" opacity="0.5"/>
        <line x1="72" y1="50" x2="86" y2="50" stroke="#06b6d4" strokeWidth="1.5" opacity="0.5"/>
      </svg>

      <h1 className="setup-title">Psych Professor</h1>
      <p className="setup-subtitle">
        The Professor is watching. Every choice, every word — it all becomes data.
        Who are you?
      </p>

      <form className="setup-form" onSubmit={handleSubmit}>
        <input
          className="setup-input"
          type="text"
          placeholder="Your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoFocus
          required
        />
        <input
          className="setup-input"
          type="text"
          placeholder="Player ID (optional, auto-generated)"
          value={userId}
          onChange={(e) => setUserId(e.target.value.replace(/\s+/g, '_'))}
        />
        <button
          className="setup-btn"
          type="submit"
          disabled={!name.trim()}
        >
          Enter the Study
        </button>
      </form>
    </div>
  )
}
