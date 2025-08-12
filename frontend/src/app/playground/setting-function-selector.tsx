"use client";

import { useState } from "react";
import { Code, Check, Loader2, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { useAgentStore } from "@/lib/store/agent";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";
import { BsQuestionCircle } from "react-icons/bs";
import { useShallow } from "zustand/react/shallow";

const MAX_FUNCTIONS =
  Number(process.env.NEXT_PUBLIC_AGENT_MAX_FUNCTIONS) || 100;

export function FunctionMultiSelector() {
  const [open, setOpen] = useState(false);

  const {
    selectedFunctions,
    setSelectedFunctions,
    getAvailableAppFunctions,
    loadingFunctions,
  } = useAgentStore(
    useShallow((state) => ({
      selectedFunctions: state.selectedFunctions,
      setSelectedFunctions: state.setSelectedFunctions,
      getAvailableAppFunctions: state.getAvailableAppFunctions,
      loadingFunctions: state.loadingFunctions,
    })),
  );
  const appFunctions = getAvailableAppFunctions();
  const availableFunctionNames = appFunctions.map((func) => func.name);
  const allSelected =
    availableFunctionNames.length > 0 &&
    selectedFunctions.length === availableFunctionNames.length;

  const handleFunctionChange = (functionName: string) => {
    if (selectedFunctions.includes(functionName)) {
      setSelectedFunctions(
        selectedFunctions.filter((name) => name !== functionName),
      );
    } else {
      if (selectedFunctions.length >= MAX_FUNCTIONS) {
        toast.error(
          `You can only select up to ${MAX_FUNCTIONS} functions at a time`,
        );
        return;
      }
      setSelectedFunctions([...selectedFunctions, functionName]);
    }
  };

  const handleSelectAll = () => {
    if (allSelected) {
      setSelectedFunctions([]);
    } else {
      if (availableFunctionNames.length > MAX_FUNCTIONS) {
        toast.error(
          `You can only select up to ${MAX_FUNCTIONS} functions. Cannot select all ${availableFunctionNames.length} functions.`,
        );
        return;
      }
      setSelectedFunctions(availableFunctionNames);
    }
  };

  return (
    <div className="space-y-2">
      <Tooltip>
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium">Functions</h3>
          <TooltipTrigger asChild>
            <BsQuestionCircle className="h-4 w-4 text-muted-foreground" />
          </TooltipTrigger>
        </div>
        <TooltipContent>
          <p>Select functions from selected apps.</p>
        </TooltipContent>
      </Tooltip>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            size="sm"
            className="w-full rounded-md h-8 bg-transparent border-input flex justify-start items-center hover:bg-accent hover:text-accent-foreground transition-colors px-3 h-9"
            aria-label={`Functions: ${selectedFunctions.length === 0 ? "All" : `${selectedFunctions.length} selected`}`}
          >
            <div className="flex items-center gap-3">
              <Code className="size-4 text-muted-foreground" />
              <span className="text-sm font-medium">Functions</span>
            </div>
            <div className="ml-auto">
              {loadingFunctions ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <>
                  {selectedFunctions.length > 0 ? (
                    <Badge className="size-4 px-1.5 flex items-center justify-center text-xs font-medium bg-primary text-primary-foreground">
                      {selectedFunctions.length}
                    </Badge>
                  ) : (
                    <Badge
                      variant="outline"
                      className="py-0.5 px-2 flex items-center justify-center text-xs font-medium"
                    >
                      None
                    </Badge>
                  )}
                </>
              )}
            </div>
            <ChevronsUpDown className="h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent
          className="w-auto min-w-[var(--radix-popover-trigger-width)] max-w-2xl p-0"
          align="end"
        >
          <Command className="rounded-lg shadow-md">
            <CommandInput placeholder="Search functions..." />
            <CommandList>
              <CommandEmpty>No functions found.</CommandEmpty>
              <CommandGroup>
                {loadingFunctions ? (
                  <div className="text-sm text-muted-foreground p-2">
                    Loading functions...
                  </div>
                ) : (
                  <>
                    {appFunctions.length > 0 && (
                      <CommandItem
                        key="select-all"
                        onSelect={handleSelectAll}
                        className="flex items-center gap-2"
                      >
                        <div className="flex items-center gap-2 flex-1">
                          <span>
                            {allSelected ? "Deselect All" : "Select All"}
                          </span>
                        </div>
                        <Check
                          className={cn(
                            "h-4 w-4 shrink-0 flex-shrink-0",
                            allSelected ? "opacity-100" : "opacity-0",
                          )}
                        />
                      </CommandItem>
                    )}
                    <div className="h-px bg-border my-1" />
                    {appFunctions.map((func) => (
                      <CommandItem
                        key={`function-${func.name}`}
                        value={func.name}
                        onSelect={() => handleFunctionChange(func.name)}
                        className="flex items-center gap-2"
                        data-value={func.name}
                      >
                        <div className="flex-1">
                          <span className="text-sm">{func.name}</span>
                        </div>
                        <Check
                          className={cn(
                            "h-4 w-4 shrink-0 flex-shrink-0",
                            selectedFunctions.includes(func.name)
                              ? "opacity-100"
                              : "opacity-0",
                          )}
                        />
                      </CommandItem>
                    ))}
                  </>
                )}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}
