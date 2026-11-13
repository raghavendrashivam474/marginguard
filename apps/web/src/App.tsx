import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-emerald-500 flex items-center justify-center font-bold text-slate-950">
              M
            </div>
            <h1 className="text-xl font-semibold tracking-tight">MarginGuard</h1>
          </div>
          <Badge variant="outline" className="border-emerald-500/50 text-emerald-400">
            v0.1.0
          </Badge>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="max-w-2xl w-full space-y-8">
          {/* Hero */}
          <div className="text-center space-y-4">
            <h2 className="text-3xl font-bold tracking-tight">Financial Leakage Detection</h2>
            <p className="text-slate-400 text-lg">
              AI-assisted identification of duplicate invoices, payment mismatches, and pricing
              discrepancies for SMEs and distributors.
            </p>
          </div>

          {/* Status Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">Frontend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-emerald-400 font-medium">Running</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">React + Vite + TypeScript</p>
              </CardContent>
            </Card>

            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">Backend</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-slate-500" />
                  <span className="text-slate-400 font-medium">Not Connected</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">FastAPI + Python</p>
              </CardContent>
            </Card>

            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">Database</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-slate-500" />
                  <span className="text-slate-400 font-medium">Not Configured</span>
                </div>
                <p className="text-xs text-slate-500 mt-1">PostgreSQL</p>
              </CardContent>
            </Card>
          </div>

          {/* Sprint Info */}
          <Card className="bg-slate-900/50 border-slate-800">
            <CardContent className="pt-6">
              <p className="text-sm text-slate-400 text-center">
                <span className="text-slate-300 font-medium">Phase 0 — MG-S0.1</span> &middot;
                Project foundation established. No financial intelligence functionality at this
                stage.
              </p>
            </CardContent>
          </Card>

          {/* CTA */}
          <div className="flex justify-center gap-4">
            <Button className="bg-emerald-600 hover:bg-emerald-500">View API Docs</Button>
            <Button variant="outline" className="border-slate-700 text-slate-300">
              Documentation
            </Button>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 px-6 py-4">
        <p className="text-center text-xs text-slate-600">
          MarginGuard &middot; Development Environment &middot; Sprint MG-S0.1
        </p>
      </footer>
    </div>
  )
}

export default App
