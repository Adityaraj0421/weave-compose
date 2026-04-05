import { useState, useEffect } from 'react'
import { getSkills, type SkillResponse } from '../api'
import SkillCard from './SkillCard'

const PLATFORM_STYLES: Record<string, string> = {
  claude_code: 'bg-indigo-900 text-indigo-300',
  cursor: 'bg-blue-900 text-blue-300',
  codex: 'bg-amber-900 text-amber-300',
  windsurf: 'bg-teal-900 text-teal-300',
}
const DEFAULT_STYLE = 'bg-gray-800 text-gray-400'

export default function SkillBrowser(): React.JSX.Element {
  const [skills, setSkills] = useState<SkillResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedSkill, setSelectedSkill] = useState<SkillResponse | null>(null)
  const [platformFilter, setPlatformFilter] = useState('all')

  useEffect(() => {
    getSkills()
      .then(setSkills)
      .catch((e: Error) => { setError(e.message) })
      .finally(() => { setLoading(false) })
  }, [])

  const platforms = ['all', ...Array.from(new Set(skills.map((s) => s.platform)))]
  const filtered = platformFilter === 'all' ? skills : skills.filter((s) => s.platform === platformFilter)

  if (loading) return <p className="text-gray-500 text-sm">Loading skills…</p>

  if (error !== null) {
    return (
      <p className="text-red-400 text-sm">
        Server not reachable: {error}. Run <code className="font-mono">weave serve</code> first.
      </p>
    )
  }

  if (skills.length === 0) {
    return (
      <p className="text-gray-500 text-sm">
        No skills loaded. Run <code className="font-mono">weave load &lt;path&gt;</code> first.
      </p>
    )
  }

  return (
    <div className="relative">
      {/* Filter bar */}
      <div className="flex flex-wrap gap-2 mb-4">
        {platforms.map((p) => (
          <button
            key={p}
            onClick={() => { setPlatformFilter(p) }}
            className={`rounded px-3 py-1 text-sm font-medium transition-colors ${
              platformFilter === p
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {p === 'all' ? 'All' : p.replace('_', ' ')}
          </button>
        ))}
        <span className="ml-auto self-center text-xs text-gray-600">
          {filtered.length} skill(s)
        </span>
      </div>

      {/* Card grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((skill) => (
          <SkillCard key={skill.id} skill={skill} onClick={() => { setSelectedSkill(skill) }} />
        ))}
      </div>

      {/* Detail panel */}
      {selectedSkill !== null && (
        <div className="fixed right-0 top-0 h-full w-96 bg-gray-900 shadow-2xl p-6 overflow-y-auto z-10 ring-1 ring-gray-800">
          <button
            onClick={() => { setSelectedSkill(null) }}
            className="absolute top-4 right-4 text-gray-500 hover:text-gray-200 text-xl font-bold"
            aria-label="Close"
          >
            ✕
          </button>

          <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium mb-3 ${PLATFORM_STYLES[selectedSkill.platform] ?? DEFAULT_STYLE}`}>
            {selectedSkill.platform.replace('_', ' ')}
          </span>

          <h2 className="text-lg font-semibold text-gray-100 mb-4">{selectedSkill.name}</h2>

          <section className="mb-4">
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
              Trigger context
            </h4>
            <p className="text-sm text-gray-300 leading-relaxed">{selectedSkill.trigger_context}</p>
          </section>

          <section className="mb-4">
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
              Capabilities
            </h4>
            <div className="flex flex-wrap gap-1">
              {selectedSkill.capabilities.map((cap) => (
                <span key={cap} className="rounded bg-gray-800 px-1.5 py-0.5 text-xs font-mono text-gray-400">
                  {cap}
                </span>
              ))}
            </div>
          </section>

          <section className="mb-4">
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
              Source path
            </h4>
            <p className="text-xs font-mono text-gray-500 break-all">{selectedSkill.source_path}</p>
          </section>

          <section>
            <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">
              Loaded at
            </h4>
            <p className="text-xs text-gray-500">{selectedSkill.loaded_at}</p>
          </section>
        </div>
      )}
    </div>
  )
}
