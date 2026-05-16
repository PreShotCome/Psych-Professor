import { useState, useEffect } from 'react'
import Setup from './components/Setup'
import Header from './components/Header'
import ChatView from './components/ChatView'
import ProfilePanel from './components/ProfilePanel'
import InterviewView from './components/InterviewView'

function loadPsychState() {
  try {
    const raw = localStorage.getItem('psychState')
    return raw ? JSON.parse(raw) : { profile: null, session: null }
  } catch {
    return { profile: null, session: null }
  }
}

function savePsychState(state) {
  localStorage.setItem('psychState', JSON.stringify(state))
}

export default function App() {
  const [userId] = useState(() => localStorage.getItem('userId') || '')
  const [displayName] = useState(() => localStorage.getItem('displayName') || '')
  const [view, setView] = useState('chat')
  const [psychState, setPsychState] = useState(loadPsychState)
  const [interviewQuestions, setInterviewQuestions] = useState([])

  useEffect(() => {
    fetch('/api/interview-questions')
      .then(r => r.json())
      .then(d => {
        setInterviewQuestions(d.questions ?? [])
        window.__INTERVIEW_QUESTIONS__ = d.questions ?? []
      })
      .catch(() => {})
  }, [])

  function updateState(newState) {
    savePsychState(newState)
    setPsychState(newState)
  }

  function handleSetupComplete() {
    window.location.reload()
  }

  if (!userId) {
    return <Setup onComplete={handleSetupComplete} />
  }

  return (
    <div className="app">
      <Header displayName={displayName} view={view} onViewChange={setView} />
      <main className="app-main">
        {view === 'chat' && (
          <ChatView userId={userId} displayName={displayName} psychState={psychState} onStateUpdate={updateState} />
        )}
        {view === 'interview' && (
          <InterviewView userId={userId} displayName={displayName} psychState={psychState} onStateUpdate={updateState} questions={interviewQuestions} />
        )}
        {view === 'profile' && (
          <ProfilePanel userId={userId} displayName={displayName} psychState={psychState} onStateUpdate={updateState} />
        )}
      </main>
    </div>
  )
}
