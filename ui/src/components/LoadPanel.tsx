import { useState } from 'react'
import { loadSkills, getStatus, type LoadResponse, type StatusResponse } from '../api'

// Full Tailwind class strings — must not be constructed dynamically (tree-shaking)
const PLATFORM_STYLES: Record<string, string> = {
  claude_code: 'bg-indigo-900 text-indigo-300',
  cursor: 'bg-blue-900 text-blue-300',
  codex: 'bg-amber-900 text-amber-300',
  windsurf: 'bg-teal-900 text-teal-300',
}
const DEFAULT_STYLE = 'bg-gray-800 text-gray-400'

const PLATFORM_OPTIONS: string[] = ['claude_code', 'cursor', 'codex', 'windsurf']

export default function LoadPanel(): React.JSX.Element {
  const [path, setPath] = useState('')
  const [platform, setPlatform] = useState('claude_code')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<LoadResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [status, setStatus] = useState<StatusResponse | null>(null)

  async function handleLoad(): Promise<void> {
    if (loading || path.trim() === '') return
    setLoading(true)
    setError(null)
    setResult(null)
    setStatus(null)
    try {
      const data = await loadSkills(path.trim(), platform)
      setResult(data)
      const statusData = await getStatus()
      setStatus(statusData)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl">
      <h2 className="text-lg font-semibold text-gray-100 mb-4">Load Skills</h2>

      {/* Path input */}
      <div className="flex gap-2 mb-3">
        <input
          type="text"
          value={path}
          onChange={(e) => { setPath(e.target.value) }}
          onKeyDown={(e) => { if (e.key === 'Enter') { void handleLoad() } }}
          placeholder="/path/to/skills/directory"
          className="flex-1 rounded bg-gray-900 ring-1 ring-gray-700 px-4 py-2 text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-indigo-500"
        />
      </div>

      {/* Platform select + Load button */}
      <div className="flex gap-2 mb-6">
        <select
          value={platform}
          onChange={(e) => { setPlatform(e.target.value) }}
          className="rounded bg-gray-900 ring-1 ring-gray-700 px-3 py-2 text-sm text-gray-100 focus:outline-none focus:ring-indigo-500"
        >
          {PLATFORM_OPTIONS.map((p) => (
            <option key={p} value={p}>
              {p.replace('_', ' ')}
            </option>
          ))}
        </select>
        <button
          onClick={() => { void handleLoad() }}
          disabled={loading || path.trim() === ''}
          className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Loading…' : 'Load'}
        </button>
      </div>

      {/* Error */}
      {error !== null && (
        <p className="text-red-400 text-sm mb-4">
          Failed to load: {error}. Check the path and ensure{' '}
          <code className="font-mono">weave serve</code> is running.
        </p>
      )}

      {/* Success card */}
      {result !== null && (
        <div className="rounded bg-gray-900 ring-1 ring-gray-800 p-4">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-indigo-400 font-semibold text-sm">
              Loaded {result.loaded} skill{result.loaded !== 1 ? 's' : ''}
            </span>
            <span className={`rounded px-2 py-0.5 text-xs font-medium ${PLATFORM_STYLES[result.platform] ?? DEFAULT_STYLE}`}>
              {result.platform.replace('_', ' ')}
            </span>
          </div>

          {/* Registry status */}
          {status !== null && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Registry total: {status.total}
              </p>
              <div className="flex flex-wrap gap-1">
                {Object.entries(status.by_platform).map(([p, count]) => (
                  <span
                    key={p}
                    className="rounded bg-gray-800 px-2 py-0.5 text-xs font-mono text-gray-400"
                  >
                    {p.replace('_', ' ')}: {count}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
