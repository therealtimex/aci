"use client";

import React, { useEffect, useState, useCallback } from "react";
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

const AppPage = () => {
  const { appName } = useParams<{ appName: string }>();
  const { project } = useProject();
  const [app, setApp] = useState<App | null>(null);
  const [functions, setFunctions] = useState<AppFunction[]>([]);
  const [appConfig, setAppConfig] = useState<AppConfig | null>(null);

  const getApiKey = useCallback(() => {
    if (
      !project ||
      !project.agents ||
      project.agents.length === 0 ||
      !project.agents[0].api_keys ||
      project.agents[0].api_keys.length === 0
    ) {
      return null;
    }
    return project.agents[0].api_keys[0].key;
  }, [project]);

  const configureApp = async () => {
    const apiKey = getApiKey();
    if (!apiKey || !app) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/v1/app-configurations/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-API-KEY": apiKey,
          },
          body: JSON.stringify({
            app_name: appName,
            security_scheme: app.security_schemes[0],
            security_scheme_overrides: {},
            all_functions_enabled: true,
            enabled_functions: [],
          }),
        },
      );

      if (response.status === 409) {
        toast.error(
          `App configuration already exists for app: ${app.display_name}`,
        );
        return;
      }

      if (!response.ok) {
        throw new Error(`Failed to configure app`);
      }

      toast.success(`Successfully configured app: ${app.display_name}`);
    } catch (error) {
      console.error("Error configuring app:", error);
      toast.error(`Failed to configure app. Please try again.`);
    }
  };

  const updateApp = useCallback(async () => {
    const apiKey = getApiKey();
    if (!apiKey) return null;
    const params = new URLSearchParams();
    params.append("app_names", appName);

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/v1/apps/?${params.toString()}`,
      {
        method: "GET",
        headers: {
          "X-API-KEY": apiKey,
        },
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch app`);
    }

    const apps = await response.json();
    const app = apps[0];
    setApp(app);
    return app;
  }, [appName, getApiKey]);

  const updateFunctions = useCallback(async () => {
    const apiKey = getApiKey();
    if (!apiKey) return [];
    const params = new URLSearchParams();
    params.append("app_names", appName);

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/v1/functions/?${params.toString()}`,
      {
        method: "GET",
        headers: {
          "X-API-KEY": apiKey,
        },
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch functions`);
    }

    const functions = await response.json();
    setFunctions(functions);
    return functions;
  }, [appName, getApiKey]);

  const updateAppConfig = useCallback(async () => {
    const apiKey = getApiKey();
    if (!apiKey) return null;
    const params = new URLSearchParams();
    params.append("app_names", appName);

    const response = await fetch(
      `${
        process.env.NEXT_PUBLIC_API_URL
      }/v1/app-configurations/?${params.toString()}`,
      {
        method: "GET",
        headers: {
          "X-API-KEY": apiKey,
        },
      },
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch app configuration`);
    }

    const configs = await response.json();
    const config = configs.length > 0 ? configs[0] : null;
    setAppConfig(config);
    return config;
  }, [appName, getApiKey]);

  useEffect(() => {
    async function loadData() {
      try {
        await Promise.all([updateApp(), updateFunctions(), updateAppConfig()]);
      } catch (error) {
        console.error("Error fetching app data:", error);
      }
    }

    loadData();
  }, [appName, updateApp, updateAppConfig, updateFunctions, project]);

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
            await updateAppConfig();
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
