import { useState } from 'react'
import { Activity, ArrowRight, Mail, Lock, User, Zap } from 'lucide-react'
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

interface RegisterPageProps {
  onRegister: () => void
  onSwitchToLogin: () => void
}

export function RegisterPage({ onRegister, onSwitchToLogin }: RegisterPageProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    setLoading(true)
    try {
      const res = await fetch(`${getApiBase()}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          email,
          password,
          confirm_password: confirmPassword,
        }),
      })
      const data = await res.json().catch(() => null)
      if (!res.ok) {
        throw new Error(data?.detail || 'Registration failed')
      }
      if (data?.token) {
        localStorage.setItem('traca_token', data.token)
      }
      onRegister()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
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
          <Button variant="outline" size="sm" onClick={onSwitchToLogin}>
            Sign In
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
              Get Started
            </div>
            <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Create your <span className="text-primary">traca</span> account
            </h1>
            <p className="mt-3 text-muted-foreground">
              Start trading smarter with AI-powered behavioral coaching
            </p>
          </div>

          <Card className="border-border/50 shadow-2xl shadow-primary/5">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg">Register</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {error ? (
                  <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                    {error}
                  </div>
                ) : null}
                <div className="space-y-2">
                  <label className="text-sm font-medium" htmlFor="name">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="name"
                      type="text"
                      placeholder="John Doe"
                      className="pl-10"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium" htmlFor="register-email">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="register-email"
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
                  <label className="text-sm font-medium" htmlFor="register-password">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="register-password"
                      type="password"
                      placeholder="••••••••"
                      className="pl-10"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium" htmlFor="confirm-password">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="confirm-password"
                      type="password"
                      placeholder="••••••••"
                      className="pl-10"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />
                  </div>
                </div>

                <label className="flex items-start gap-2 text-sm">
                  <input
                    type="checkbox"
                    className="mt-0.5 h-4 w-4 rounded border-border accent-primary"
                    required
                  />
                  <span className="text-muted-foreground">
                    I agree to the{' '}
                    <button type="button" className="text-primary hover:underline">
                      Terms of Service
                    </button>{' '}
                    and{' '}
                    <button type="button" className="text-primary hover:underline">
                      Privacy Policy
                    </button>
                  </span>
                </label>

                <Button type="submit" className="w-full text-base py-5" size="lg" disabled={loading}>
                  Create Account
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </form>

              <div className="mt-6 text-center text-sm text-muted-foreground">
                Already have an account?{' '}
                <button
                  onClick={onSwitchToLogin}
                  className="font-medium text-primary hover:underline"
                >
                  Sign in
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
