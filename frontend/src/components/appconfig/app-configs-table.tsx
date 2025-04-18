"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { type AppConfig } from "@/lib/types/appconfig";
import { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { IdDisplay } from "@/components/apps/id-display";
import { GoTrash } from "react-icons/go";
import { App } from "@/lib/types/app";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { deleteAppConfig, updateAppConfig } from "@/lib/api/appconfig";
import { getApiKey } from "@/lib/api/util";

import Image from "next/image";
import { EnhancedSwitch } from "@/components/ui-extensions/enhanced-switch/enhanced-switch";
import { useMetaInfo } from "@/components/context/metainfo";
interface AppConfigsTableProps {
  appConfigs: AppConfig[];
  appsMap: Record<string, App>;
  linkedAccountsCountMap: Record<string, number>;
  updateAppConfigs: () => void;
}

export function AppConfigsTable({
  appConfigs,
  appsMap,
  linkedAccountsCountMap,
  updateAppConfigs,
}: AppConfigsTableProps) {
  const { activeProject } = useMetaInfo();

  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  const categories = Array.from(
    new Set(Object.values(appsMap).flatMap((app) => app.categories)),
  );

  // Sort app configurations by app name
  const sortedAppConfigs = [...appConfigs].sort((a, b) =>
    a.app_name.localeCompare(b.app_name),
  );

  const filteredAppConfigs = sortedAppConfigs.filter((config) => {
    // If the app doesn't exist in appsMap, only match by app_name
    if (!appsMap[config.app_name]) {
      return config.app_name.toLowerCase().includes(searchQuery.toLowerCase());
    }

    const matchesNameAndCategory =
      config.app_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      appsMap[config.app_name]?.categories?.some((c) =>
        c.toLowerCase().includes(searchQuery.toLowerCase()),
      );

    const matchesCategory =
      selectedCategory === "all" ||
      appsMap[config.app_name]?.categories?.includes(selectedCategory);

    return matchesNameAndCategory && matchesCategory;
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex-1 flex items-center space-x-4">
          <Input
            placeholder="Search by app name or category"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-sm"
          />
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="all" />
            </SelectTrigger>
            <SelectContent>
              {["all", ...categories].map((category) => (
                <SelectItem key={category} value={category}>
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader className="bg-gray-100">
            <TableRow>
              <TableHead>APP NAME</TableHead>
              <TableHead>LINKED ACCOUNTS</TableHead>
              <TableHead>ENABLED</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAppConfigs.map((config) => (
              <TableRow key={config.id}>
                <TableCell>
                  <div className="flex items-center gap-3">
                    <div className="relative h-5 w-5 flex-shrink-0 overflow-hidden">
                      {appsMap[config.app_name]?.logo && (
                        <Image
                          src={appsMap[config.app_name]?.logo || ""}
                          alt={`${config.app_name} logo`}
                          fill
                          className="object-contain"
                        />
                      )}
                    </div>
                    <IdDisplay id={config.app_name} dim={false} />
                  </div>
                </TableCell>
                <TableCell>
                  {linkedAccountsCountMap[config.app_name] || 0}
                </TableCell>
                <TableCell>
                  <EnhancedSwitch
                    checked={config.enabled}
                    onAsyncChange={async (checked) => {
                      try {
                        const apiKey = getApiKey(activeProject);
                        await updateAppConfig(config.app_name, checked, apiKey);
                        return true;
                      } catch (error) {
                        console.error("Failed to update app config:", error);
                        return false;
                      }
                    }}
                    successMessage={(newState) => {
                      return `${config.app_name} configurations ${newState ? "enabled" : "disabled"}`;
                    }}
                    errorMessage="Failed to update app configuration"
                  />
                </TableCell>
                <TableCell className="space-x-2 flex">
                  <Link href={`/appconfigs/${config.app_name}`}>
                    <Button variant="outline" size="sm">
                      Open
                    </Button>
                  </Link>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600"
                      >
                        <GoTrash />
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Confirm Deletion?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This action cannot be undone. This will permanently
                          delete the app configuration for &quot;
                          {config.app_name}&quot; and remove all the linked
                          accounts for this app.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={async () => {
                            try {
                              const apiKey = getApiKey(activeProject);

                              await deleteAppConfig(config.app_name, apiKey);
                              updateAppConfigs();
                            } catch (error) {
                              console.error(error);
                            }
                          }}
                        >
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
