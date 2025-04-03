"use client";

import { Column } from "@tanstack/react-table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface ColumnFilterProps<TData = unknown, TValue = unknown> {
  column:
    | {
        getFilterValue: () => string | unknown;
        setFilterValue: (value: string | undefined) => void;
      }
    | Column<TData, TValue>;
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
  const selectedValue = (column.getFilterValue() as string) || defaultOption;

  return (
    <Select
      value={selectedValue}
      onValueChange={(value) => {
        column.setFilterValue(value === defaultOption ? undefined : value);
      }}
    >
      <SelectTrigger className={width}>
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
