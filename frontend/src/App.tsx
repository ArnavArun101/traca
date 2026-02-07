import { useEffect } from 'react'
import { useWebSocket } from '@/hooks/useWebSocket'
import { Header } from '@/components/layout/Header'
import { PriceCards } from '@/components/dashboard/PriceCards'
import { CandlestickChart } from '@/components/dashboard/CandlestickChart'
import { IndicatorPanel } from '@/components/dashboard/IndicatorPanel'
import { AlertsPanel } from '@/components/dashboard/AlertsPanel'
import { BehavioralPanel } from '@/components/dashboard/BehavioralPanel'
import { ChatPanel } from '@/components/chat/ChatPanel'
import { SocialPanel } from '@/components/social/SocialPanel'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'

export default function App() {
  const { connected, sendMessage } = useWebSocket()

  useEffect(() => {
    if (connected) {
      sendMessage({ type: 'list_assets' })
      sendMessage({ type: 'get_prices' })
      sendMessage({ type: 'list_alerts' })
    }
  }, [connected, sendMessage])

  return (
    <div className="flex h-screen flex-col">
      <Header connected={connected} sendMessage={sendMessage} />

      <div className="flex flex-1 overflow-hidden flex-col lg:flex-row">
        {/* Dashboard - Left side */}
        <div className="flex-[3] overflow-y-auto border-r p-4 space-y-4 min-w-0">
          <PriceCards sendMessage={sendMessage} />
          <CandlestickChart />

          <Tabs defaultValue="indicators">
            <TabsList>
              <TabsTrigger value="indicators">Indicators</TabsTrigger>
              <TabsTrigger value="alerts">Alerts</TabsTrigger>
              <TabsTrigger value="behavioral">Behavioral</TabsTrigger>
              <TabsTrigger value="social">Social</TabsTrigger>
            </TabsList>
            <TabsContent value="indicators">
              <IndicatorPanel />
            </TabsContent>
            <TabsContent value="alerts">
              <AlertsPanel sendMessage={sendMessage} />
            </TabsContent>
            <TabsContent value="behavioral">
              <BehavioralPanel />
            </TabsContent>
            <TabsContent value="social">
              <SocialPanel sendMessage={sendMessage} />
            </TabsContent>
          </Tabs>
        </div>

        {/* Chat - Right side */}
        <div className="flex-[2] min-w-0 flex flex-col min-h-[300px] lg:min-h-0">
          <ChatPanel sendMessage={sendMessage} />
        </div>
      </div>
    </div>
  )
}
