"use client";

import { AppGrid } from "@/components/apps/app-grid";
import { Separator } from "@/components/ui/separator";
import { useProject } from "@/components/context/project";
import { App } from "@/lib/types/app";
import { useEffect, useState } from "react";

export default function AppStorePage() {
  const { project } = useProject();
  const [apps, setApps] = useState<App[]>([]);

  // TODO: implement pagination once we have a lot of apps

  useEffect(() => {
    async function fetchApps() {
      if (
        !project ||
        !project.agents ||
        project.agents.length === 0 ||
        !project.agents[0].api_keys ||
        project.agents[0].api_keys.length === 0
      ) {
        return;
      }

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/v1/apps/`,
          {
            method: "GET",
            headers: {
              "X-API-KEY": project.agents[0].api_keys[0].key,
            },
          }
        );

        if (!response.ok) {
          console.log(response);
          throw new Error(`Failed to fetch apps`);
        }
        const retrievedApps: App[] = await response.json();
        setApps(retrievedApps);
      } catch (error) {
        console.error("Error fetching apps:", error);
      }
    }

    fetchApps();
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
