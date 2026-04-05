import { useState } from 'react'
import SkillBrowser from './components/SkillBrowser'
import VisualComposer from './components/VisualComposer'
import LoadPanel from './components/LoadPanel'

type Tab = 'browse' | 'compose' | 'load'

const TAB_LABELS: Record<Tab, string> = {
  browse: 'Browse Skills',
  compose: 'Compose',
  load: 'Load',
}

export default function App(): React.JSX.Element {
  const [tab, setTab] = useState<Tab>('browse')

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-indigo-400">Weave</h1>
        <p className="text-gray-400 mt-1">Platform-aware skill composition layer</p>

        {/* Tab bar */}
        <div className="flex gap-6 mt-4 border-b border-gray-800">
          {(Object.keys(TAB_LABELS) as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => { setTab(t) }}
              className={`pb-2 text-sm font-medium transition-colors ${
                tab === t
                  ? 'border-b-2 border-indigo-400 text-indigo-400'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {TAB_LABELS[t]}
            </button>
          ))}
        </div>
      </header>

      <main>
        {tab === 'browse' && <SkillBrowser />}
        {tab === 'compose' && <VisualComposer />}
        {tab === 'load' && <LoadPanel />}
      </main>
    </div>
  )
}
