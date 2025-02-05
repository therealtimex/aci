"use client";
import Link from "next/link";
import Image from "next/image";
// import { RiLinkUnlinkM } from "react-icons/ri";
import { GrAppsRounded } from "react-icons/gr";
import { cn } from "@/lib/utils";

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
  useSidebar,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { ProjectSelector } from "./project-selector";
import { PiStorefront } from "react-icons/pi";
import { GoHome } from "react-icons/go";
import { RiSettings4Line } from "react-icons/ri";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

export function AppSidebar() {
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";

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
    // {
    //   title: "Linked Accounts",
    //   url: `/linked-accounts`,
    //   icon: RiLinkUnlinkM,
    // },
  ];

  return (
    <Sidebar variant="inset" collapsible="icon" className="flex flex-col">
      <SidebarHeader>
        <div className={cn(
          "flex items-center p-4",
          isCollapsed ? "justify-center" : "justify-between gap-2"
        )}>
          {!isCollapsed && (
            <div className="h-8 w-auto relative">
              <Image
                src="/logo.svg"
                alt="Aipotheosis Labs Logo"
                width={150}
                height={30}
                priority
                className="object-contain"
              />
            </div>
          )}
          <SidebarTrigger />
        </div>
        <Separator />
        <div className={cn(
          "transition-all duration-200 overflow-hidden",
          isCollapsed 
            ? "max-h-0 opacity-0 scale-95" 
            : "max-h-[100px] opacity-100 scale-100"
        )}>
          <div className="w-full p-4">
            <ProjectSelector />
          </div>
          <Separator />
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <SidebarMenuButton asChild>
                        <Link 
                          href={item.url} 
                          className={cn(
                            "flex items-center gap-3 px-4 py-2",
                            isCollapsed && "justify-center"
                          )}
                        >
                          <item.icon className="h-5 w-5 flex-shrink-0" />
                          {!isCollapsed && <span>{item.title}</span>}
                        </Link>
                      </SidebarMenuButton>
                    </TooltipTrigger>
                    {isCollapsed && (
                      <TooltipContent side="right">
                        {item.title}
                      </TooltipContent>
                    )}
                  </Tooltip>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <Separator />
        <Link
          href="/account" 
          className={cn(
            "flex items-center gap-3 p-4",
            isCollapsed && "justify-center"
          )}
        >
          <RiSettings4Line className="h-5 w-5 flex-shrink-0" />
          {!isCollapsed && <span>Account Settings</span>}
        </Link>
      </SidebarFooter>
    </Sidebar>
  );
}
