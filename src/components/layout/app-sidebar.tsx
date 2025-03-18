"use client";

import Link from "next/link";
import Image from "next/image";
// import { RiLinkUnlinkM } from "react-icons/ri";
import { GrAppsRounded } from "react-icons/gr";
import { cn } from "@/lib/utils";
import { usePathname } from "next/navigation";

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
// import { GoHome } from "react-icons/go";
import { RiSettings3Line, RiSettings4Line } from "react-icons/ri";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export function AppSidebar() {
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";
  const pathname = usePathname();

  const items = [
    // {
    //   title: "Home",
    //   url: `/`,
    //   icon: GoHome,
    // },
    {
      title: "App Store",
      url: `/apps`,
      icon: PiStorefront,
    },
    {
      title: "App Configurations",
      url: `/appconfigs`,
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
      <div className="w-full bg-black text-white text-center py-1 text-xs font-bold rounded-md">
        In Closed Beta
      </div>
      <SidebarHeader>
        <div
          className={cn(
            "flex items-center p-4",
            isCollapsed ? "justify-center" : "justify-between gap-2",
          )}
        >
          {!isCollapsed && (
            <div className="h-8 w-auto relative flex items-center justify-center">
              <Image
                src="/aci-dev-full-logo.svg"
                alt="ACI Dev Logo"
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
        <div
          className={cn(
            "transition-all duration-200 overflow-hidden",
            isCollapsed
              ? "max-h-0 opacity-0 scale-95"
              : "max-h-[100px] opacity-100 scale-100",
          )}
        >
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
              {items.map((item) => {
                const isActive =
                  pathname === item.url || pathname.startsWith(item.url);
                return (
                  <SidebarMenuItem key={item.title}>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <SidebarMenuButton asChild>
                          <Link
                            href={item.url}
                            className={cn(
                              "flex items-center gap-3 px-4 py-2 transition-colors",
                              isCollapsed && "justify-center",
                              isActive &&
                                "bg-primary/10 text-primary font-medium",
                            )}
                          >
                            <item.icon
                              className={cn(
                                "h-5 w-5 flex-shrink-0",
                                isActive && "text-primary",
                              )}
                            />
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
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <Tooltip>
              <TooltipTrigger asChild>
                <SidebarMenuButton asChild>
                  <Link
                    href="/project-setting"
                    className={cn(
                      "flex items-center gap-3 p-4 transition-colors",
                      isCollapsed && "justify-center",
                      pathname === "/project-setting" &&
                        "bg-primary/10 text-primary font-medium",
                    )}
                  >
                    <RiSettings3Line
                      className={cn(
                        "h-5 w-5 flex-shrink-0",
                        pathname === "/project-setting" && "text-primary",
                      )}
                    />
                    {!isCollapsed && <span>Manage Project</span>}
                  </Link>
                </SidebarMenuButton>
              </TooltipTrigger>
              {isCollapsed && (
                <TooltipContent side="right">Manage Project</TooltipContent>
              )}
            </Tooltip>
          </SidebarMenuItem>
        </SidebarMenu>

        <Separator />

        <SidebarMenu>
          <SidebarMenuItem>
            <Tooltip>
              <TooltipTrigger asChild>
                <SidebarMenuButton asChild>
                  <Link
                    href="/account"
                    className={cn(
                      "flex items-center gap-3 p-4 transition-colors",
                      isCollapsed && "justify-center",
                      pathname === "/account" &&
                        "bg-primary/10 text-primary font-medium",
                    )}
                  >
                    <RiSettings4Line
                      className={cn(
                        "h-5 w-5 flex-shrink-0",
                        pathname === "/account" && "text-primary",
                      )}
                    />
                    {!isCollapsed && <span>Account Settings</span>}
                  </Link>
                </SidebarMenuButton>
              </TooltipTrigger>
              {isCollapsed && (
                <TooltipContent side="right">Account Settings</TooltipContent>
              )}
            </Tooltip>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
