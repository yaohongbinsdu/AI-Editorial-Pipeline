import type {
  ArticleBrief,
  ArticleDetail,
  CategoryPage,
  CategoryStats,
  ClusterBrief,
  ClusterDetail,
  DashboardOverview,
  PaginatedResponse,
  PipelineRunDetail,
  PipelineRun,
  PipelineStatus,
  RSSSource,
  RSSSourceCreate,
  RSSSourceUpdate,
  SimilarArticle,
} from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1'

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText} — ${url}`)
  }
  return res.json() as Promise<T>
}

function qs(params: Record<string, string | number | boolean | undefined | null>): string {
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== null && v !== '',
  )
  if (entries.length === 0) return ''
  return '?' + new URLSearchParams(entries.map(([k, v]) => [k, String(v)])).toString()
}

// ── Dashboard ───────────────────────────────────────────
export async function getDashboardOverview(hours = 24): Promise<DashboardOverview> {
  return fetchApi(`/dashboard/overview${qs({ hours })}`)
}

export { getDashboardTrending }
async function getDashboardTrending(limit = 10) {
  return fetchApi<{ trending_clusters: ClusterBrief[]; trending_articles: ArticleBrief[] }>(
    `/dashboard/trending${qs({ limit })}`,
  )
}

// ── Articles ────────────────────────────────────────────
export interface ArticleListParams {
  category?: string
  status?: string
  novelty_gate?: boolean
  editorial_vote?: string
  min_score?: number
  sort_by?: string
  order?: 'asc' | 'desc'
  page?: number
  page_size?: number
}

export async function getArticles(
  params: ArticleListParams = {},
): Promise<PaginatedResponse<ArticleBrief>> {
  return fetchApi(`/articles${qs(params as Record<string, string | number | boolean>)}`)
}

export async function getArticle(id: string): Promise<ArticleDetail> {
  return fetchApi(`/articles/${id}`)
}

export async function getSimilarArticles(
  id: string,
  limit = 5,
  threshold = 0.75,
): Promise<SimilarArticle[]> {
  return fetchApi(`/articles/${id}/similar${qs({ limit, threshold })}`)
}

// ── Clusters ────────────────────────────────────────────
export interface ClusterListParams {
  category?: string
  min_articles?: number
  sort_by?: string
  page?: number
  page_size?: number
}

export async function getClusters(
  params: ClusterListParams = {},
): Promise<PaginatedResponse<ClusterBrief>> {
  return fetchApi(`/clusters${qs(params as Record<string, string | number | boolean>)}`)
}

export async function getCluster(id: string): Promise<ClusterDetail> {
  return fetchApi(`/clusters/${id}`)
}

// ── Categories ──────────────────────────────────────────
export async function getCategories(): Promise<CategoryStats[]> {
  return fetchApi('/categories')
}

export async function getCategoryPage(
  slug: string,
  hours = 24,
  page = 1,
  pageSize = 20,
): Promise<CategoryPage> {
  return fetchApi(
    `/categories/${slug}${qs({ hours, page, page_size: pageSize })}`,
  )
}

// ── Sources ─────────────────────────────────────────────
export async function getSources(): Promise<RSSSource[]> {
  return fetchApi('/sources')
}

export async function createSource(data: RSSSourceCreate): Promise<RSSSource> {
  return fetchApi('/sources', { method: 'POST', body: JSON.stringify(data) })
}

export async function updateSource(id: string, data: RSSSourceUpdate): Promise<RSSSource> {
  return fetchApi(`/sources/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
}

export async function deleteSource(id: string): Promise<void> {
  await fetchApi(`/sources/${id}`, { method: 'DELETE' })
}

// ── Pipeline ────────────────────────────────────────────
export async function getPipelineStatus(): Promise<PipelineStatus> {
  return fetchApi('/pipeline/status')
}

export async function getPipelineRuns(limit = 24): Promise<PipelineRun[]> {
  return fetchApi(`/pipeline/runs${qs({ limit })}`)
}

export async function getPipelineRunDetail(runId: string): Promise<PipelineRunDetail> {
  return fetchApi(`/pipeline/runs/${runId}`)
}

export async function triggerPipeline(): Promise<{ run_id: string; message: string }> {
  return fetchApi('/pipeline/trigger?sync=true', { method: 'POST' })
}
