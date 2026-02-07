import { X, Brain, Flame, Trophy, AlertTriangle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useBehavioralStore } from '@/stores/behavioralStore'
import { cn } from '@/lib/utils'

export function BehavioralPanel() {
  const report = useBehavioralStore((s) => s.report)
  const nudges = useBehavioralStore((s) => s.nudges)
  const dismissNudge = useBehavioralStore((s) => s.dismissNudge)

  if (!report && nudges.length === 0) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12 text-muted-foreground text-sm">
          <div className="text-center space-y-1">
            <Brain className="h-8 w-8 mx-auto opacity-40" />
            <p>No behavioral data yet</p>
            <p className="text-xs">Trade activity will be analyzed here</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const score = report?.metrics.discipline_score.score ?? 0
  const scorePercent = Math.round(score * 100)
  const sentiment = report?.sentiment ?? 0
  const streakType = report?.metrics.streaks.type ?? 'unknown'
  const streakCount = report?.metrics.streaks.current_streak ?? 0
  const ruleBreaks = report?.metrics.discipline_score.rule_breaks ?? {}

  const urgencyColors: Record<string, string> = {
    low: 'border-blue-500/30 bg-blue-500/5',
    medium: 'border-yellow-500/30 bg-yellow-500/5',
    high: 'border-orange-500/30 bg-orange-500/5',
    critical: 'border-red-500/30 bg-red-500/5',
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <Brain className="h-4 w-4" />
          Behavioral Analysis
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {report && (
          <>
            <div className="grid grid-cols-3 gap-3 text-center">
              <div>
                <div className="relative mx-auto h-16 w-16">
                  <svg className="h-16 w-16 -rotate-90" viewBox="0 0 36 36">
                    <path
                      className="text-muted"
                      d="M18 2.0845a15.9155 15.9155 0 0 1 0 31.831 15.9155 15.9155 0 0 1 0-31.831"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                    />
                    <path
                      className={cn(
                        scorePercent >= 75 ? 'text-green-500' : scorePercent >= 50 ? 'text-yellow-500' : 'text-red-500'
                      )}
                      d="M18 2.0845a15.9155 15.9155 0 0 1 0 31.831 15.9155 15.9155 0 0 1 0-31.831"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeDasharray={`${scorePercent}, 100`}
                    />
                  </svg>
                  <span className="absolute inset-0 flex items-center justify-center text-sm font-bold">
                    {scorePercent}
                  </span>
                </div>
                <div className="text-xs text-muted-foreground mt-1">Discipline</div>
              </div>

              <div className="flex flex-col items-center justify-center">
                <div className={cn(
                  'text-2xl font-bold',
                  sentiment > 0 ? 'text-green-500' : sentiment < 0 ? 'text-red-500' : 'text-muted-foreground'
                )}>
                  {sentiment > 0 ? '+' : ''}{sentiment.toFixed(2)}
                </div>
                <div className="text-xs text-muted-foreground">Sentiment</div>
              </div>

              <div className="flex flex-col items-center justify-center">
                <div className="flex items-center gap-1">
                  {streakType === 'win' ? (
                    <Trophy className="h-4 w-4 text-green-500" />
                  ) : streakType === 'loss' ? (
                    <Flame className="h-4 w-4 text-red-500" />
                  ) : null}
                  <span className="text-2xl font-bold">{streakCount}</span>
                </div>
                <div className="text-xs text-muted-foreground">
                  {streakType === 'win' ? 'Win' : streakType === 'loss' ? 'Loss' : ''} Streak
                </div>
              </div>
            </div>

            {Object.entries(ruleBreaks).some(([, v]) => v > 0) && (
              <div className="flex flex-wrap gap-1.5">
                {Object.entries(ruleBreaks).map(([rule, count]) =>
                  count > 0 ? (
                    <Badge key={rule} variant="destructive" className="text-xs">
                      <AlertTriangle className="h-3 w-3 mr-1" />
                      {rule.replace(/_/g, ' ')}: {count}
                    </Badge>
                  ) : null
                )}
              </div>
            )}
          </>
        )}

        {nudges.length > 0 && (
          <div className="space-y-2">
            <div className="text-xs font-medium text-muted-foreground">Active Nudges</div>
            {nudges.map((nudge) => (
              <div
                key={nudge.id}
                className={cn(
                  'rounded-md border p-2.5 text-sm',
                  urgencyColors[nudge.urgency] ?? 'border-border'
                )}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-medium text-xs">{nudge.title}</div>
                    <div className="text-xs text-muted-foreground mt-0.5">{nudge.message}</div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-5 w-5 shrink-0"
                    onClick={() => dismissNudge(nudge.id)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
