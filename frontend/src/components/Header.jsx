const EyeIcon = () => (
  <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none">
    <circle cx="50" cy="50" r="36" stroke="#7c3aed" strokeWidth="3" opacity="0.6"/>
    <ellipse cx="50" cy="50" rx="22" ry="14" stroke="#a78bfa" strokeWidth="2.5"/>
    <circle cx="50" cy="50" r="9" fill="#7c3aed"/>
    <circle cx="50" cy="50" r="4" fill="#080813"/>
    <circle cx="53" cy="47" r="2" fill="#e0d0ff" opacity="0.7"/>
    <line x1="14" y1="50" x2="28" y2="50" stroke="#06b6d4" strokeWidth="1.5" opacity="0.5"/>
    <line x1="72" y1="50" x2="86" y2="50" stroke="#06b6d4" strokeWidth="1.5" opacity="0.5"/>
  </svg>
)

const ChatIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
  </svg>
)

const ProfileIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
)

const InterviewIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
    <line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>
)

export default function Header({ displayName, view, onViewChange }) {
  return (
    <header className="header">
      <div className="header-logo">
        <EyeIcon />
        <div>
          <div className="header-title">Prof.</div>
          <div className="header-subtitle">{displayName}</div>
        </div>
      </div>

      <div className="header-tabs">
        <button className={`tab-btn ${view === 'chat' ? 'active' : ''}`} onClick={() => onViewChange('chat')} title="Chat">
          <ChatIcon />
        </button>
        <button className={`tab-btn ${view === 'interview' ? 'active' : ''}`} onClick={() => onViewChange('interview')} title="Interview">
          <InterviewIcon />
        </button>
        <button className={`tab-btn ${view === 'profile' ? 'active' : ''}`} onClick={() => onViewChange('profile')} title="Profile">
          <ProfileIcon />
        </button>
      </div>

      <div className="header-actions" style={{ width: 44 }} />
    </header>
  )
}
