"use client";
import Link from "next/link";
import { RiLinkUnlinkM } from "react-icons/ri";
import { GrAppsRounded } from "react-icons/gr";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { ProjectSelector } from "./project-selector";
import { PiStorefront } from "react-icons/pi";
import { GoHome } from "react-icons/go";
import { RiSettings4Line } from "react-icons/ri";

import { useProject } from "@/components/context/project";

export function AppSidebar() {
  const { project } = useProject();
  console.log(project); // TODO:
  const items = [
    {
      title: "Home",
      url: `/`,
      icon: GoHome,
    },
    {
      title: "App Store",
      url: `/apps`,
      icon: PiStorefront,
    },
    {
      title: "App Configurations",
      url: `/appconfig`,
      icon: GrAppsRounded,
    },
    {
      title: "Linked Accounts",
      url: `/linked-accounts`,
      icon: RiLinkUnlinkM,
    },
  ];

  return (
    <Sidebar variant="inset" className="">
      <SidebarHeader >
        <div className="flex items-end w-full justify-between">
          Aipotheosis Labs
          <SidebarTrigger />
        </div>
        <Separator />
        <div className="w-full py-4">
          <ProjectSelector />
        </div>
        <Separator />
      </SidebarHeader>

      <SidebarContent >
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <Link href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="px-4">
        <Separator />
        <Link href="/settings" className="flex items-center gap-2 py-4">
          <RiSettings4Line />
          Account Settings
        </Link>
      </SidebarFooter>
    </Sidebar>
  );
}
