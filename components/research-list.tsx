"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Clock, Eye, RefreshCw } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface ResearchTopic {
  id: number
  topic: string
  status: string
  created_at: string
}

interface ResearchListProps {
  onResearchSelected: (id: number) => void
  refreshTrigger: number
}

export function ResearchList({ onResearchSelected, refreshTrigger }: ResearchListProps) {
  const [topics, setTopics] = useState<ResearchTopic[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const { toast } = useToast()

  const fetchTopics = async (showRefreshIndicator = false) => {
    if (showRefreshIndicator) {
      setIsRefreshing(true)
    } else {
      setIsLoading(true)
    }

    try {
      const response = await fetch("http://localhost:8000/research")

      if (!response.ok) {
        throw new Error("Failed to fetch research topics")
      }

      const data = await response.json()
      setTopics(data)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load research topics",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    fetchTopics()
  }, [refreshTrigger])

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
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Research History</h2>
          <Skeleton className="h-10 w-24" />
        </div>
        {[...Array(3)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <Skeleton className="h-6 w-20" />
                <Skeleton className="h-9 w-24" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-foreground">Research History</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={() => fetchTopics(true)}
          disabled={isRefreshing}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {topics.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
              <Clock className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium text-foreground mb-2">No Research Topics Yet</h3>
            <p className="text-muted-foreground">
              Submit your first research topic to get started with AI-powered research.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {topics.map((topic) => (
            <Card key={topic.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <CardTitle className="text-lg text-balance leading-tight">{topic.topic}</CardTitle>
                    <CardDescription className="flex items-center gap-2 mt-2">
                      <Clock className="w-4 h-4" />
                      {formatDate(topic.created_at)}
                    </CardDescription>
                  </div>
                  <Badge className={getStatusColor(topic.status)}>
                    {topic.status.charAt(0).toUpperCase() + topic.status.slice(1)}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">Research ID: #{topic.id}</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onResearchSelected(topic.id)}
                    className="flex items-center gap-2"
                  >
                    <Eye className="w-4 h-4" />
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
