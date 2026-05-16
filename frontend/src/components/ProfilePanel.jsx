import { useState } from 'react'
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

export default function ProfilePanel({ userId, displayName, psychState, onStateUpdate }) {
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState(null)

  const { profile, session } = psychState
  const lifetimeTraits = profile?.lifetime_traits ?? {}
  const sessionTraits = session?.traits ?? {}
  const hasSession = Boolean(session)

  // Compute divergence locally (mean abs diff / 2 per trait)
  const divergence = hasSession
    ? TRAIT_NAMES.reduce((sum, t) => {
        const lt = lifetimeTraits[t] ?? 0
        const st = sessionTraits[t] ?? 0
        return sum + Math.abs(lt - st) / 2
      }, 0) / TRAIT_NAMES.length
    : 0

  async function handleNewSession() {
    if (!confirm('Start a new session? Current session will be saved to your lifetime profile.')) return
    setStarting(true)
    setError(null)
    try {
      const result = await api.startSession(userId, displayName, profile)
      onStateUpdate({ profile: result.profile, session: result.session })
    } catch (err) {
      setError(err.message)
    } finally {
      setStarting(false)
    }
  }

  const initials = (profile?.display_name || displayName || '?')
    .split(/\s+/).map((w) => w[0]).join('').slice(0, 2).toUpperCase()

  return (
    <div className="profile-panel">

      {/* Identity */}
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

      {/* Divergence */}
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
              style={{ width: `${divergence * 100}%`, backgroundColor: divergenceColor(divergence) }}
            />
          </div>
        </div>
      )}

      {/* Lifetime traits */}
      <div className="card">
        <div className="card-title">Lifetime Profile</div>
        {(profile?.total_interactions ?? 0) > 0 ? (
          <div className="traits-list">
            {TRAIT_NAMES.map((t) => (
              <TraitBar key={t} trait={t} value={lifetimeTraits[t] ?? 0} />
            ))}
          </div>
        ) : (
          <p className="no-data">Not enough data yet — keep talking.</p>
        )}
      </div>

      {error && <div className="error-banner">{error}</div>}

      <button className="new-session-btn" onClick={handleNewSession} disabled={starting}>
        {starting ? 'Starting…' : '+ Start New Session / New Run'}
      </button>

      <button
        className="new-session-btn"
        style={{ borderColor: 'rgba(239,68,68,0.4)', color: '#f87171', marginTop: 4 }}
        onClick={() => {
          if (!confirm('Reset everything? Your entire profile and history will be erased.')) return
          localStorage.clear()
          window.location.reload()
        }}
      >
        ✕ Reset Profile
      </button>

    </div>
  )
}
