"use client";

import { FunctionDetail } from "@/components/apps/function-detail";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { type AppFunction } from "@/lib/types/appfunction";
import { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { IdDisplay } from "./id-display";

interface AppFunctionsTableProps {
  functions: AppFunction[];
}

export function AppFunctionsTable({ functions }: AppFunctionsTableProps) {
  // const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedTag, setSelectedTag] = useState("all");

  // const categories = Array.from(
  //   new Set(functions.flatMap((func) => func.categories || []))
  // );
  const tags = Array.from(
    new Set(functions.flatMap((func) => func.tags || [])),
  );

  const filteredFunctions = functions.filter((func) => {
    // const matchesCategory = selectedCategory === "all" || (func.categories && func.categories.includes(selectedCategory));
    const matchesTag =
      selectedTag === "all" || (func.tags && func.tags.includes(selectedTag));
    return matchesTag; // && matchesCategory
  });

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        {/* <Select onValueChange={setSelectedCategory}>
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
        </Select> */}

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
              <TableHead className="max-w-[500px]">DESCRIPTION</TableHead>
              <TableHead className="text-center">ACTIONS</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredFunctions.map((func) => (
              <TableRow key={func.id}>
                <TableCell className="font-medium">
                  <IdDisplay id={func.name} dim={false} />
                </TableCell>
                <TableCell className="max-w-[500px]">
                  {func.description}
                </TableCell>
                <TableCell className="text-center">
                  <FunctionDetail func={func} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
