"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { ArrowLeft, Clock, ExternalLink, Tag, CheckCircle, XCircle, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface WorkflowLog {
  id: number
  step_number: number
  step_name: string
  status: string
  log_message: string
  execution_time_ms: number
  created_at: string
}

interface ResearchResult {
  id: number
  article_title: string
  article_url: string
  article_summary: string
  keywords: string[]
  source_api: string
  created_at: string
}

interface ResearchDetailData {
  id: number
  topic: string
  status: string
  created_at: string
  updated_at: string
  workflow_logs: WorkflowLog[]
  research_results: ResearchResult[]
}

interface ResearchDetailProps {
  researchId: number
  onBack: () => void
}

export function ResearchDetail({ researchId, onBack }: ResearchDetailProps) {
  const [data, setData] = useState<ResearchDetailData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const { toast } = useToast()

  useEffect(() => {
    const fetchResearchDetail = async () => {
      try {
        const response = await fetch(`http://localhost:8000/research/${researchId}`)

        if (!response.ok) {
          throw new Error("Failed to fetch research details")
        }

        const result = await response.json()
        setData(result)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load research details",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchResearchDetail()

    // Poll for updates if status is processing or queued
    const interval = setInterval(() => {
      if (data?.status === "processing" || data?.status === "queued") {
        fetchResearchDetail()
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [researchId, data?.status])

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return <CheckCircle className="w-4 h-4 text-chart-1" />
      case "processing":
        return <Loader2 className="w-4 h-4 text-chart-2 animate-spin" />
      case "failed":
        return <XCircle className="w-4 h-4 text-destructive" />
      default:
        return <Clock className="w-4 h-4 text-muted-foreground" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return "bg-chart-1 text-chart-1-foreground"
      case "processing":
        return "bg-chart-2 text-chart-2-foreground"
      case "queued":
        return "bg-chart-4 text-chart-4-foreground"
      case "failed":
        return "bg-destructive text-destructive-foreground"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-8 w-64" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <Skeleton className="h-64 w-full" />
            <Skeleton className="h-48 w-full" />
          </div>
          <div className="space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-48 w-full" />
          </div>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">Research details not found</p>
        <Button onClick={onBack} className="mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to List
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <Button variant="outline" onClick={onBack}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-bold text-foreground text-balance">{data.topic}</h1>
            <Badge className={getStatusColor(data.status)}>
              {getStatusIcon(data.status)}
              <span className="ml-1">{data.status.charAt(0).toUpperCase() + data.status.slice(1)}</span>
            </Badge>
          </div>
          <p className="text-muted-foreground">
            Research ID: #{data.id} • Created: {formatDate(data.created_at)}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Research Results */}
          <Card>
            <CardHeader>
              <CardTitle>Research Results</CardTitle>
              <CardDescription>
                {data.research_results.length > 0
                  ? `Found ${data.research_results.length} relevant articles`
                  : "No results available yet"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {data.research_results.length > 0 ? (
                <div className="space-y-4">
                  {data.research_results.map((result, index) => (
                    <div key={result.id} className="border border-border rounded-lg p-4">
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <h3 className="font-semibold text-foreground text-balance leading-tight">
                          {result.article_title}
                        </h3>
                        <Badge variant="outline" className="shrink-0">
                          {result.source_api}
                        </Badge>
                      </div>

                      <p className="text-sm text-muted-foreground mb-3 leading-relaxed">{result.article_summary}</p>

                      <div className="flex items-center justify-between gap-4">
                        <div className="flex items-center gap-2 flex-wrap">
                          <Tag className="w-4 h-4 text-muted-foreground" />
                          {result.keywords.map((keyword, i) => (
                            <Badge key={i} variant="secondary" className="text-xs">
                              {keyword}
                            </Badge>
                          ))}
                        </div>

                        <Button variant="outline" size="sm" asChild>
                          <a href={result.article_url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="w-4 h-4 mr-2" />
                            View Article
                          </a>
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                    <Clock className="w-8 h-8 text-muted-foreground" />
                  </div>
                  <p className="text-muted-foreground">
                    {data.status === "processing" || data.status === "queued"
                      ? "Research in progress. Results will appear here when ready."
                      : "No research results available."}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Status Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Current Status</span>
                <Badge className={getStatusColor(data.status)}>
                  {data.status.charAt(0).toUpperCase() + data.status.slice(1)}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Last Updated</span>
                <span className="text-sm text-foreground">{formatDate(data.updated_at)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Results Found</span>
                <span className="text-sm text-foreground">{data.research_results.length}</span>
              </div>
            </CardContent>
          </Card>

          {/* Workflow Logs */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Workflow Progress</CardTitle>
              <CardDescription>Step-by-step execution logs</CardDescription>
            </CardHeader>
            <CardContent>
              {data.workflow_logs.length > 0 ? (
                <div className="space-y-4">
                  {data.workflow_logs
                    .sort((a, b) => a.step_number - b.step_number)
                    .map((log, index) => (
                      <div key={log.id} className="relative">
                        {index < data.workflow_logs.length - 1 && (
                          <div className="absolute left-4 top-8 w-px h-8 bg-border" />
                        )}
                        <div className="flex items-start gap-3">
                          <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                              log.status === "completed"
                                ? "bg-chart-1 text-chart-1-foreground"
                                : log.status === "failed"
                                  ? "bg-destructive text-destructive-foreground"
                                  : "bg-muted text-muted-foreground"
                            }`}
                          >
                            {log.status === "completed" ? (
                              <CheckCircle className="w-4 h-4" />
                            ) : log.status === "failed" ? (
                              <XCircle className="w-4 h-4" />
                            ) : (
                              <span className="text-xs font-medium">{log.step_number}</span>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between gap-2">
                              <h4 className="text-sm font-medium text-foreground">{log.step_name}</h4>
                              {log.execution_time_ms && (
                                <span className="text-xs text-muted-foreground">{log.execution_time_ms}ms</span>
                              )}
                            </div>
                            <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{log.log_message}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-sm text-muted-foreground">No workflow logs available yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
