"use client";

import { useEffect, useState } from "react";
import { AppConfig } from "@/lib/types/appconfig";
import { dummyAppConfigs } from "@/lib/dummyData";
import { Button } from "@/components/ui/button";
import { IdDisplay } from "@/components/apps/id-display";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Switch } from "@/components/ui/switch";
import { GoTrash } from "react-icons/go";
import { useParams } from "next/navigation";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";


export default function AppConfigDetailPage() {
  const {configId} = useParams<{configId: string}>();
  const [appConfig, setAppConfig] = useState<AppConfig | null>(null);
  const defaultTab = "linked";

  useEffect(() => {
    async function fetchAppConfig() {
      try {
        // In a real app, this would be an API call
        const config = dummyAppConfigs.find((c) => c.id === configId);
        setAppConfig(config || null);
      } catch (error) {
        console.error("Error fetching app config:", error);
      }
    }

    fetchAppConfig();
  }, [configId]);

  if (!appConfig) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
            W
          </div>
          <div>
            <h1 className="text-2xl font-semibold">github</h1>
            <div className="flex-shrink-0 w-20">
              <IdDisplay id={appConfig.id} />
            </div>
          </div>
        </div>
        <Button className="bg-primary hover:bg-primary/90 text-white">
          + Add Account
        </Button>
      </div>

      <Tabs defaultValue={defaultTab} className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="linked">Linked Accounts</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="linked">
        <div className="rounded-md border">
          <Table>
            <TableHeader className="bg-gray-100">
              <TableRow>
                <TableHead>ACCOUNT OWNER</TableHead>
                <TableHead>ACCOUNT ID</TableHead>
                <TableHead>CREATED AT</TableHead>
                <TableHead>ENABLED</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
                      W
                    </div>
                    github
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex-shrink-0 w-20">
                    <IdDisplay id="abcd...efgh" />
                  </div>
                </TableCell>
                <TableCell>12</TableCell>
                <TableCell>
                  <Switch checked={true} />
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm" className="text-red-600">
                    <GoTrash />
                  </Button>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
                      W
                    </div>
                    google
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex-shrink-0 w-20">
                    <IdDisplay id="zxcv...xawe" />
                  </div>
                </TableCell>
                <TableCell>5</TableCell>
                <TableCell>
                  <Switch checked={true} />
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm" className="text-red-600">
                    <GoTrash />
                  </Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
        </TabsContent>

        <TabsContent value="logs">
          <div className="text-gray-500">Logs content coming soon...</div>
        </TabsContent>

        <TabsContent value="settings">
          <div className="text-gray-500">Settings content coming soon...</div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
