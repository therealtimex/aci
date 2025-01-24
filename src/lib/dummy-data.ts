export interface App {
  id: string;
  name: string;
  icon: string;
  description: string;
  categories: string[];
  tags: string[];
}

export interface AppFunction {
  id: string;
  name: string;
  functionId: string;
  description: string;
}

export const dummyApps: App[] = [
  {
    id: "slack",
    name: "Slack",
    icon: "/globe.svg",
    description: "Slack is a channel-based messaging platform.",
    categories: ["Productivity"],
    tags: ["Collaboration"],
  },
  {
    id: "salesforce",
    name: "Salesforce",
    icon: "/window.svg",
    description: "Salesforce is a customer relationship management solution.",
    categories: ["CRM"],
    tags: [],
  },
  {
    id: "hubspot",
    name: "HubSpot",
    icon: "/file.svg",
    description: "HubSpot is a developer and marketer of software products for inbound marketing, sales, and customer service.",
    categories: ["CRM", "Marketing"],
    tags: [],
  },
  {
    id: "github",
    name: "GitHub",
    icon: "/globe.svg",
    description: "A platform for version control and collaboration",
    categories: ["Dev-tools"],
    tags: ["Collaboration"],
  },
  {
    id: "jira",
    name: "Jira",
    icon: "/window.svg",
    description: "A tool for bug tracking, issue tracking, and agile project management.",
    categories: ["Productivity", "Ticketing"],
    tags: [],
  },
  {
    id: "gmail",
    name: "Gmail",
    icon: "/file.svg",
    description: "Connect to Gmail to send and manage emails.",
    categories: ["Productivity", "Email"],
    tags: [],
  }
];

export const dummyAppFunctions: AppFunction[] = [
  {
    id: "1",
    name: "Jira Feature 1",
    functionId: "#WE785",
    description: "Ut enim ad minim veniam, quis nostrud exercita...",
  },
  {
    id: "2",
    name: "Jira Feature 2",
    functionId: "#WE785",
    description: "Ut enim ad minim veniam, quis nostrud exercita...",
  },
];
