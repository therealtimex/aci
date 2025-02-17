"use client";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

import { GoBell } from "react-icons/go";
import { BsQuestionCircle } from "react-icons/bs";
import { Separator } from "@/components/ui/separator";
import { BreadcrumbLinks } from "./BreadcrumbLinks";
import { usePathname } from "next/navigation";

export const Header = () => {
  const pathname = usePathname();

  return (
    <div>
      <div className="flex w-full items-center justify-between px-4 py-2">
        <BreadcrumbLinks pathname={pathname} />

        <Input
          placeholder="Search keyword, category, etc."
          className="mx-2 w-80"
        />

        <div className="flex items-center">
          <Button variant="outline" className="px-2 mx-2">
            <GoBell />
          </Button>
          <Button variant="outline" className="px-2">
            <BsQuestionCircle />
            <span>Support</span>
          </Button>
        </div>
      </div>
      <Separator />
    </div>
  );
};
