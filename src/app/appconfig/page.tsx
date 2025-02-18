"use client";

// import { Button } from "@/components/ui/button";
import { useCallback, useEffect, useState } from "react";
// import { GoPlus } from "react-icons/go";
import { AppConfig } from "@/lib/types/appconfig";
import { Separator } from "@/components/ui/separator";
import { AppConfigsTable } from "@/components/appconfig/app-configs-table";
import { useProject } from "@/components/context/project";
import { getApiKey } from "@/lib/api/util";
import { getAllAppConfigs } from "@/lib/api/appconfig";

export default function AppConfigPage() {
  const [appConfigs, setAppConfigs] = useState<AppConfig[]>([]);

  const { project } = useProject();

  const loadAppConfigs = useCallback(async () => {
    if (!project) {
      console.warn("No active project");
      return;
    }
    const apiKey = getApiKey(project);

    const appConfigs = await getAllAppConfigs(apiKey);
    setAppConfigs(appConfigs);
  }, [project]);

  useEffect(() => {
    loadAppConfigs();
  }, [project, loadAppConfigs]);


  return (
    <div>
      <div className="m-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">App Configurations</h1>
        </div>
        {/* <Button className="bg-primary hover:bg-primary/90 text-white">
          <GoPlus />
          Add App
        </Button> */}
      </div>
      <Separator />

      <div className="m-4">
        <AppConfigsTable
          appConfigs={appConfigs}
          updateAppConfigs={loadAppConfigs}
        />
      </div>
    </div>
  );
}
