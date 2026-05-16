import { useState, useEffect } from 'react'
import { api } from '../api'
import TraitBar from './TraitBar'

const TRAIT_NAMES = [
  'moral', 'law', 'aggression', 'deception', 'empathy',
  'dominance', 'impulsivity', 'curiosity', 'paranoia', 'manipulation',
]

function divergenceColor(d) {
  if (d < 0.15) return 'var(--good)'
  if (d < 0.35) return 'var(--warn)'
  return 'var(--evil)'
}

export default function ProfilePanel({ userId, displayName }) {
  const [profile, setProfile] = useState(null)
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [startingSession, setStartingSession] = useState(false)

  async function load() {
    try {
      setError(null)
      const [p, s] = await Promise.all([
        api.getProfile(userId),
        api.getSession(userId),
      ])
      setProfile(p)
      setSession(s)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [userId])

  async function handleNewSession() {
    if (!confirm('Start a new session? The current session will be saved to your lifetime profile.')) return
    setStartingSession(true)
    try {
      await api.startSession(userId, displayName)
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setStartingSession(false)
    }
  }

  if (loading) {
    return (
      <div className="profile-panel" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div className="loading-ring" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="profile-panel">
        <div className="error-banner">{error}</div>
      </div>
    )
  }

  const initials = (profile?.display_name || displayName || '?')
    .split(/\s+/)
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()

  const sessionTraits = session?.session_traits ?? {}
  const lifetimeTraits = profile?.lifetime_traits ?? {}
  const divergence = session?.divergence ?? 0
  const hasSession = session?.active

  return (
    <div className="profile-panel">

      {/* Identity card */}
      <div className="card">
        <div className="profile-identity">
          <div className="profile-avatar">{initials}</div>
          <div>
            <div className="profile-name">{profile?.display_name || displayName}</div>
            <div className="profile-archetype">
              {profile?.archetype || 'archetype forming…'}
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-row">
        <div className="stat-chip">
          <span className="stat-value">{profile?.session_count ?? 0}</span>
          <span className="stat-label">Sessions</span>
        </div>
        <div className="stat-chip">
          <span className="stat-value">{profile?.total_interactions ?? 0}</span>
          <span className="stat-label">Messages</span>
        </div>
        <div className="stat-chip">
          <span className="stat-value">{session?.interaction_count ?? 0}</span>
          <span className="stat-label">This Run</span>
        </div>
      </div>

      {/* Current session traits */}
      <div className="card">
        <div className="card-title">Current Session</div>
        {hasSession ? (
          <>
            <div className="session-badge" style={{ marginBottom: 14 }}>
              <span className="session-badge-dot" />
              Session {session.session_id}
            </div>
            <div className="traits-list">
              {TRAIT_NAMES.map((t) => (
                <TraitBar key={t} trait={t} value={sessionTraits[t] ?? 0} />
              ))}
            </div>
          </>
        ) : (
          <p className="no-data">No active session — start chatting to begin one.</p>
        )}
      </div>

      {/* Divergence from lifetime */}
      {hasSession && (
        <div className="card">
          <div className="card-title">Session vs Lifetime Divergence</div>
          <div className="divergence-label">
            <span className="divergence-value" style={{ color: divergenceColor(divergence) }}>
              {(divergence * 100).toFixed(0)}%
            </span>{' '}
            {divergence < 0.15
              ? 'consistent with your history'
              : divergence < 0.35
              ? 'moderate shift detected'
              : 'significant persona divergence — playing differently this run'}
          </div>
          <div className="divergence-bar">
            <div
              className="divergence-fill"
              style={{
                width: `${divergence * 100}%`,
                backgroundColor: divergenceColor(divergence),
              }}
            />
          </div>
        </div>
      )}

      {/* Lifetime traits */}
      <div className="card">
        <div className="card-title">Lifetime Profile</div>
        {profile?.total_interactions > 0 ? (
          <div className="traits-list">
            {TRAIT_NAMES.map((t) => (
              <TraitBar key={t} trait={t} value={lifetimeTraits[t] ?? 0} />
            ))}
          </div>
        ) : (
          <p className="no-data">Not enough data yet — keep talking.</p>
        )}
      </div>

      {/* New session */}
      <button
        className="new-session-btn"
        onClick={handleNewSession}
        disabled={startingSession}
      >
        {startingSession ? 'Starting…' : '+ Start New Session / New Run'}
      </button>

    </div>
  )
}
