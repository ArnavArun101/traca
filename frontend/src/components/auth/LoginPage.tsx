import { useState } from 'react'
import { Activity, ArrowRight, Mail, Lock, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

function getApiBase(): string {
  const envUrl = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
  const base = envUrl && envUrl.length > 0
    ? envUrl
    : `${window.location.protocol}//${window.location.hostname}:8000`
  return base.replace(/\/$/, '')
}

interface LoginPageProps {
  onLogin: () => void
  onSwitchToRegister: () => void
}

export function LoginPage({ onLogin, onSwitchToRegister }: LoginPageProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await fetch(`${getApiBase()}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      const data = await res.json().catch(() => null)
      if (!res.ok) {
        throw new Error(data?.detail || 'Login failed')
      }
      if (data?.token) {
        localStorage.setItem('traca_token', data.token)
      }
      onLogin()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-lg">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2.5">
            <Activity className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold tracking-tight">traca</span>
          </div>
          <Button variant="outline" size="sm" onClick={onSwitchToRegister}>
            Create Account
          </Button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex flex-1 items-center justify-center pt-16 px-6">
        {/* Gradient orbs */}
        <div className="pointer-events-none absolute -top-40 left-1/2 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-primary/5 blur-3xl" />
        <div className="pointer-events-none absolute top-20 right-0 h-[400px] w-[400px] rounded-full bg-primary/3 blur-3xl" />

        <div className="relative w-full max-w-md">
          <div className="mx-auto mb-8 text-center">
            <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm text-primary">
              <Zap className="h-3.5 w-3.5" />
              Welcome Back
            </div>
            <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Sign in to <span className="text-primary">traca</span>
            </h1>
            <p className="mt-3 text-muted-foreground">
              Access your AI-powered trading dashboard
            </p>
          </div>

          <Card className="border-border/50 shadow-2xl shadow-primary/5">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg">Login</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {error ? (
                  <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                    {error}
                  </div>
                ) : null}
                <div className="space-y-2">
                  <label className="text-sm font-medium" htmlFor="email">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@example.com"
                      className="pl-10"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium" htmlFor="password">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="password"
                      type="password"
                      placeholder="••••••••"
                      className="pl-10"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      className="h-4 w-4 rounded border-border accent-primary"
                    />
                    <span className="text-muted-foreground">Remember me</span>
                  </label>
                  <button
                    type="button"
                    className="text-sm text-primary hover:underline"
                  >
                    Forgot password?
                  </button>
                </div>

                <Button type="submit" className="w-full text-base py-5" size="lg" disabled={loading}>
                  Sign In
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </form>

              <div className="mt-6 text-center text-sm text-muted-foreground">
                Don't have an account?{' '}
                <button
                  onClick={onSwitchToRegister}
                  className="font-medium text-primary hover:underline"
                >
                  Create one
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border/50 bg-card/30">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Activity className="h-4 w-4 text-primary" />
            <span className="font-medium text-foreground">traca</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Built with Deriv API, Mistral AI & React
          </p>
        </div>
      </footer>
    </div>
  )
}
