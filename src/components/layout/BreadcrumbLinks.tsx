"use client";

import Link from "next/link";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "../ui/breadcrumb";

interface BreadcrumbLinksProps {
  pathname: string;
}

export const BreadcrumbLinks = ({ pathname }: BreadcrumbLinksProps) => {
  const segments = pathname.split("/").filter(Boolean);
  let cumulativePath = "";
  const breadcrumbs = segments.map((segment) => {
    cumulativePath += "/" + segment;
    return { label: segment.toUpperCase(), href: cumulativePath };
  });

  const breadcrumbsList = [];

  for (let i = 0; i < breadcrumbs.length; i++) {
    if (i > 0) {
      breadcrumbsList.push(<BreadcrumbSeparator key={i * 2 - 1} />);
    }

    breadcrumbsList.push(
      <BreadcrumbItem key={i * 2}>
        <Link href={breadcrumbs[i].href}>{breadcrumbs[i].label}</Link>
      </BreadcrumbItem>,
    );
  }

  return (
    <Breadcrumb>
      <BreadcrumbList>
        {breadcrumbs.length > 0 ? (
          breadcrumbsList
        ) : (
          <BreadcrumbItem>
            <BreadcrumbLink href="/">Home</BreadcrumbLink>
          </BreadcrumbItem>
        )}
      </BreadcrumbList>
    </Breadcrumb>
  );
};
