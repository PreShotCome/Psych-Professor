import { useState } from 'react'
import Setup from './components/Setup'
import Header from './components/Header'
import ChatView from './components/ChatView'
import ProfilePanel from './components/ProfilePanel'

export default function App() {
  const [userId] = useState(() => localStorage.getItem('userId') || '')
  const [displayName] = useState(() => localStorage.getItem('displayName') || '')
  const [view, setView] = useState('chat')
  const [profileKey, setProfileKey] = useState(0)

  function handleSetupComplete() {
    // Force re-render by reloading — clean way to reinitialize all state
    window.location.reload()
  }

  if (!userId) {
    return <Setup onComplete={handleSetupComplete} />
  }

  return (
    <div className="app">
      <Header
        displayName={displayName}
        view={view}
        onViewChange={setView}
        userId={userId}
      />
      <main className="app-main">
        {view === 'chat' ? (
          <ChatView
            userId={userId}
            displayName={displayName}
            onMessageSent={() => setProfileKey((k) => k + 1)}
          />
        ) : (
          <ProfilePanel
            key={profileKey}
            userId={userId}
            displayName={displayName}
          />
        )}
      </main>
    </div>
  )
}
