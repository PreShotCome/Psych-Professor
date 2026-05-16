import { useState, useRef, useEffect, useCallback } from 'react'
import { api } from '../api'
import { traitChipColor } from './TraitBar'

const TRAIT_NAMES = [
  'moral', 'law', 'aggression', 'deception', 'empathy',
  'dominance', 'impulsivity', 'curiosity', 'paranoia', 'manipulation',
]

function getSignificantSignals(signals) {
  if (!signals) return []
  return TRAIT_NAMES
    .filter((t) => Math.abs(signals[t] ?? 0) >= 0.2)
    .sort((a, b) => Math.abs(signals[b]) - Math.abs(signals[a]))
    .slice(0, 4)
    .map((t) => ({ trait: t, value: signals[t] }))
}

function TraitFlash({ signals }) {
  const chips = getSignificantSignals(signals)
  if (!chips.length) return null
  return (
    <div className="trait-flash">
      {chips.map(({ trait, value }) => {
        const color = traitChipColor(trait, value)
        return (
          <span key={trait} className="trait-chip" style={{ color, borderColor: `${color}33` }}>
            {trait} {value >= 0 ? '+' : ''}{value.toFixed(2)}
          </span>
        )
      })}
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="msg-row npc">
      <span className="msg-sender">Professor</span>
      <div className="typing-indicator">
        <div className="typing-dot" />
        <div className="typing-dot" />
        <div className="typing-dot" />
      </div>
    </div>
  )
}

let _msgId = 0
const nextId = () => ++_msgId

export default function ChatView({ userId, displayName, psychState, onStateUpdate }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => { scrollToBottom() }, [messages, loading, scrollToBottom])

  async function sendMessage() {
    const text = input.trim()
    if (!text || loading) return

    setInput('')
    setError(null)
    setMessages((prev) => [...prev, { id: nextId(), role: 'user', content: text }])
    setLoading(true)

    try {
      const result = await api.chat(
        userId,
        displayName,
        text,
        psychState.profile,
        psychState.session,
      )
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: 'npc',
          content: result.response,
          signals: result.signals_this_turn,
        },
      ])
      // Persist updated profile + session to localStorage via parent
      onStateUpdate({ profile: result.profile, session: result.session })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="chat-view">
      {messages.length === 0 && !loading && (
        <div className="empty-chat">
          <svg className="empty-chat-icon" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none">
            <circle cx="50" cy="50" r="36" stroke="#7c3aed" strokeWidth="3" opacity="0.3"/>
            <ellipse cx="50" cy="50" rx="22" ry="14" stroke="#a78bfa" strokeWidth="2" opacity="0.4"/>
            <circle cx="50" cy="50" r="9" fill="#7c3aed" opacity="0.4"/>
          </svg>
          <p>The Professor awaits.<br />Every word you say is data.</p>
        </div>
      )}

      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`msg-row ${msg.role}`}>
            <span className="msg-sender">{msg.role === 'user' ? displayName : 'Professor'}</span>
            <div className="msg-bubble">{msg.content}</div>
            {msg.role === 'npc' && <TraitFlash signals={msg.signals} />}
          </div>
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="chat-input-row">
        <textarea
          ref={inputRef}
          className="chat-input"
          rows={1}
          placeholder="Speak your mind…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          className="send-btn"
          onClick={sendMessage}
          disabled={!input.trim() || loading}
          aria-label="Send"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
    </div>
  )
}
