"use client";

import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { GoPlus } from "react-icons/go";
import { AppConfig } from "@/lib/types/appconfig";
import { Separator } from "@/components/ui/separator";
import { AppConfigsTable } from "@/components/appconfig/app-configs-table";
import { useProject } from "@/components/context/project";
import { App } from "@/lib/types/app";
import { getApiKey } from "@/lib/api/util";
import { getAllAppConfigs } from "@/lib/api/appconfig";
import { getApps } from "@/lib/api/app";

export default function AppConfigPage() {
  const [appConfigs, setAppConfigs] = useState<AppConfig[]>([]);
  const [appsMap, setAppsMap] = useState<Record<string, App>>({});

  const { project } = useProject();

  useEffect(() => {
    async function loadAppConfigs() {
      if (!project) {
        console.warn("No active project");
        return;
      }
      const apiKey = getApiKey(project);

      const appConfigs = await getAllAppConfigs(apiKey);
      setAppConfigs(appConfigs);
    }
    loadAppConfigs();
  }, [project]);

  useEffect(() => {
    async function loadAppMaps() {
      if (!appConfigs) {
        return;
      }

      if (!project) {
        console.warn("No active project");
        return;
      }
      const apiKey = getApiKey(project);

      const apps = await getApps(
        appConfigs.map((config) => config.app_name),
        apiKey,
      );
      setAppsMap(
        apps.reduce(
          (acc, app) => {
            acc[app.name] = app;
            return acc;
          },
          {} as Record<string, App>,
        ),
      );
    }
    loadAppMaps();
  }, [project, appConfigs]);

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
