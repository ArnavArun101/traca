import { StrictMode, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { LandingPage } from './components/landing/LandingPage'

function Root() {
  const [launched, setLaunched] = useState(false)

  if (!launched) {
    return <LandingPage onLaunch={() => setLaunched(true)} />
  }

  return <App />
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Root />
  </StrictMode>,
)
