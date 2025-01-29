"use client";

import { AppConfigsTable } from "@/components/apps/app-configs-table";
import { useProject } from "@/components/context/project";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { dummyAppConfigs } from "@/lib/dummyData";
import { AppConfig } from "@/lib/types";
import { useEffect, useState } from "react";
import { GoPlus } from "react-icons/go";

export default function AppConfigPage() {
  const { project } = useProject();

  const [appConfigs, setAppConfigs] = useState<AppConfig[]>([]);

  useEffect(() => {
    // TODO: fetch app configurations from backend with app id
    setAppConfigs(dummyAppConfigs);
  }, [project?.id]);

  return (
    <div>
      <div className="m-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">App Configurations</h1>
        </div>
        <Button className="bg-teal-400 text-black hover:bg-teal-500">
          <GoPlus />
          Add App
        </Button>
      </div>
      <Separator />

      <div className="m-4">
        <AppConfigsTable appConfigs={appConfigs} />
      </div>
    </div>
  );
}
