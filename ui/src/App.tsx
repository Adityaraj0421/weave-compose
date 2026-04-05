import { useState, useEffect } from 'react'
import { getStatus, type StatusResponse } from './api'

export default function App(): React.JSX.Element {
  const [status, setStatus] = useState<StatusResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getStatus()
      .then(setStatus)
      .catch((e: Error) => { setError(e.message) })
  }, [])

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-indigo-400">Weave</h1>
        <p className="text-gray-400 mt-1">Platform-aware skill composition layer</p>
      </header>

      <section>
        {!status && !error && (
          <p className="text-gray-500 text-sm">Connecting to Weave server…</p>
        )}
        {status !== null && (
          <p className="text-green-400 text-sm">
            Server connected — {status.total} skill(s) loaded
          </p>
        )}
        {error !== null && (
          <p className="text-red-400 text-sm">
            Server not reachable: {error}. Run{' '}
            <code className="font-mono">weave serve</code> first.
          </p>
        )}
      </section>
    </div>
  )
}
