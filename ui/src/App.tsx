import SkillBrowser from './components/SkillBrowser'

export default function App(): React.JSX.Element {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-indigo-400">Weave</h1>
        <p className="text-gray-400 mt-1">Platform-aware skill composition layer</p>
      </header>

      <main>
        <SkillBrowser />
      </main>
    </div>
  )
}
