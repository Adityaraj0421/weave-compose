import { useState } from 'react'
import { querySkills, composeSkills, type QueryResult } from '../api'

// Full Tailwind class strings — must not be constructed dynamically (tree-shaking)
const PLATFORM_STYLES: Record<string, string> = {
  claude_code: 'bg-indigo-900 text-indigo-300',
  cursor: 'bg-blue-900 text-blue-300',
  codex: 'bg-amber-900 text-amber-300',
  windsurf: 'bg-teal-900 text-teal-300',
}
const DEFAULT_STYLE = 'bg-gray-800 text-gray-400'

export default function VisualComposer(): React.JSX.Element {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<QueryResult[]>([])
  const [composed, setComposed] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  async function handleQuery(): Promise<void> {
    if (loading || query.trim() === '') return
    setLoading(true)
    setError(null)
    setComposed(null)
    setResults([])
    try {
      const data = await querySkills(query.trim(), 2)
      setResults(data)
      if (data.length > 0) {
        const ids = data.map((r) => r.skill.id)
        const scores = data.map((r) => r.score)
        const composeData = await composeSkills(ids, scores)
        setComposed(composeData.composed)
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  function handleCopy(): void {
    void navigator.clipboard.writeText(composed ?? '')
    setCopied(true)
    setTimeout(() => { setCopied(false) }, 2000)
  }

  return (
    <div className="max-w-3xl">
      {/* Query input row */}
      <div className="flex gap-2 mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => { setQuery(e.target.value) }}
          onKeyDown={(e) => { if (e.key === 'Enter') { void handleQuery() } }}
          placeholder="Describe a task, e.g. 'design a button component'…"
          className="flex-1 rounded bg-gray-900 ring-1 ring-gray-700 px-4 py-2 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-indigo-500"
        />
        <button
          onClick={() => { void handleQuery() }}
          disabled={loading || query.trim() === ''}
          className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Querying…' : 'Query'}
        </button>
      </div>

      {/* Error */}
      {error !== null && (
        <p className="text-red-400 text-sm mb-4">
          Server not reachable: {error}. Run <code className="font-mono">weave serve</code> first.
        </p>
      )}

      {/* Empty state */}
      {!loading && results.length === 0 && error === null && composed === null && (
        <p className="text-gray-600 text-sm">Enter a query above to find and compose matching skills.</p>
      )}

      {/* Matched skills */}
      {results.length > 0 && (
        <section className="mb-6">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Matched Skills
          </h3>
          <div className="flex flex-col gap-2">
            {results.map((r) => (
              <div
                key={r.skill.id}
                className="flex items-center justify-between rounded bg-gray-900 px-4 py-3 ring-1 ring-gray-800"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className={`shrink-0 rounded px-2 py-0.5 text-xs font-medium ${PLATFORM_STYLES[r.skill.platform] ?? DEFAULT_STYLE}`}>
                    {r.skill.platform.replace('_', ' ')}
                  </span>
                  <span className="text-sm text-gray-100 truncate">{r.skill.name}</span>
                </div>
                <span className="shrink-0 ml-4 text-sm font-mono text-indigo-400">
                  {(r.score * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Composed output */}
      {composed !== null && (
        <section>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Composed Context
            </h3>
            <button
              onClick={handleCopy}
              className="rounded bg-gray-800 px-3 py-1 text-xs font-medium text-gray-400 hover:bg-gray-700 hover:text-gray-200 transition-colors"
            >
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <pre className="rounded bg-gray-900 ring-1 ring-gray-800 p-4 text-xs text-gray-300 overflow-x-auto whitespace-pre-wrap break-words">
            <code>{composed}</code>
          </pre>
        </section>
      )}
    </div>
  )
}
