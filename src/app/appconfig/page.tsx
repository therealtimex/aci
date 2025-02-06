"use client";

import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { GoPlus } from "react-icons/go";
import { AppConfig } from "@/lib/types/appconfig";
import { dummyAppConfigs } from "@/lib/dummyData";
import { Separator } from "@/components/ui/separator";
import { AppConfigsTable } from "@/components/apps/app-configs-table";

export default function AppConfigPage() {
  const [appConfigs, setAppConfigs] = useState<AppConfig[]>([]);

  useEffect(() => {
    async function fetchAppConfigs() {
      try {
        setAppConfigs(dummyAppConfigs);
      } catch (error) {
        console.error("Error fetching app configs:", error);
      }
    }

    fetchAppConfigs();
  }, []);

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
        <AppConfigsTable appConfigs={appConfigs} />
      </div>
    </div>
  );
}
