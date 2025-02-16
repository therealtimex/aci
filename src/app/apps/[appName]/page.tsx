"use client";

import React, { useEffect, useState } from "react";
import { AppFunctionsTable } from "@/components/apps/app-functions-table";
import { Separator } from "@/components/ui/separator";
import { useParams } from "next/navigation";
import { IdDisplay } from "@/components/apps/id-display";
import { Button } from "@/components/ui/button";
import { useProject } from "@/components/context/project";
import { type AppFunction } from "@/lib/types/appfunction";
import { type App } from "@/lib/types/app";
import { toast } from "sonner";
import { AppConfig } from "@/lib/types/appconfig";
import { getApiKey } from "@/lib/api/util";
import { getApp } from "@/lib/api/app";
import { getFunctionsForApp } from "@/lib/api/appfunction";
import {
  AppAlreadyConfiguredError,
  createAppConfig,
  getAppConfig,
} from "@/lib/api/appconfig";

const AppPage = () => {
  const { appName } = useParams<{ appName: string }>();
  const { project } = useProject();
  const [app, setApp] = useState<App | null>(null);
  const [functions, setFunctions] = useState<AppFunction[]>([]);
  const [appConfig, setAppConfig] = useState<AppConfig | null>(null);

  const configureApp = async () => {
    if (!project) {
      throw new Error("No API key available");
    }

    const apiKey = getApiKey(project);
    if (!app) return;

    try {
      await createAppConfig(appName, app.security_schemes[0], apiKey);
      toast.success(`Successfully configured app: ${app.display_name}`);
    } catch (error) {
      if (error instanceof AppAlreadyConfiguredError) {
        toast.error(
          `App configuration already exists for app: ${app.display_name}`,
        );
      } else {
        console.error("Error configuring app:", error);
        toast.error(`Failed to configure app. Please try again.`);
      }
    }
  };

  useEffect(() => {
    async function loadData() {
      try {
        if (!project) {
          console.warn("No active project");
          return;
        }

        const apiKey = getApiKey(project);

        const app = await getApp(appName, apiKey);
        setApp(app);

        const functions = await getFunctionsForApp(appName, apiKey);
        setFunctions(functions);

        const appConfig = await getAppConfig(appName, apiKey);
        setAppConfig(appConfig);
      } catch (error) {
        console.error("Error fetching app data:", error);
      }
    }

    loadData();
  }, [appName, project]);

  return (
    <div>
      <div className="m-4 flex items-center justify-between">
        <div>
          {app && (
            <>
              <h1 className="text-2xl font-bold">{app.display_name}</h1>
              <IdDisplay id={app.id} />
            </>
          )}
        </div>
        <Button
          className="bg-primary text-white hover:bg-primary/90"
          onClick={async () => {
            await configureApp();
            if (!project) {
              throw new Error("No active project");
            }

            const apiKey = getApiKey(project);
            const appConfig = await getAppConfig(appName, apiKey);
            setAppConfig(appConfig);
          }}
          disabled={appConfig !== null}
        >
          {appConfig ? "Configured" : "Configure App"}
        </Button>
      </div>
      <Separator />

      <div className="m-4">
        <AppFunctionsTable functions={functions} />
      </div>
    </div>
  );
};

export default AppPage;
