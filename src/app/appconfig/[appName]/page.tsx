"use client";

import { useEffect, useState } from "react";
import { LinkedAccount } from "@/lib/types/linkedaccount";
import Image from "next/image";
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
import { App } from "@/lib/types/app";
import { useProject } from "@/components/context/project";
import { AddAccountForm } from "@/components/appconfig/add-account";
import { getApiKey } from "@/lib/api/util";
import { getApp } from "@/lib/api/app";
import { getLinkedAccounts } from "@/lib/api/linkedaccount";

export default function AppConfigDetailPage() {
  const { appName } = useParams<{ appName: string }>();
  const { project } = useProject();
  const [app, setApp] = useState<App | null>(null);
  const [linkedAccounts, setLinkedAccounts] = useState<LinkedAccount[]>([]);

  useEffect(() => {
    async function loadAppAndLinkedAccounts() {
      if (!project) {
        console.warn("No active project");
        return;
      }
      const apiKey = getApiKey(project);

      const app = await getApp(appName, apiKey);
      setApp(app);

      const linkedAccounts = await getLinkedAccounts(appName, apiKey);
      setLinkedAccounts(linkedAccounts);
    }
    loadAppAndLinkedAccounts();
  }, [project, appName]);

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="relative h-12 w-12 flex-shrink-0 overflow-hidden rounded-lg">
            {app && (
              <Image
                src={app?.logo ?? ""}
                alt={`${app?.display_name} logo`}
                fill
                className="object-cover"
              />
            )}
          </div>
          <div>
            <h1 className="text-2xl font-semibold">{app?.display_name}</h1>
            <IdDisplay id={app?.id ?? ""} />
          </div>
        </div>
        {app && (
          <AddAccountForm
            app={app}
            updateLinkedAccounts={async () => {
              if (!project) {
                console.warn("No active project");
                return;
              }
              const apiKey = getApiKey(project);

              const linkedAccounts = await getLinkedAccounts(appName, apiKey);
              setLinkedAccounts(linkedAccounts);
            }}
          />
        )}
      </div>

      <Tabs defaultValue={"linked"} className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="linked">Linked Accounts</TabsTrigger>
          {/* <TabsTrigger value="logs">Logs</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger> */}
        </TabsList>

        <TabsContent value="linked">
          <div className="rounded-md border">
            <Table>
              <TableHeader className="bg-gray-100">
                <TableRow>
                  <TableHead>ACCOUNT OWNER ID</TableHead>
                  <TableHead>CREATED AT</TableHead>
                  <TableHead>ENABLED</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {linkedAccounts.map((account) => (
                  <TableRow key={account.id}>
                    <TableCell>
                      <div className="flex-shrink-0">
                        <IdDisplay id={account.linked_account_owner_id} />
                      </div>
                    </TableCell>
                    <TableCell>{account.created_at}</TableCell>
                    <TableCell>
                      <Switch checked={account.enabled} />
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600"
                      >
                        <GoTrash />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TabsContent>

        {/* <TabsContent value="logs">
          <div className="text-gray-500">Logs content coming soon...</div>
        </TabsContent>

        <TabsContent value="settings">
          <div className="text-gray-500">Settings content coming soon...</div>
        </TabsContent> */}
      </Tabs>
    </div>
  );
}
