export type EditorialVote = 'must_read' | 'interesting' | 'skip'

export type ArticleStatus =
  | 'pending'
  | 'fetching'
  | 'fetched'
  | 'summarizing'
  | 'summarized'
  | 'vectorizing'
  | 'vectorized'
  | 'scoring'
  | 'completed'
  | 'fetch_failed'
  | 'summary_failed'
  | 'score_failed'

export type CategorySlug =
  | 'finance'
  | 'technology'
  | 'commercial_space'
  | 'new_energy'
  | 'healthcare'
  | 'agriculture'
  | 'consumer'
  | 'real_estate'
  | 'manufacturing'
  | 'crypto'
  | 'macro_economy'
  | 'regulation'
  | 'other'

export const CATEGORY_LABELS: Record<CategorySlug, string> = {
  finance: '金融',
  technology: '科技',
  commercial_space: '商业航天',
  new_energy: '新能源',
  healthcare: '医疗健康',
  agriculture: '农业',
  consumer: '消费',
  real_estate: '房地产',
  manufacturing: '制造业',
  crypto: '加密货币',
  macro_economy: '宏观经济',
  regulation: '监管政策',
  other: '其他',
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface RSSSourceBrief {
  id: string
  name: string
  category: CategorySlug
}

export interface RSSSource {
  id: string
  url: string
  name: string
  category: CategorySlug
  enabled: boolean
  fetch_interval_minutes: number
  last_fetched_at: string | null
  consecutive_failures: number
}

export interface RSSSourceCreate {
  url: string
  name: string
  category: CategorySlug
  fetch_interval_minutes?: number
}

export interface RSSSourceUpdate {
  name?: string
  category?: CategorySlug
  enabled?: boolean
  fetch_interval_minutes?: number
}

export interface SummaryData {
  human_tldr: string
  vector_tldr: string
  key_points: string[]
  rewritten_title: string
  category: CategorySlug
  tags: string[]
}

export interface GravityScoreData {
  industry_impact: number
  consumer_impact: number
  actionability: number
  risk_urgency: number
  novelty: number
  technical_depth: number
  second_order_potential: number
  builder_relevance: number
  entertainment_value: number
  signal_to_noise: number
  viral_potential: number
  early_trend_signal: number
  pr_fluff: number
  speculation: number
  concreteness: number
  paid_sponsorship: number
  editorial_vote: EditorialVote
  novelty_gate: boolean
  composite_score: number
  reasoning: string | null
}

export interface ArticleBrief {
  id: string
  final_title: string
  rewritten_title: string | null
  human_tldr: string | null
  category: CategorySlug | null
  tags: string[]
  composite_score: number | null
  editorial_vote: EditorialVote | null
  viral_potential: number | null
  published_at: string | null
  source_name: string
  final_image_url: string | null
}

export interface ArticleDetail {
  id: string
  original_url: string
  final_title: string
  final_content: string
  final_image_url: string | null
  published_at: string | null
  author: string | null
  status: ArticleStatus
  source: RSSSourceBrief
  summary: SummaryData | null
  gravity_score: GravityScoreData | null
  cluster: ClusterBrief | null
}

export interface SimilarArticle {
  article: ArticleBrief
  similarity: number
}

export interface ClusterBrief {
  id: string
  title: string
  category: CategorySlug
  article_count: number
  last_updated_at: string
  top_article: ArticleBrief | null
}

export interface ClusterDetail {
  id: string
  title: string
  category: CategorySlug
  article_count: number
  expansion_triggered: boolean
  first_seen_at: string
  last_updated_at: string
  articles: ArticleBrief[]
}

export interface CategoryStats {
  slug: CategorySlug
  name: string
  article_count: number
  cluster_count: number
  heat_score: number
  trending_up: boolean
}

export interface CategoryPage {
  category: CategoryStats
  clusters: ClusterBrief[]
  articles: PaginatedResponse<ArticleBrief>
  top_keywords: string[]
}

export interface PipelineHealth {
  last_run_at: string | null
  last_run_status: string | null
  success_rate_24h: number
  articles_processed_24h: number
}

export interface MarketFocus {
  category: CategorySlug
  heat_score: number
  article_count: number
  top_keywords: string[]
}

export interface DashboardOverview {
  time_window_hours: number
  total_articles: number
  category_breakdown: CategoryStats[]
  top_clusters: ClusterBrief[]
  must_read_articles: ArticleBrief[]
  market_focus: MarketFocus[]
  pipeline_health: PipelineHealth
}

export interface PipelineRun {
  id: string
  started_at: string
  completed_at: string | null
  status: 'running' | 'completed' | 'failed'
  articles_discovered: number
  articles_processed: number
  articles_failed: number
  duration_seconds: number | null
}

export interface StepStats {
  step_name: string
  status: string
  count: number
  avg_duration_ms: number
}

export interface PipelineStatus {
  is_running: boolean
  current_run: PipelineRun | null
  last_completed_run: PipelineRun | null
  step_stats_24h: StepStats[]
}

export interface StepLog {
  step_name: string
  article_id: string | null
  status: string
  duration_ms: number
  error_message: string | null
  retry_count: number
}

export interface PipelineRunDetail {
  run: PipelineRun
  step_logs: StepLog[]
}

export interface GravityScoreDetail {
  industry_impact: number
  consumer_impact: number
  actionability: number
  risk_urgency: number
  novelty: number
  technical_depth: number
  second_order_potential: number
  builder_relevance: number
  entertainment_value: number
  signal_to_noise: number
  viral_potential: number
  early_trend_signal: number
  pr_fluff: number
  speculation: number
  concreteness: number
  paid_sponsorship: number
  editorial_vote: string
  novelty_gate: boolean
  composite_score: number
  reasoning: string
}
