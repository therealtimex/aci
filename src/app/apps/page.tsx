"use client";

import { AppGrid } from "@/components/apps/app-grid";
import { Separator } from "@/components/ui/separator";
import { useProject } from "@/components/context/project";
import { App } from "@/lib/types/app";
import { useEffect, useState } from "react";
import { getApiKey } from "@/lib/api/util";
import { getAllApps } from "@/lib/api/app";

export default function AppStorePage() {
  const { project } = useProject();
  const [apps, setApps] = useState<App[]>([]);

  // TODO: implement pagination once we have a lot of apps
  useEffect(() => {
    async function loadApps() {
      try {
        if (!project) {
          console.warn("No active project");
          return;
        }

        const apiKey = getApiKey(project);
        const apps = await getAllApps(apiKey);

        setApps(apps);
      } catch (error) {
        console.error("Error fetching apps:", error);
      }
    }
    loadApps();
  }, [project]);

  return (
    <div>
      <div className="m-4">
        <h1 className="text-2xl font-bold">App Store</h1>
        <p className="text-sm text-muted-foreground">
          Browse and connect with your favorite apps and tools.
        </p>
      </div>
      <Separator />

      <div className="m-4">
        <AppGrid apps={apps} />
      </div>
    </div>
  );
}
