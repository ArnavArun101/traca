import {
  Activity,
  BarChart3,
  BrainCircuit,
  MessageSquare,
  Bell,
  TrendingUp,
  Share2,
  ArrowRight,
  ChevronRight,
  Shield,
  Zap,
  LineChart,
} from 'lucide-react'
import { Button } from '@/components/ui/button'

interface LandingPageProps {
  onLaunch: () => void
}

const features = [
  {
    icon: TrendingUp,
    title: 'Real-Time Market Data',
    description:
      'Stream live prices from Deriv across synthetic indices, forex, and crypto. Watch candlestick charts update tick-by-tick.',
  },
  {
    icon: BrainCircuit,
    title: 'AI Trading Coach',
    description:
      'Chat with a Mistral-powered assistant that understands markets. Ask questions, get explanations, and receive actionable insights.',
  },
  {
    icon: Shield,
    title: 'Behavioral Analysis',
    description:
      'Track your trading discipline with real-time scoring. Get nudges when emotional patterns threaten your strategy.',
  },
  {
    icon: BarChart3,
    title: 'Technical Indicators',
    description:
      'RSI, MACD, and moving averages calculated on demand. Visual charts with clear buy/sell signal badges.',
  },
  {
    icon: Bell,
    title: 'Smart Price Alerts',
    description:
      'Set above/below price targets on any instrument. Get instant notifications the moment your levels are hit.',
  },
  {
    icon: Share2,
    title: 'Social Content Studio',
    description:
      'Generate trading insights for LinkedIn or X with distinct AI personas. One click from analysis to post.',
  },
]

const stats = [
  { value: '20+', label: 'Instruments', sublabel: 'Synthetic, Forex & Crypto' },
  { value: '<50ms', label: 'Latency', sublabel: 'Real-time WebSocket feed' },
  { value: '6', label: 'AI Services', sublabel: 'Working in parallel' },
  { value: '24/7', label: 'Monitoring', sublabel: 'Always-on behavioral coach' },
]

const steps = [
  {
    step: '01',
    title: 'Connect & Subscribe',
    description:
      'Pick your asset group and start streaming live prices. Your dashboard lights up with real-time data.',
  },
  {
    step: '02',
    title: 'Analyze & Trade',
    description:
      'Use charts, indicators, and AI chat to make informed decisions. Set alerts so you never miss a move.',
  },
  {
    step: '03',
    title: 'Review & Improve',
    description:
      'Get behavioral reports on your trading patterns. Let the AI coach help you build discipline over time.',
  },
]

export function LandingPage({ onLaunch }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-lg">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2.5">
            <Activity className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold tracking-tight">traca</span>
          </div>
          <Button onClick={onLaunch} size="sm">
            Launch Dashboard
            <ArrowRight className="ml-1.5 h-4 w-4" />
          </Button>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden pt-16">
        {/* Gradient orbs */}
        <div className="pointer-events-none absolute -top-40 left-1/2 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-primary/5 blur-3xl" />
        <div className="pointer-events-none absolute top-20 right-0 h-[400px] w-[400px] rounded-full bg-primary/3 blur-3xl" />

        <div className="relative mx-auto max-w-6xl px-6 pb-24 pt-28 text-center lg:pb-32 lg:pt-36">
          <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm text-primary">
            <Zap className="h-3.5 w-3.5" />
            AI-Powered Trading Intelligence
          </div>

          <h1 className="mx-auto max-w-4xl text-4xl font-bold leading-tight tracking-tight sm:text-5xl lg:text-6xl">
            Trade Smarter with{' '}
            <span className="text-primary">Behavioral AI</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed">
            traca combines real-time market data, technical analysis, and AI-driven
            behavioral coaching to help you make disciplined trading decisions —
            not emotional ones.
          </p>

          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button onClick={onLaunch} size="lg" className="text-base px-8 py-6">
              Open Dashboard
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button variant="outline" size="lg" className="text-base px-8 py-6" onClick={() => {
              document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
            }}>
              See Features
              <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          </div>

          {/* Dashboard preview */}
          <div className="mx-auto mt-16 max-w-5xl overflow-hidden rounded-xl border border-border/50 bg-card shadow-2xl shadow-primary/5">
            <div className="flex items-center gap-2 border-b border-border/50 bg-secondary/30 px-4 py-3">
              <div className="h-3 w-3 rounded-full bg-destructive/60" />
              <div className="h-3 w-3 rounded-full bg-yellow-500/60" />
              <div className="h-3 w-3 rounded-full bg-primary/60" />
              <span className="ml-3 text-xs text-muted-foreground">traca — dashboard</span>
            </div>
            <div className="grid grid-cols-3 gap-3 p-4">
              {/* Simulated price cards */}
              {['R_100', 'frxEURUSD', 'cryBTCUSD'].map((sym) => (
                <div key={sym} className="rounded-lg border border-border/50 bg-secondary/20 p-3">
                  <div className="text-xs text-muted-foreground">{sym}</div>
                  <div className="mt-1 text-lg font-bold text-primary">
                    {sym === 'R_100' ? '1,247.83' : sym === 'frxEURUSD' ? '1.0892' : '67,432.10'}
                  </div>
                </div>
              ))}
              {/* Simulated chart area */}
              <div className="col-span-2 flex h-40 items-end gap-[2px] rounded-lg border border-border/50 bg-secondary/10 p-4">
                {Array.from({ length: 40 }, (_, i) => {
                  const h = 20 + Math.sin(i * 0.3) * 15 + Math.random() * 30
                  const up = Math.random() > 0.45
                  return (
                    <div
                      key={i}
                      className="flex-1 rounded-sm"
                      style={{
                        height: `${h}%`,
                        backgroundColor: up
                          ? 'hsl(197 100% 39% / 0.6)'
                          : 'hsl(0 84% 60% / 0.5)',
                      }}
                    />
                  )
                })}
              </div>
              {/* Simulated chat */}
              <div className="flex flex-col justify-between rounded-lg border border-border/50 bg-secondary/10 p-3">
                <div className="space-y-2">
                  <div className="rounded-md bg-primary/10 px-2 py-1 text-xs text-primary">
                    RSI is at 28 — oversold
                  </div>
                  <div className="rounded-md bg-secondary px-2 py-1 text-xs text-muted-foreground">
                    What does this mean?
                  </div>
                </div>
                <div className="mt-2 h-6 rounded-md border border-border/50 bg-background/50" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="border-t border-border/50 bg-card/30">
        <div className="mx-auto max-w-6xl px-6 py-24 lg:py-32">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Everything You Need to Trade with Confidence
            </h2>
            <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
              Six integrated tools working together in a single real-time dashboard.
              No tab switching. No context loss.
            </p>
          </div>

          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => (
              <div
                key={f.title}
                className="group rounded-xl border border-border/50 bg-card p-6 transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
              >
                <div className="mb-4 inline-flex rounded-lg bg-primary/10 p-3">
                  <f.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-lg font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  {f.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-t border-border/50">
        <div className="mx-auto max-w-6xl px-6 py-20 lg:py-24">
          <div className="grid grid-cols-2 gap-8 lg:grid-cols-4">
            {stats.map((s) => (
              <div key={s.label} className="text-center">
                <div className="text-4xl font-bold text-primary lg:text-5xl">
                  {s.value}
                </div>
                <div className="mt-2 text-sm font-medium">{s.label}</div>
                <div className="mt-1 text-xs text-muted-foreground">{s.sublabel}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="border-t border-border/50 bg-card/30">
        <div className="mx-auto max-w-6xl px-6 py-24 lg:py-32">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              How It Works
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-muted-foreground">
              From connection to continuous improvement in three simple steps.
            </p>
          </div>

          <div className="mt-16 grid gap-8 lg:grid-cols-3">
            {steps.map((s) => (
              <div key={s.step} className="relative rounded-xl border border-border/50 bg-card p-8">
                <span className="text-5xl font-bold text-primary/15">{s.step}</span>
                <h3 className="mt-2 text-xl font-semibold">{s.title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                  {s.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Chat preview */}
      <section className="border-t border-border/50">
        <div className="mx-auto max-w-6xl px-6 py-24 lg:py-32">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            <div>
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Your AI Trading Companion
              </h2>
              <p className="mt-4 text-muted-foreground leading-relaxed">
                Ask anything about the markets. Get plain-language explanations of
                complex indicators. Receive behavioral nudges when your trading
                patterns drift from your strategy.
              </p>
              <ul className="mt-6 space-y-3">
                {[
                  'Natural language market explanations',
                  'Real-time behavioral nudges',
                  'News summaries on demand',
                  'Social content generation',
                ].map((item) => (
                  <li key={item} className="flex items-center gap-3 text-sm">
                    <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10">
                      <LineChart className="h-3 w-3 text-primary" />
                    </div>
                    {item}
                  </li>
                ))}
              </ul>
              <Button onClick={onLaunch} className="mt-8" size="lg">
                Try It Now
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>

            {/* Chat mockup */}
            <div className="rounded-xl border border-border/50 bg-card p-1">
              <div className="rounded-lg bg-secondary/20 p-4 space-y-3">
                <div className="flex justify-end">
                  <div className="rounded-lg bg-primary/20 px-3 py-2 text-sm max-w-[80%]">
                    Explain what's happening with EUR/USD right now
                  </div>
                </div>
                <div className="flex justify-start">
                  <div className="rounded-lg bg-secondary px-3 py-2 text-sm max-w-[80%] text-muted-foreground">
                    EUR/USD is currently trading at 1.0892, showing a mild bearish
                    bias. RSI at 42 suggests neutral momentum, while MACD is
                    approaching a potential bullish crossover. Key support at 1.0850.
                  </div>
                </div>
                <div className="flex justify-end">
                  <div className="rounded-lg bg-primary/20 px-3 py-2 text-sm max-w-[80%]">
                    Should I set an alert at 1.0850?
                  </div>
                </div>
                <div className="flex justify-start">
                  <div className="rounded-lg bg-secondary px-3 py-2 text-sm max-w-[80%] text-muted-foreground">
                    That's a solid support level. I'd recommend setting a "below
                    1.0850" alert so you're notified if it breaks. Want me to create
                    that alert for you?
                  </div>
                </div>
                <div className="flex items-center gap-2 pt-1">
                  <div className="flex-1 rounded-md border border-border/50 bg-background/50 px-3 py-2 text-xs text-muted-foreground">
                    Ask about any market...
                  </div>
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary">
                    <MessageSquare className="h-4 w-4 text-primary-foreground" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="border-t border-border/50">
        <div className="mx-auto max-w-6xl px-6 py-24 text-center lg:py-32">
          <div className="mx-auto max-w-2xl rounded-2xl border border-primary/20 bg-primary/5 px-8 py-16">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Ready to Trade Smarter?
            </h2>
            <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
              Stop letting emotions drive your trades. Open the dashboard and let
              AI-powered behavioral coaching guide your decisions.
            </p>
            <Button onClick={onLaunch} size="lg" className="mt-8 text-base px-10 py-6">
              Launch Dashboard
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 bg-card/30">
        <div className="mx-auto flex max-w-6xl flex-col items-center px-6 py-6">
          <div className="flex w-full items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Activity className="h-4 w-4 text-primary" />
              <span className="font-medium text-foreground">traca</span>
            </div>
            <p className="text-xs text-muted-foreground">
              Built with Deriv API, Mistral AI & React
            </p>
          </div>

          {/* Easter Egg */}
          <div className="mt-4 opacity-30 hover:opacity-100 transition-opacity duration-500">
            <a
              href="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[11px] text-muted-foreground/60 hover:text-primary transition-colors"
            >
              Special thanks to Deriv & lablab for organizing this hackathon ✨
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
