"use client";

import { useCallback, useEffect, useState } from "react";
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

export default function AppConfigDetailPage() {
  const { appId } = useParams<{ appId: string }>();
  const { project } = useProject();
  const [app, setApp] = useState<App | null>(null);
  const [linkedAccounts, setLinkedAccounts] = useState<LinkedAccount[]>([]);

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

  const updateApp = useCallback(async () => {
    const apiKey = getApiKey();
    if (!apiKey) return null;
    const params = new URLSearchParams();
    params.append("app_ids", appId);

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/v1/apps/?${params.toString()}`,
      {
        method: "GET",
        headers: {
          "X-API-KEY": apiKey,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch app`);
    }

    const apps = await response.json();
    const app = apps[0];
    setApp(app);
    return app;
  }, [appId, getApiKey]);

  const updateLinkedAccounts = useCallback(async () => {
    const apiKey = getApiKey();
    if (!apiKey) return null;
    const params = new URLSearchParams();
    params.append("app_ids", appId);

    const response = await fetch(
      `${
        process.env.NEXT_PUBLIC_API_URL
      }/v1/linked-accounts/?${params.toString()}`,
      {
        method: "GET",
        headers: {
          "X-API-KEY": apiKey,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch linked accounts`);
    }

    const linkedAccounts = await response.json();
    setLinkedAccounts(linkedAccounts);
  }, [appId, getApiKey]);

  useEffect(() => {
    updateApp();
    updateLinkedAccounts();
  }, [updateApp, updateLinkedAccounts]);

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
        <Button className="bg-primary hover:bg-primary/90 text-white">
          + Add Account
        </Button>
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
                  <TableHead>ACCOUNT OWNER</TableHead>
                  <TableHead>ACCOUNT ID</TableHead>
                  <TableHead>CREATED AT</TableHead>
                  <TableHead>ENABLED</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {linkedAccounts.map((account) => (
                  <TableRow key={account.id}>
                    <TableCell>
                      {/* TODO: show real owner name */}
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
                          D
                        </div>
                        Tom
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex-shrink-0 w-20">
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
