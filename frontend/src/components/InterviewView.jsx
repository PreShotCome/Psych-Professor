import { useState } from 'react'
import { api } from '../api'
import TraitBar, { traitChipColor } from './TraitBar'

const TRAIT_NAMES = [
  'moral', 'law', 'aggression', 'deception', 'empathy',
  'dominance', 'impulsivity', 'curiosity', 'paranoia', 'manipulation',
]

const PHASE_COLORS = {
  1: '#06b6d4',
  2: '#a78bfa',
  3: '#22c55e',
  4: '#f59e0b',
  5: '#ef4444',
}

function SignalFlash({ signals }) {
  if (!signals) return null
  const chips = TRAIT_NAMES
    .filter(t => Math.abs(signals[t] ?? 0) >= 0.15)
    .sort((a, b) => Math.abs(signals[b]) - Math.abs(signals[a]))
    .slice(0, 5)
  if (!chips.length) return <p className="no-data" style={{ fontSize: '0.78rem' }}>No strong signals detected in this answer.</p>
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 10 }}>
      {chips.map(t => {
        const v = signals[t]
        const color = traitChipColor(t, v)
        return (
          <span key={t} className="trait-chip" style={{ color, borderColor: `${color}40`, fontSize: '0.75rem', padding: '3px 10px' }}>
            {t} {v >= 0 ? '+' : ''}{v.toFixed(2)}
          </span>
        )
      })}
    </div>
  )
}

function ProfileSummary({ psychState }) {
  const profile = psychState?.profile
  const lt = profile?.lifetime_traits ?? {}
  const dominant = TRAIT_NAMES
    .filter(t => Math.abs(lt[t] ?? 0) >= 0.2)
    .sort((a, b) => Math.abs(lt[b]) - Math.abs(lt[a]))

  return (
    <div className="profile-panel" style={{ justifyContent: 'flex-start' }}>
      <div className="card" style={{ textAlign: 'center', padding: '24px 16px' }}>
        <div style={{ fontSize: '2rem', marginBottom: 8 }}>🧠</div>
        <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-light)', marginBottom: 4 }}>
          Profile Complete
        </div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          {profile?.archetype ? `Archetype: ${profile.archetype}` : 'Archetype forming — play more to refine it'}
        </div>
      </div>

      <div className="stats-row">
        <div className="stat-chip">
          <span className="stat-value">{profile?.total_interactions ?? 0}</span>
          <span className="stat-label">Answers</span>
        </div>
        <div className="stat-chip">
          <span className="stat-value">{dominant.length}</span>
          <span className="stat-label">Traits mapped</span>
        </div>
      </div>

      <div className="card">
        <div className="card-title">Your Psychological Profile</div>
        {dominant.length > 0 ? (
          <div className="traits-list">
            {TRAIT_NAMES.map(t => (
              <TraitBar key={t} trait={t} value={lt[t] ?? 0} />
            ))}
          </div>
        ) : (
          <p className="no-data">Answers were too brief to map clearly — try the chat for deeper profiling.</p>
        )}
      </div>

      <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textAlign: 'center', padding: '0 16px' }}>
        Switch to Chat to keep talking — the profile continues building with every message.
      </p>
    </div>
  )
}

export default function InterviewView({ userId, displayName, psychState, onStateUpdate, questions: questionsProp }) {
  const [currentQ, setCurrentQ] = useState(0)
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [lastSignals, setLastSignals] = useState(null)
  const [error, setError] = useState(null)
  const [done, setDone] = useState(false)

  const questions = questionsProp?.length ? questionsProp : FALLBACK_QUESTIONS

  const q = questions[currentQ]
  const total = questions.length
  const progress = ((currentQ) / total) * 100

  async function handleSubmit() {
    const text = answer.trim()
    if (!text || loading) return
    setLoading(true)
    setError(null)
    setLastSignals(null)

    const formatted = `[Psych Interview — Question: "${q.text}"]\nAnswer: ${text}`

    try {
      const result = await api.chat(
        userId, displayName, formatted,
        psychState.profile, psychState.session, [],
      )
      setLastSignals(result.signals_this_turn)
      onStateUpdate({ profile: result.profile, session: result.session })

      if (currentQ + 1 >= total) {
        setDone(true)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function next() {
    setAnswer('')
    setLastSignals(null)
    setCurrentQ(q => q + 1)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && e.metaKey) handleSubmit()
  }

  if (done) return <ProfileSummary psychState={psychState} />

  const phaseColor = PHASE_COLORS[q.phase] ?? 'var(--accent)'

  return (
    <div className="interview-view">

      {/* Progress */}
      <div className="interview-header">
        <div className="interview-progress-track">
          <div className="interview-progress-fill" style={{ width: `${progress}%`, backgroundColor: phaseColor }} />
        </div>
        <div className="interview-meta">
          <span style={{ color: phaseColor, fontWeight: 700 }}>Phase {q.phase}: {q.phase_name}</span>
          <span style={{ color: 'var(--text-muted)' }}>{currentQ + 1} / {total}</span>
        </div>
      </div>

      {/* Question */}
      <div className="interview-body">
        <div className="interview-question">{q.text}</div>

        {/* Signal feedback from last answer */}
        {lastSignals && (
          <div className="interview-signals">
            <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', marginBottom: 6 }}>
              Detected signals
            </div>
            <SignalFlash signals={lastSignals} />
          </div>
        )}

        <textarea
          className="interview-answer"
          placeholder="Answer honestly — the more specific, the better…"
          value={answer}
          onChange={e => setAnswer(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          rows={4}
          autoFocus
        />

        {error && <div className="error-banner">{error}</div>}

        <div className="interview-actions">
          {lastSignals ? (
            <button className="setup-btn" onClick={next}>
              Next Question →
            </button>
          ) : (
            <button className="setup-btn" onClick={handleSubmit} disabled={!answer.trim() || loading}>
              {loading ? 'Analyzing…' : 'Submit Answer'}
            </button>
          )}
          <button
            className="new-session-btn"
            style={{ marginTop: 0, fontSize: '0.8rem', padding: '10px' }}
            onClick={() => { setAnswer(''); setLastSignals(null); next() }}
            disabled={loading}
          >
            Skip
          </button>
        </div>
      </div>

    </div>
  )
}

// Inline fallback — replaced by the fetched list from /api/interview-questions
const FALLBACK_QUESTIONS = [
  { phase: 1, phase_name: 'Foundations', trait: 'moral', text: "If you found a wallet with $500 cash and the owner's ID, what would you do?" },
  { phase: 1, phase_name: 'Foundations', trait: 'empathy', text: "When you see a stranger visibly upset in public, what's your instinct?" },
]
