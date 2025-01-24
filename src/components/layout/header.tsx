"use client";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
} from "@/components/ui/breadcrumb";
import { GoBell } from "react-icons/go";
import { BsQuestionCircle } from "react-icons/bs";
import { Separator } from "@/components/ui/separator";

export const Header = () => {
  return (
    <div>
      <div className="flex w-full items-center justify-between px-4 py-2">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="/">Dashboard</BreadcrumbLink>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

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
