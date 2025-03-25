"use client";

import React, { useEffect, useState } from "react";
import { AppFunctionsTable } from "@/components/apps/app-functions-table";
import { Separator } from "@/components/ui/separator";
import { useParams } from "next/navigation";
import { IdDisplay } from "@/components/apps/id-display";
import { Button } from "@/components/ui/button";
import { useProject } from "@/components/context/project";
import { BsQuestionCircle } from "react-icons/bs";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";
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
import Image from "next/image";
import { ConfigureAppPopup } from "@/components/apps/configure-app-popup";

const AppPage = () => {
  const { appName } = useParams<{ appName: string }>();
  const { project } = useProject();
  const [app, setApp] = useState<App | null>(null);
  const [functions, setFunctions] = useState<AppFunction[]>([]);
  const [appConfig, setAppConfig] = useState<AppConfig | null>(null);

  const configureApp = async (security_scheme: string) => {
    if (!project) {
      throw new Error("No API key available");
    }

    const apiKey = getApiKey(project);
    if (!app) return;

    try {
      const appConfig = await createAppConfig(appName, security_scheme, apiKey);
      setAppConfig(appConfig);
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
            <div className="flex items-center gap-4">
              <div className="relative h-12 w-12 flex-shrink-0 overflow-hidden rounded-lg">
                <Image
                  src={app?.logo ?? ""}
                  alt={`${app?.display_name} logo`}
                  fill
                  className="object-contain"
                />
              </div>
              <div>
                <h1 className="text-2xl font-bold">{app.display_name}</h1>
                <IdDisplay id={app.name} />
              </div>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="cursor-pointer">
                <BsQuestionCircle className="h-4 w-4 text-muted-foreground" />
              </span>
            </TooltipTrigger>
            <TooltipContent side="top">
              <p className="text-xs">
                {appConfig
                  ? "The app has already been configured. It is ready for your agents to use."
                  : "Click to configure the application. This will add the application to your project, allowing your agents to use it."}
              </p>
            </TooltipContent>
          </Tooltip>
          {app && (
            <ConfigureAppPopup
              name={app.name}
              security_schemes={app.security_schemes}
              configureApp={configureApp}
            >
              <Button
                className="bg-primary text-white hover:bg-primary/90"
                disabled={appConfig !== null}
              >
                {appConfig ? "Configured" : "Configure App"}
              </Button>
            </ConfigureAppPopup>
          )}
        </div>
      </div>
      <Separator />

      <div className="m-4">
        <AppFunctionsTable functions={functions} />
      </div>
    </div>
  );
};

export default AppPage;
