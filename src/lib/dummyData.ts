import { App, AppFunction, AppConfig } from "./types";

export const dummyApps: App[] = [
  {
    id: "I78576",
    name: "Slack",
    icon: "/globe.svg",
    description: "Slack is a channel-based messaging platform.",
    categories: ["Productivity"],
    tags: ["Collaboration"],
  },
  {
    id: "I78577",
    name: "Salesforce",
    icon: "/window.svg",
    description: "Salesforce is a customer relationship management solution.",
    categories: ["CRM"],
    tags: [],
  },
  {
    id: "I78578",
    name: "HubSpot",
    icon: "/file.svg",
    description:
      "HubSpot is a developer and marketer of software products for inbound marketing, sales, and customer service.",
    categories: ["CRM", "Marketing"],
    tags: [],
  },
  {
    id: "I78579",
    name: "GitHub",
    icon: "/globe.svg",
    description: "A platform for version control and collaboration",
    categories: ["Dev-tools"],
    tags: ["Collaboration"],
  },
  {
    id: "I78580",
    name: "Jira",
    icon: "/window.svg",
    description:
      "A tool for bug tracking, issue tracking, and agile project management.",
    categories: ["Productivity", "Ticketing"],
    tags: [],
  },
  {
    id: "I78581",
    name: "Gmail",
    icon: "/file.svg",
    description: "Connect to Gmail to send and manage emails.",
    categories: ["Productivity", "Email"],
    tags: [],
  },
];

export const dummyFunctions: AppFunction[] = [
  {
    id: "1",
    name: "Jira Feature 1",
    functionId: "#WE785",
    description: "Ut enim ad minim veniam, quis nostrud exercita...",
    categories: ["Category 1", "Category 2"],
    tags: ["Tag 1", "Tag 2"],
  },
  {
    id: "2",
    name: "Jira Feature 2",
    functionId: "#WE785",
    description: "Ut enim ad minim veniam, quis nostrud exercita...",
    categories: ["Category 2", "Category 3"],
    tags: ["Tag 2", "Tag 3"],
  },
];

export const dummyAppConfigs: AppConfig[] = [
  {
    id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    project_id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    app_id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    security_scheme: "no_auth",
    security_scheme_overrides: {},
    enabled: true,
    all_functions_enabled: true,
    enabled_functions: [
      "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    ],
  },
  {
    id: "4fa85f64-5717-4562-b3fc-2c963f66afa7",
    project_id: "4fa85f64-5717-4562-b3fc-2c963f66afa7",
    app_id: "4fa85f64-5717-4562-b3fc-2c963f66afa7",
    security_scheme: "api_key",
    security_scheme_overrides: { "header": "X-API-KEY" },
    enabled: false,
    all_functions_enabled: false,
    enabled_functions: [],
  },
  {
    id: "5fa85f64-5717-4562-b3fc-2c963f66afa8",
    project_id: "5fa85f64-5717-4562-b3fc-2c963f66afa8",
    app_id: "5fa85f64-5717-4562-b3fc-2c963f66afa8",
    security_scheme: "oauth2",
    security_scheme_overrides: { "token_url": "https://example.com/token" },
    enabled: true,
    all_functions_enabled: false,
    enabled_functions: [
      "5fa85f64-5717-4562-b3fc-2c963f66afa8",
      "6fa85f64-5717-4562-b3fc-2c963f66afa9"
    ],
  },
  {
    id: "6fa85f64-5717-4562-b3fc-2c963f66afa9",
    project_id: "6fa85f64-5717-4562-b3fc-2c963f66afa9",
    app_id: "6fa85f64-5717-4562-b3fc-2c963f66afa9",
    security_scheme: "basic_auth",
    security_scheme_overrides: { "username_field": "user", "password_field": "pass" },
    enabled: false,
    all_functions_enabled: true,
    enabled_functions: [],
  }
];
