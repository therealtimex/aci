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
import { type AppFunction } from "@/lib/types";
import { useEffect, useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { dummyFunctions } from "@/lib/dummyData";

interface AppFunctionsTableProps {
  appId: string;
}

export function AppFunctionsTable({ appId }: AppFunctionsTableProps) {
  const [functions, setFunctions] = useState<AppFunction[]>([]);
  // TODO: fetch functions from backend with app id
  const [selectedCategory, setSelectedCategory] = useState("all"); // eslint-disable-line
  const [selectedTag, setSelectedTag] = useState("all"); // eslint-disable-line

  useEffect(() => {
    setFunctions(dummyFunctions);
  }, [appId]);

  const categories = Array.from(
    new Set(dummyFunctions.flatMap((func) => func.categories || []))
  );
  const tags = Array.from(
    new Set(dummyFunctions.flatMap((func) => func.tags || []))
  );

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <Select onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-[120px]">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            {["all", ...categories].map((category) => (
              <SelectItem key={category} value={category}>
                {category}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select onValueChange={setSelectedTag}>
          <SelectTrigger className="w-[80px]">
            <SelectValue placeholder="Tags" />
          </SelectTrigger>
          <SelectContent>
            {["all", ...tags].map((tag) => (
              <SelectItem key={tag} value={tag}>
                {tag}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader className="bg-gray-100">
            <TableRow>
              <TableHead>FUNCTION NAME</TableHead>
              <TableHead>FUNCTION ID</TableHead>
              <TableHead className="max-w-[500px]">DESCRIPTION</TableHead>
              <TableHead className="text-right">ACTIONS</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {functions.map((func) => (
              <TableRow key={func.id}>
                <TableCell className="font-medium">{func.name}</TableCell>
                <TableCell>{func.functionId}</TableCell>
                <TableCell className="max-w-[500px]">
                  {func.description}
                </TableCell>
                <TableCell className="text-right">
                  <Button variant="outline" size="sm">
                    See Details
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
