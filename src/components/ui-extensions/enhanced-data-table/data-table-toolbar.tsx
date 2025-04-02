"use client";

import { Table } from "@tanstack/react-table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import { useState } from "react";

interface EnhancedDataTableToolbarProps<TData> {
  table: Table<TData>;
  placeholder?: string;
  showSearchInput?: boolean;
}

export function EnhancedDataTableToolbar<TData>({
  table,
  placeholder = "Search...",
  showSearchInput,
}: EnhancedDataTableToolbarProps<TData>) {
  const [searchValue, setSearchValue] = useState("");

  const handleSearch = (value: string) => {
    setSearchValue(value);
    table.setGlobalFilter(value);
  };

  const isFiltered = table.getState().globalFilter ? true : false;

  return (
    <div className="flex items-center justify-between py-4">
      {showSearchInput && (
        <div className="flex flex-1 items-center space-x-2">
          <Input
            placeholder={placeholder}
            value={searchValue}
            onChange={(event) => handleSearch(event.target.value)}
            className="h-8 w-[250px]"
          />
          {isFiltered && (
            <Button
              variant="ghost"
              onClick={() => handleSearch("")}
              className="h-8 px-2 lg:px-3"
            >
              Clear
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      )}
    </div>
  );
}
