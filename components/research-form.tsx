"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardContent } from "@/components/ui/card"
import { Loader2, Send, CheckCircle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface ResearchFormProps {
  onSubmitted: () => void
}

export function ResearchForm({ onSubmitted }: ResearchFormProps) {
  const [topic, setTopic] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!topic.trim()) {
      toast({
        title: "Error",
        description: "Please enter a research topic",
        variant: "destructive",
      })
      return
    }

    setIsSubmitting(true)

    try {
      const response = await fetch("http://localhost:8000/research", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic: topic.trim() }),
      })

      if (!response.ok) {
        throw new Error("Failed to submit research topic")
      }

      const result = await response.json()

      setIsSubmitted(true)
      setTopic("")

      toast({
        title: "Research Submitted",
        description: "Your research topic has been queued for processing",
      })

      onSubmitted()

      // Reset submitted state after 3 seconds
      setTimeout(() => {
        setIsSubmitted(false)
      }, 3000)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to submit research topic. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="topic">Research Topic</Label>
        <Textarea
          id="topic"
          placeholder="Enter your research topic (e.g., 'Artificial Intelligence in Healthcare', 'Climate Change Solutions', 'Quantum Computing Applications')"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="min-h-[100px] resize-none"
          maxLength={500}
          disabled={isSubmitting}
        />
        <p className="text-sm text-muted-foreground">{topic.length}/500 characters</p>
      </div>

      <div className="flex items-center gap-3">
        <Button type="submit" disabled={isSubmitting || !topic.trim()} className="flex items-center gap-2">
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Processing...
            </>
          ) : isSubmitted ? (
            <>
              <CheckCircle className="w-4 h-4" />
              Submitted
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Start Research
            </>
          )}
        </Button>

        {isSubmitted && (
          <Card className="border-chart-1 bg-chart-1/5">
            <CardContent className="p-3">
              <p className="text-sm text-chart-1 font-medium">
                Research queued successfully! Check the History tab to monitor progress.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </form>
  )
}
