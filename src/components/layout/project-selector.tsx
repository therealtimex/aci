"use client";

import { Check, ChevronsUpDown } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { useEffect, useState } from "react";
import { Project, useProject } from "@/components/context/project";
import { Skeleton } from "../ui/skeleton";
import { GoPlus } from "react-icons/go";
import { RiSettings3Line } from "react-icons/ri";

interface ProjectSelectOption {
  value: string; // project id
  label: string; // project name
}

export function ProjectSelector() {
  const { project, setProject } = useProject();
  const [projects, setProjects] = useState<Map<string, Project>>(new Map());
  const [projectSelectOptions, setProjectSelectOptions] = useState<
    ProjectSelectOption[]
  >([]);

  const [open, setOpen] = useState(false);

  useEffect(() => {
    setProjects(
      new Map( // TODO: The array will be fetched from backend
        [
          {
            id: "1",
            name: "Default",
          },
          {
            id: "2",
            name: "Project 1",
          },
          {
            id: "3",
            name: "Project 2",
          },
        ].map((p) => [p.id, p])
      )
    );

    if (!project) {
      // TODO: the initial active project will be fetched from backend
      setProject({
        id: "1",
        name: "Default",
      });
    }
  }, [project, setProject, setProjects]);

  useEffect(() => {
    setProjectSelectOptions(
      Array.from(projects.values()).map((p) => ({
        value: p.id,
        label: p.name,
      }))
    );
  }, [projects]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between"
        >
          {project ? project.name : <Skeleton className="h-4 w-24" />}
          <ChevronsUpDown className="opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0">
        <Command>
          <CommandInput placeholder="Search project..." className="h-9" />
          <CommandList>
            <CommandEmpty>No project found.</CommandEmpty>
            <CommandGroup>
              {projectSelectOptions.map((option) => (
                <CommandItem
                  key={option.value}
                  value={option.value}
                  onSelect={(selectedProjectId) => {
                    setProject(projects.get(selectedProjectId)!);
                    setOpen(false);
                  }}
                >
                  {option.label}
                  <Check
                    className={cn(
                      "ml-auto",
                      project?.id === option.value ? "opacity-100" : "opacity-0"
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
            <CommandGroup>
              <CommandItem>
                <GoPlus />
                <span>Create Project</span>
              </CommandItem>
              <CommandItem>
                <RiSettings3Line />
                <span>Manage Project</span>
              </CommandItem>
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
