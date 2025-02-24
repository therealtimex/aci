import { AppFunction } from "@/lib/types/appfunction";

export async function getFunctionsForApp(
  appName: string,
  apiKey: string,
): Promise<AppFunction[]> {
  const params = new URLSearchParams();
  params.append("app_names", appName);

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/v1/functions?${params.toString()}`,
    {
      method: "GET",
      headers: {
        "X-API-KEY": apiKey,
      },
    },
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch functions: ${response.status} ${response.statusText}`,
    );
  }

  const functions = await response.json();
  return functions;
}
