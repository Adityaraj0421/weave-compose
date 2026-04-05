/** Typed API client for the Weave local FastAPI server. */

const BASE_URL: string = (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:7842'

// ---------------------------------------------------------------------------
// Response types — mirror the server's Pydantic models exactly
// ---------------------------------------------------------------------------

export interface SkillResponse {
  id: string
  name: string
  platform: string
  trigger_context: string
  capabilities: string[]
  source_path: string
  loaded_at: string
}

export interface QueryResult {
  skill: SkillResponse
  score: number
}

export interface LoadResponse {
  loaded: number
  platform: string
}

export interface ComposeResponse {
  composed: string
}

export interface StatusResponse {
  total: number
  by_platform: Record<string, number>
  model: string
}

// ---------------------------------------------------------------------------
// Private helper
// ---------------------------------------------------------------------------

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const detail = await res.text()
    throw new Error(`${res.status} ${detail}`)
  }
  return res.json() as Promise<T>
}

// ---------------------------------------------------------------------------
// Public API functions
// ---------------------------------------------------------------------------

export const getSkills = (): Promise<SkillResponse[]> =>
  request('/skills')

export const loadSkills = (path: string, platform = 'claude_code'): Promise<LoadResponse> =>
  request('/load', { method: 'POST', body: JSON.stringify({ path, platform }) })

export const querySkills = (query: string, topN = 1): Promise<QueryResult[]> =>
  request('/query', { method: 'POST', body: JSON.stringify({ query, top_n: topN }) })

export const composeSkills = (
  skillIds: string[],
  scores: number[],
): Promise<ComposeResponse> =>
  request('/compose', {
    method: 'POST',
    body: JSON.stringify({ skill_ids: skillIds, scores }),
  })

export const getStatus = (): Promise<StatusResponse> =>
  request('/status')
