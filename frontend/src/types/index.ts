// ── Outgoing messages (frontend → backend) ──

export interface SubscribeMsg {
  type: 'subscribe'
  symbol: string
}

export interface SubscribeGroupMsg {
  type: 'subscribe_group'
  group: 'synthetic' | 'forex' | 'crypto'
}

export interface ListAssetsMsg {
  type: 'list_assets'
}

export interface GetPricesMsg {
  type: 'get_prices'
}

export interface ChatMsg {
  type: 'chat'
  message: string
}

export interface AnalyzeBehaviorMsg {
  type: 'analyze_behavior'
  trades: TradeData[]
}

export interface GenerateSocialMsg {
  type: 'generate_social'
  topic: string
  platform: 'linkedin' | 'x'
}

export interface TradeHistoryMsg {
  type: 'trade_history'
  limit: number
}

export interface CandlesHistoryMsg {
  type: 'candles_history'
  symbol: string
  limit: number
}

export interface TradeEventMsg {
  type: 'trade_event'
  trade: TradeData
  recent_trades?: TradeData[]
}

export interface IndicatorsMsg {
  type: 'indicators'
  symbol: string
  limit: number
}

export interface CreateAlertMsg {
  type: 'create_alert'
  symbol: string
  target_price: number
  direction: 'above' | 'below'
}

export interface ListAlertsMsg {
  type: 'list_alerts'
}

export interface CancelAlertMsg {
  type: 'cancel_alert'
  alert_id: number
}

export interface FetchHistoryMsg {
  type: 'fetch_history'
  symbol: string
  limit: number
}

export interface GetStoredHistoryMsg {
  type: 'get_stored_history'
  symbol: string
  limit: number
  start_epoch?: number
}

export interface ExplainMsg {
  type: 'explain'
  symbol: string
}

export interface AskMarketMsg {
  type: 'ask_market'
  question: string
  symbol?: string
}

export interface NewsSummaryMsg {
  type: 'news_summary'
  symbol: string
  headlines?: string[]
}

export type OutgoingMessage =
  | SubscribeMsg
  | SubscribeGroupMsg
  | ListAssetsMsg
  | GetPricesMsg
  | ChatMsg
  | AnalyzeBehaviorMsg
  | GenerateSocialMsg
  | TradeHistoryMsg
  | CandlesHistoryMsg
  | TradeEventMsg
  | IndicatorsMsg
  | CreateAlertMsg
  | ListAlertsMsg
  | CancelAlertMsg
  | FetchHistoryMsg
  | GetStoredHistoryMsg
  | ExplainMsg
  | AskMarketMsg
  | NewsSummaryMsg

// ── Incoming messages (backend → frontend) ──

export interface InfoResponse {
  type: 'info'
  message: string
}

export interface ErrorResponse {
  type: 'error'
  message: string
}

export interface AssetListResponse {
  type: 'asset_list'
  data: Record<string, string[]>
}

export interface LatestPricesResponse {
  type: 'latest_prices'
  data: Record<string, number>
}

export interface PriceUpdateResponse {
  type: 'price_update'
  symbol: string
  price: number
  timestamp: number
}

export interface ChatResponseMsg {
  type: 'chat_response'
  text: string
}

export interface BehavioralReportResponse {
  type: 'behavioral_report'
  data: BehavioralReport
}

export interface NudgesResponse {
  type: 'nudges'
  data: Nudge[]
}

export interface SocialDraftResponse {
  type: 'social_draft'
  platform: string
  text: string
}

export interface TradeHistoryResponse {
  type: 'trade_history'
  data: {
    status: string
    count: number
    trades: AccountTrade[]
  }
}

export interface CandlesHistoryResponse {
  type: 'candles_history'
  symbol: string
  data: Candle[]
}

export interface IndicatorResultResponse {
  type: 'indicator_result'
  symbol: string
  data: IndicatorData
}

export interface AlertCreatedResponse {
  type: 'alert_created'
  data: {
    status: string
    alert_id: number
    symbol: string
    target_price: number
    direction: string
  }
}

export interface AlertListResponse {
  type: 'alert_list'
  data: PriceAlert[]
}

export interface AlertCancelledResponse {
  type: 'alert_cancelled'
  data: {
    status: string
    alert_id: number
  }
}

export interface HistoryDataResponse {
  type: 'history_data'
  symbol: string
  candles: Candle[]
}

export interface StoredHistoryResponse {
  type: 'stored_history'
  symbol: string
  candles: Candle[]
}

export interface MarketExplanationResponse {
  type: 'market_explanation'
  symbol: string
  text: string
}

export interface MarketAnswerResponse {
  type: 'market_answer'
  text: string
}

export interface NewsSummaryResponse {
  type: 'news_summary'
  symbol: string
  text: string
}

export interface PriceAlertTriggeredResponse {
  type: 'price_alert_triggered'
  alert_id: number
  symbol: string
  target_price: number
  current_price: number
  direction: string
  message: string
}

export type IncomingMessage =
  | InfoResponse
  | ErrorResponse
  | AssetListResponse
  | LatestPricesResponse
  | PriceUpdateResponse
  | ChatResponseMsg
  | BehavioralReportResponse
  | NudgesResponse
  | SocialDraftResponse
  | TradeHistoryResponse
  | CandlesHistoryResponse
  | IndicatorResultResponse
  | AlertCreatedResponse
  | AlertListResponse
  | AlertCancelledResponse
  | HistoryDataResponse
  | StoredHistoryResponse
  | MarketExplanationResponse
  | MarketAnswerResponse
  | NewsSummaryResponse
  | PriceAlertTriggeredResponse

// ── Shared data types ──

export interface TradeData {
  symbol: string
  price: number
  action: 'buy' | 'sell'
  amount: number
  timestamp: number
}

export interface AccountTrade {
  transaction_id: string
  symbol: string
  amount: number
  balance: number
  transaction_time: number
  action_type: string
  longcode: string
}

export interface Candle {
  epoch: number
  open: number
  high: number
  low: number
  close: number
}

export interface IndicatorData {
  status: string
  indicators: {
    sma_20: number[]
    sma_50: number[]
    ema_12: number[]
    ema_26: number[]
    rsi: number[]
    macd: {
      macd_line: number[]
      signal_line: number[]
      histogram: number[]
    }
  }
  latest: {
    price: number
    sma_20: number
    sma_50: number
    ema_12: number
    ema_26: number
    rsi: number
    macd_line: number
    signal_line: number
    macd_histogram: number
  }
  signals: string[]
}

export interface BehavioralReport {
  status: string
  metrics: {
    total_trades: number
    win_rate: number
    streaks: {
      current_streak: number
      type: 'win' | 'loss' | 'unknown'
    }
    discipline_score: {
      score: number
      rule_breaks: Record<string, number>
    }
  }
  alerts: {
    risk: string[]
    overtrading: string[]
    rapid_entries: string[]
  }
  nudges: string[]
  sentiment: number
}

export interface Nudge {
  id: string
  type: 'warning' | 'suggestion' | 'reflection' | 'celebration' | 'break' | 'limit'
  urgency: 'low' | 'medium' | 'high' | 'critical'
  title: string
  message: string
  action_suggestion: string
  trigger: string
  created_at: string
  dismissed: boolean
}

export interface PriceAlert {
  alert_id: number
  symbol: string
  target_price: number
  direction: 'above' | 'below'
  is_active: boolean
  created_at: number
  triggered_at: number | null
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}
