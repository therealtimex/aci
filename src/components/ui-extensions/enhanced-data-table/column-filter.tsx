"use client";

import { Column } from "@tanstack/react-table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useEffect, useState } from "react";
interface ColumnFilterProps<TData, TValue> {
  column: Column<TData, TValue>;
  options: string[];
  placeholder?: string;
  defaultOption?: string;
  defaultLabel?: string;
  width?: string;
}

export function ColumnFilter<TData, TValue>({
  column,
  options,
  placeholder = "Filter...",
  defaultOption = "",
  defaultLabel = "All",
  width = "w-[150px]",
}: ColumnFilterProps<TData, TValue>) {
  const [selectedValue, setSelectedValue] = useState(defaultOption);

  useEffect(() => {
    const filterValue = column.getFilterValue() as string;
    if (filterValue) {
      setSelectedValue(filterValue);
    }
  }, [column]);

  return (
    <Select
      value={selectedValue}
      onValueChange={(value) => {
        setSelectedValue(value);
        column.setFilterValue(value === defaultOption ? undefined : value);
      }}
    >
      <SelectTrigger className={`${width} h-8`}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value={defaultOption}>{defaultLabel}</SelectItem>
        {options.map((option) => (
          <SelectItem key={option} value={option}>
            {option}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
