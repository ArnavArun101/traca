import { StrictMode, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { LandingPage } from './components/landing/LandingPage'
import { LoginPage } from './components/auth/LoginPage'
import { RegisterPage } from './components/auth/RegisterPage'

type Page = 'landing' | 'login' | 'register' | 'dashboard'

function Root() {
  const [page, setPage] = useState<Page>('landing')

  if (page === 'landing') {
    return <LandingPage onLaunch={() => setPage('login')} />
  }

  if (page === 'login') {
    return (
      <LoginPage
        onLogin={() => setPage('dashboard')}
        onSwitchToRegister={() => setPage('register')}
      />
    )
  }

  if (page === 'register') {
    return (
      <RegisterPage
        onRegister={() => setPage('login')}
        onSwitchToLogin={() => setPage('login')}
      />
    )
  }

  return <App />
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Root />
  </StrictMode>,
)
