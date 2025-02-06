import { AppConfig } from "@/lib/types/appconfig";

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
