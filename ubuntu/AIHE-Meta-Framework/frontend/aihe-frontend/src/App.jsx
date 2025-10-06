import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  BarChart3, 
  Building2, 
  CheckCircle, 
  Clock, 
  FileText, 
  Home, 
  Settings, 
  TrendingUp,
  Users,
  Brain,
  Shield,
  Target,
  Zap
} from 'lucide-react'
import './App.css'

// Main Dashboard Component
function Dashboard() {
  const [selectedMetric, setSelectedMetric] = useState('rgi')

  const metrics = {
    rgi: { value: 0.72, label: 'Reifegrad-Index', color: 'bg-blue-500', description: 'Gewichteter Gesamtreifegrad' },
    eqi: { value: 0.68, label: 'Equilibrium Quality Index', color: 'bg-green-500', description: 'Ausgewogenheit der Entwicklung' },
    si: { value: 0.31, label: 'Spannungsindex', color: 'bg-orange-500', description: 'Systemspannungen zwischen Dimensionen' },
    sbs: { value: 0.70, label: 'System Balance Score', color: 'bg-purple-500', description: 'Strategischer Gesamtwert' }
  }

  const dimensions = [
    { id: 'D1', name: 'Führung & Governance', score: 2.5, target: 3.0, icon: Shield },
    { id: 'D2', name: 'Strategie & Alignment', score: 2.8, target: 3.2, icon: Target },
    { id: 'D3', name: 'Kultur & Veränderung', score: 1.8, target: 3.0, icon: Users },
    { id: 'D4', name: 'Kompetenzen & Bildung', score: 1.5, target: 3.5, icon: Brain },
    { id: 'D5', name: 'Datenqualität & Ethik', score: 2.3, target: 3.0, icon: Shield },
    { id: 'D6', name: 'Technologieeinsatz', score: 3.5, target: 3.0, icon: Zap },
    { id: 'D7', name: 'Prozesse & Automatisierung', score: 2.7, target: 3.0, icon: Settings },
    { id: 'D8', name: 'Wirkung & Nachhaltigkeit', score: 2.0, target: 3.0, icon: TrendingUp }
  ]

  const recentAssessments = [
    { id: 1, name: 'Q4 2024 Assessment', status: 'completed', date: '2024-10-01', progress: 100 },
    { id: 2, name: 'Follow-up Assessment', status: 'in_progress', date: '2024-10-15', progress: 65 },
    { id: 3, name: 'Quick Scan', status: 'draft', date: '2024-10-20', progress: 0 }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Brain className="h-8 w-8 text-blue-600" />
                <h1 className="text-xl font-bold text-slate-900 dark:text-white">AIHE Meta-Framework</h1>
              </div>
            </div>
            <nav className="flex space-x-4">
              <Button variant="ghost" size="sm">
                <Home className="h-4 w-4 mr-2" />
                Dashboard
              </Button>
              <Button variant="ghost" size="sm">
                <FileText className="h-4 w-4 mr-2" />
                Assessments
              </Button>
              <Button variant="ghost" size="sm">
                <BarChart3 className="h-4 w-4 mr-2" />
                Reports
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
            Willkommen im AIHE Meta-Framework
          </h2>
          <p className="text-slate-600 dark:text-slate-300">
            Bewerten und steuern Sie die verantwortungsvolle Integration von KI in Ihrer Organisation
          </p>
        </div>

        {/* Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {Object.entries(metrics).map(([key, metric]) => (
            <Card 
              key={key} 
              className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                selectedMetric === key ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => setSelectedMetric(key)}
            >
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-600 dark:text-slate-300">
                  {metric.label}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-2xl font-bold text-slate-900 dark:text-white">
                    {(metric.value * 100).toFixed(0)}%
                  </div>
                  <div className={`w-3 h-3 rounded-full ${metric.color}`}></div>
                </div>
                <Progress value={metric.value * 100} className="mt-2" />
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {metric.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Dimensions Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Dimensions Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5" />
                <span>Dimensionen Übersicht</span>
              </CardTitle>
              <CardDescription>
                Bewertung der 8 Kerndimensionen des AIHE Frameworks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {dimensions.map((dimension) => {
                  const Icon = dimension.icon
                  const gap = Math.abs(dimension.target - dimension.score)
                  const gapPercentage = (gap / 4.0) * 100
                  
                  return (
                    <div key={dimension.id} className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-700">
                      <div className="flex items-center space-x-3">
                        <Icon className="h-5 w-5 text-slate-600 dark:text-slate-300" />
                        <div>
                          <div className="font-medium text-sm text-slate-900 dark:text-white">
                            {dimension.name}
                          </div>
                          <div className="text-xs text-slate-500 dark:text-slate-400">
                            Ist: {dimension.score} | Soll: {dimension.target}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={gapPercentage > 25 ? 'destructive' : gapPercentage > 15 ? 'secondary' : 'default'}>
                          Gap: {gap.toFixed(1)}
                        </Badge>
                        <Progress value={(dimension.score / 4.0) * 100} className="w-16" />
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Recent Assessments */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>Aktuelle Assessments</span>
              </CardTitle>
              <CardDescription>
                Übersicht über laufende und abgeschlossene Bewertungen
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentAssessments.map((assessment) => (
                  <div key={assessment.id} className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-700">
                    <div className="flex items-center space-x-3">
                      {assessment.status === 'completed' && <CheckCircle className="h-5 w-5 text-green-500" />}
                      {assessment.status === 'in_progress' && <Clock className="h-5 w-5 text-orange-500" />}
                      {assessment.status === 'draft' && <FileText className="h-5 w-5 text-slate-400" />}
                      <div>
                        <div className="font-medium text-sm text-slate-900 dark:text-white">
                          {assessment.name}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">
                          {assessment.date}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={
                        assessment.status === 'completed' ? 'default' :
                        assessment.status === 'in_progress' ? 'secondary' : 'outline'
                      }>
                        {assessment.status === 'completed' ? 'Abgeschlossen' :
                         assessment.status === 'in_progress' ? 'In Bearbeitung' : 'Entwurf'}
                      </Badge>
                      <Progress value={assessment.progress} className="w-16" />
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4">
                <Button className="w-full">
                  <FileText className="h-4 w-4 mr-2" />
                  Neues Assessment erstellen
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-blue-600">
                <Zap className="h-5 w-5" />
                <span>Quick Scan</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600 dark:text-slate-300 mb-4">
                Schnelle 2-Stunden-Bewertung für einen ersten Überblick
              </p>
              <Button variant="outline" className="w-full">
                Quick Scan starten
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-green-600">
                <Building2 className="h-5 w-5" />
                <span>Organisation</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600 dark:text-slate-300 mb-4">
                Verwalten Sie Ihre Organisationsdaten und Archetypen
              </p>
              <Button variant="outline" className="w-full">
                Organisation bearbeiten
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-purple-600">
                <TrendingUp className="h-5 w-5" />
                <span>Lernloop</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600 dark:text-slate-300 mb-4">
                Starten Sie einen iterativen Verbesserungszyklus
              </p>
              <Button variant="outline" className="w-full">
                Lernloop beginnen
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
      </Routes>
    </Router>
  )
}

export default App
