"use client";

import React, { useEffect, useState } from "react";
import {
  useAppFunctionsColumns,
  useAppFunctionsTableState,
} from "@/components/apps/useAppFunctionsColumns";
import { Separator } from "@/components/ui/separator";
import { useParams } from "next/navigation";
import { IdDisplay } from "@/components/apps/id-display";
import { Button } from "@/components/ui/button";
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
import { EnhancedDataTable } from "@/components/ui-extensions/enhanced-data-table/data-table";
import { useMetaInfo } from "@/components/context/metainfo";

const AppPage = () => {
  const { appName } = useParams<{ appName: string }>();
  const { activeProject } = useMetaInfo();
  const [app, setApp] = useState<App | null>(null);
  const [functions, setFunctions] = useState<AppFunction[]>([]);
  const [appConfig, setAppConfig] = useState<AppConfig | null>(null);

  const columns = useAppFunctionsColumns();
  const { setTableInstance, tagFilterComponent } =
    useAppFunctionsTableState(functions);

  const configureApp = async (security_scheme: string) => {
    const apiKey = getApiKey(activeProject);
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
        const apiKey = getApiKey(activeProject);

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
  }, [appName, activeProject]);

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
        </div>
      </div>
      <Separator />

      <div className="m-4">
        <EnhancedDataTable
          columns={columns}
          data={functions}
          searchBarProps={{ placeholder: "Search functions..." }}
          filterComponent={tagFilterComponent}
          defaultSorting={[{ id: "name", desc: false }]}
          onTableCreated={setTableInstance}
        />
      </div>
    </div>
  );
};

export default AppPage;
