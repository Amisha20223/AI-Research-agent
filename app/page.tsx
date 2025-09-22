"use client"

import { useState } from "react"
import { ResearchForm } from "@/components/research-form"
import { ResearchList } from "@/components/research-list"
import { ResearchDetail } from "@/components/research-detail"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Brain, Search, FileText } from "lucide-react"

export default function HomePage() {
  const [selectedResearchId, setSelectedResearchId] = useState<number | null>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleResearchSubmitted = () => {
    setRefreshTrigger((prev) => prev + 1)
  }

  const handleResearchSelected = (id: number) => {
    setSelectedResearchId(id)
  }

  const handleBackToList = () => {
    setSelectedResearchId(null)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-12 h-12 bg-primary rounded-lg">
              <Brain className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">AI  Research  Agent</h1>
              <p className="text-muted-foreground">Intelligent research automation platform</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {selectedResearchId ? (
          <ResearchDetail researchId={selectedResearchId} onBack={handleBackToList} />
        ) : (
          <Tabs defaultValue="submit" className="space-y-6">
            <TabsList className="grid w-full grid-cols-2 max-w-md">
              <TabsTrigger value="submit" className="flex items-center gap-2">
                <Search className="w-4 h-4" />
                Submit Research
              </TabsTrigger>
              <TabsTrigger value="history" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Research History
              </TabsTrigger>
            </TabsList>

            <TabsContent value="submit" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Submit New Research Topic</CardTitle>
                  <CardDescription>
                    Enter a research topic and our AI agent will gather relevant information, analyze articles, and
                    provide structured results with detailed workflow logs.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResearchForm onSubmitted={handleResearchSubmitted} />
                </CardContent>
              </Card>

              {/* Quick Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-chart-1/10 rounded-lg flex items-center justify-center">
                        <Search className="w-5 h-5 text-chart-1" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Average Processing</p>
                        <p className="text-2xl font-bold text-foreground">2-3 min</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-chart-2/10 rounded-lg flex items-center justify-center">
                        <FileText className="w-5 h-5 text-chart-2" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Articles per Research</p>
                        <p className="text-2xl font-bold text-foreground">5</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-chart-3/10 rounded-lg flex items-center justify-center">
                        <Brain className="w-5 h-5 text-chart-3" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Workflow Steps</p>
                        <p className="text-2xl font-bold text-foreground">5</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="history">
              <ResearchList onResearchSelected={handleResearchSelected} refreshTrigger={refreshTrigger} />
            </TabsContent>
          </Tabs>
        )}
      </main>
    </div>
  )
}
