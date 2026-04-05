import type { SkillResponse } from '../api'

interface SkillCardProps {
  skill: SkillResponse
  onClick: () => void
}

// Full Tailwind class strings — must not be constructed dynamically (tree-shaking)
const PLATFORM_STYLES: Record<string, string> = {
  claude_code: 'bg-indigo-900 text-indigo-300',
  cursor: 'bg-blue-900 text-blue-300',
  codex: 'bg-amber-900 text-amber-300',
  windsurf: 'bg-teal-900 text-teal-300',
}
const DEFAULT_STYLE = 'bg-gray-800 text-gray-400'

export default function SkillCard({ skill, onClick }: SkillCardProps): React.JSX.Element {
  const badgeStyle = PLATFORM_STYLES[skill.platform] ?? DEFAULT_STYLE
  const extraCaps = skill.capabilities.length - 3

  return (
    <div
      onClick={onClick}
      className="cursor-pointer rounded-lg bg-gray-900 p-4 ring-1 ring-gray-800 hover:ring-indigo-500 transition-shadow"
    >
      <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium mb-2 ${badgeStyle}`}>
        {skill.platform.replace('_', ' ')}
      </span>

      <h3 className="text-sm font-semibold text-gray-100 truncate mb-2">{skill.name}</h3>

      <div className="flex flex-wrap gap-1">
        {skill.capabilities.slice(0, 3).map((cap) => (
          <span
            key={cap}
            className="rounded bg-gray-800 px-1.5 py-0.5 text-xs font-mono text-gray-400"
          >
            {cap}
          </span>
        ))}
        {extraCaps > 0 && (
          <span className="rounded bg-gray-800 px-1.5 py-0.5 text-xs text-gray-500">
            +{extraCaps} more
          </span>
        )}
      </div>
    </div>
  )
}
