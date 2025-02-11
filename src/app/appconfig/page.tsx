"use client";

import { Button } from "@/components/ui/button";
import { useCallback, useEffect, useState } from "react";
import { GoPlus } from "react-icons/go";
import { AppConfig } from "@/lib/types/appconfig";
import { Separator } from "@/components/ui/separator";
import { AppConfigsTable } from "@/components/appconfig/app-configs-table";
import { useProject } from "@/components/context/project";
import { App } from "@/lib/types/app";

export default function AppConfigPage() {
  const [appConfigs, setAppConfigs] = useState<AppConfig[]>([]);
  const [appsMap, setAppsMap] = useState<Record<string, App>>({});

  const { project } = useProject();

  const updateAppConfigs = useCallback(async () => {
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
        `${process.env.NEXT_PUBLIC_API_URL}/v1/app-configurations`,
        {
          method: "GET",
          headers: {
            "X-API-KEY": project.agents[0].api_keys[0].key,
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch app configurations`);
      }

      const data = await response.json();
      setAppConfigs(data);
    } catch (error) {
      console.error("Error fetching app configs:", error);
    }
  }, [project, setAppConfigs]);

  const updateAppsMap = useCallback(async () => {
    if (
      !project ||
      !project.agents ||
      project.agents.length === 0 ||
      !project.agents[0].api_keys ||
      project.agents[0].api_keys.length === 0
    ) {
      return;
    }

    const params = new URLSearchParams();
    appConfigs.forEach((config) => {
      params.append("app_ids", config.app_id);
    });

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/v1/apps/?${params.toString()}`,
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
      setAppsMap(
        retrievedApps.reduce((acc, app) => {
          acc[app.id] = app;
          return acc;
        }, {} as Record<string, App>)
      );
    } catch (error) {
      console.error("Error fetching apps:", error);
    }
  }, [project, appConfigs]);

  useEffect(() => {
    updateAppConfigs();
  }, [updateAppConfigs]);

  useEffect(() => {
    updateAppsMap();
  }, [updateAppsMap]);

  return (
    <div>
      <div className="m-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">App Configurations</h1>
        </div>
        <Button className="bg-primary hover:bg-primary/90 text-white">
          <GoPlus />
          Add App
        </Button>
      </div>
      <Separator />

      <div className="m-4">
        <AppConfigsTable appConfigs={appConfigs} appsMap={appsMap} />
      </div>
    </div>
  );
}
