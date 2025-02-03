"use client";

import React, { useEffect, useState } from "react";
import { AppFunctionsTable } from "@/components/apps/app-functions-table";
import { Separator } from "@/components/ui/separator";
import { useParams } from "next/navigation";
import { IdDisplay } from "@/components/apps/id-display";
import { Button } from "@/components/ui/button";
import { useProject } from "@/components/context/project";
import { type Function } from "@/lib/types/function";
import { type App } from "@/lib/types/app";

const AppPage = () => {
  const { appId } = useParams<{ appId: string }>();
  const { project } = useProject();
  const [app, setApp] = useState<App | null>(null);
  const [functions, setFunctions] = useState<Function[]>([]);

  useEffect(() => {
    async function fetchAppData() {
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
        const [appResponse, functionsResponse] = await Promise.all([
          fetch(`${process.env.NEXT_PUBLIC_API_URL}/v1/apps/${appId}`, {
            method: "GET",
            headers: {
              "X-API-KEY": project.agents[0].api_keys[0].key,
            },
          }),
          fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/v1/functions/?app_ids=${appId}`,
            {
              method: "GET",
              headers: {
                "X-API-KEY": project.agents[0].api_keys[0].key,
              },
            }
          ),
        ]);

        if (!appResponse.ok || !functionsResponse.ok) {
          throw new Error(`Failed to fetch app data`);
        }

        const [retrievedApp, retrievedFunctions] = await Promise.all([
          appResponse.json(),
          functionsResponse.json(),
        ]);

        setApp(retrievedApp);
        setFunctions(retrievedFunctions);
      } catch (error) {
        console.error("Error fetching app data:", error);
      }
    }

    fetchAppData();
  }, [appId, project]);

  return (
    <div>
      <div className="m-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{app?.name}</h1>
          <IdDisplay id={appId} />
        </div>
        <Button className="bg-teal-400 text-black hover:bg-teal-500">
          Configure App
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
