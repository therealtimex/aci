"use client"

import { useParams } from "next/navigation"
import { Input } from "@/components/ui/input"
import { AppCard } from "./app-card"
import { type App } from "@/lib/dummy-data"
import { useState } from "react"

interface AppGridProps {
  apps: App[];
}

export function AppGrid({ apps }: AppGridProps) {
  const params = useParams<{ project: string }>()
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  // Get unique categories from all apps
  const categories = Array.from(
    new Set(apps.flatMap((app) => app.categories))
  ).sort()

  // Filter apps based on search query and selected category
  const filteredApps = apps.filter((app) => {
    const matchesSearch = app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      app.description.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesCategory = !selectedCategory || app.categories.includes(selectedCategory)
    
    return matchesSearch && matchesCategory
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
        <Input
          placeholder="Search apps..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="max-w-sm"
        />
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`rounded-full px-3 py-1 text-sm ${
              !selectedCategory
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground"
            }`}
          >
            All
          </button>
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`rounded-full px-3 py-1 text-sm ${
                selectedCategory === category
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {filteredApps.map((app) => (
          <AppCard key={app.id} app={app} projectName={params.project} />
        ))}
      </div>

      {filteredApps.length === 0 && (
        <div className="text-center text-muted-foreground">
          No apps found matching your criteria
        </div>
      )}
    </div>
  )
}
