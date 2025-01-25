"use client";

import React from "react";
import { AppFunctionsTable } from "@/components/apps/app-functions-table";
import { Separator } from "@/components/ui/separator";
import { useParams } from "next/navigation";
import { dummyApps } from "@/lib/dummyData";
import { AppIdDisplay } from "@/components/apps/app-id-display";
import { Button } from "@/components/ui/button";

const AppPage = () => {
  const params = useParams<{ appId: string }>();

  return (
    <div>
      <div className="m-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            {dummyApps.find((app) => app.id === params.appId)?.name}
          </h1>
          <AppIdDisplay appId={params.appId} />
        </div>
        <Button className="bg-teal-400 text-black hover:bg-teal-500">
          Configure App
        </Button>
      </div>
      <Separator />

      <div className="m-4">
        <AppFunctionsTable appId={params.appId} />
      </div>
    </div>
  );
};

export default AppPage;
