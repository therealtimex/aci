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
import { useProject } from "@/components/context/project";
import { Skeleton } from "../ui/skeleton";
// import { GoPlus } from "react-icons/go";
import { RiSettings3Line } from "react-icons/ri";
import { useUser } from "@/components/context/user";
import { Project } from "@/lib/types/project";
import Link from "next/link";
import { getProjects } from "@/lib/api/project";

interface ProjectSelectOption {
  value: string; // project id
  label: string; // project name
}

export function ProjectSelector() {
  const { user } = useUser();
  const { project, setProject } = useProject();
  const [projects, setProjects] = useState<Map<string, Project>>(new Map());
  const [projectSelectOptions, setProjectSelectOptions] = useState<
    ProjectSelectOption[]
  >([]);

  const [open, setOpen] = useState(false);

  useEffect(() => {
    async function loadProjects() {
      if (!user) {
        return;
      }

      try {
        const retrievedProjects = await getProjects(user.accessToken);

        setProjects(new Map(retrievedProjects.map((p) => [p.id, p])));
        if (!project && retrievedProjects.length > 0) {
          // TODO: there will be multiple projects in a future release
          setProject(retrievedProjects[0]);
        }
      } catch (error) {
        console.error("Error fetching projects:", error);
      }
    }

    loadProjects();
  }, [user, project, setProject, setProjects]);

  useEffect(() => {
    setProjectSelectOptions(
      Array.from(projects.values()).map((p) => ({
        value: p.id,
        label: p.name,
      })),
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
                  onSelect={() => {
                    const selectedProject = projects.get(option.value);
                    if (selectedProject) {
                      setProject(selectedProject);
                      setOpen(false);
                    } else {
                      console.error(`Project ${option.value} not found`);
                    }
                  }}
                >
                  {option.label}
                  <Check
                    className={cn(
                      "ml-auto",
                      project?.id === option.value
                        ? "opacity-100"
                        : "opacity-0",
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
            <CommandGroup>
              {/* <CommandItem>
                <GoPlus />
                <span>Create Project</span>
              </CommandItem> */}
              <Link href="/project-setting" onClick={() => setOpen(false)}>
                <CommandItem>
                  <RiSettings3Line />
                  <span>Manage Project</span>
                </CommandItem>
              </Link>
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
