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
import { Switch } from "@/components/ui/switch";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { IdDisplay } from "../apps/id-display";
import { GoTrash } from "react-icons/go";
import { App } from "@/lib/types/app";

interface AppConfigsTableProps {
  appConfigs: AppConfig[];
  appsMap: Record<string, App>;
}

export function AppConfigsTable({ appConfigs, appsMap }: AppConfigsTableProps) {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  const filteredAppConfigs = appConfigs.filter((config) =>
    config.id.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex-1 flex items-center space-x-4">
          <Input
            placeholder="Search keyword, category, etc."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-sm"
          />
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="development">Development</SelectItem>
              <SelectItem value="productivity">Productivity</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader className="bg-gray-100">
            <TableRow>
              <TableHead>APP NAME</TableHead>
              <TableHead>APP ID</TableHead>
              <TableHead>LINKED ACCOUNTS</TableHead>
              <TableHead>ENABLED</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAppConfigs.map((config) => (
              <TableRow key={config.id}>
                <TableCell>{appsMap[config.app_name]?.display_name}</TableCell>
                <TableCell>
                  <div className="flex-shrink-0 w-20">
                    <IdDisplay id={appsMap[config.app_name]?.id} />
                  </div>
                </TableCell>
                <TableCell>
                  10
                  {/* TODO: query backend to display read linked accounts number */}
                </TableCell>
                <TableCell>
                  <Switch checked={config.enabled} />
                </TableCell>
                <TableCell className="space-x-2 flex">
                  <Link href={`/appconfig/${config.app_name}`}>
                    <Button variant="outline" size="sm">
                      Open
                    </Button>
                  </Link>
                  <Button variant="ghost" size="sm" className="text-red-600">
                    <GoTrash />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
