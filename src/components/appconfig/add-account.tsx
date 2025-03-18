"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { SubmitHandler, useForm } from "react-hook-form";
import * as z from "zod";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { BsQuestionCircle } from "react-icons/bs";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";
import { GoCopy, GoPlus } from "react-icons/go";
import { App } from "@/lib/types/app";
import { useProject } from "@/components/context/project";
import { toast } from "sonner";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useState } from "react";
import {
  createAPILinkedAccount,
  createNoAuthLinkedAccount,
  getOauth2LinkURL,
} from "@/lib/api/linkedaccount";
import { getApiKey } from "@/lib/api/util";

const formSchema = z
  .object({
    appName: z.string().min(1, "App name is required"),
    authType: z.enum(["api_key", "oauth2", "no_auth"]),
    linkedAccountOwnerId: z.string().min(1, "Account owner ID is required"),
    apiKey: z.string().optional(),
  })
  .refine(
    (data) =>
      data.authType !== "api_key" || (data.apiKey && data.apiKey.length > 0),
    {
      message: "API Key is required",
      path: ["apiKey"],
    },
  );

type FormValues = z.infer<typeof formSchema>;

interface AddAccountProps {
  app: App;
  updateLinkedAccounts: () => void;
}

const FORM_SUBMIT_COPY_OAUTH2_LINK_URL = "copyOAuth2LinkURL";
const FORM_SUBMIT_LINK_OAUTH2_ACCOUNT = "linkOAuth2";
const FORM_SUBMIT_API_KEY = "apiKey";
const FORM_SUBMIT_NO_AUTH = "noAuth";

export function AddAccountForm({ app, updateLinkedAccounts }: AddAccountProps) {
  const { project } = useProject();
  const [open, setOpen] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      appName: app.display_name,
      authType: app.security_schemes[0] as "api_key" | "oauth2" | "no_auth",
      linkedAccountOwnerId: "",
      apiKey: "",
    },
  });

  const authType = form.watch("authType");

  const fetchOath2LinkURL = async (
    linkedAccountOwnerId: string,
    afterOAuth2LinkRedirectURL?: string,
  ): Promise<string> => {
    if (!project) {
      throw new Error("No API key available");
    }

    const apiKey = getApiKey(project);

    if (afterOAuth2LinkRedirectURL === undefined) {
      return await getOauth2LinkURL(app.name, linkedAccountOwnerId, apiKey);
    } else {
      return await getOauth2LinkURL(
        app.name,
        linkedAccountOwnerId,
        apiKey,
        afterOAuth2LinkRedirectURL,
      );
    }
  };

  const copyOAuth2LinkURL = async (linkedAccountOwnerId: string) => {
    try {
      const url = await fetchOath2LinkURL(linkedAccountOwnerId);
      if (!navigator.clipboard) {
        console.error("Clipboard API not supported");
        toast.error("Your browser doesn't support copying to clipboard");
        return;
      }
      navigator.clipboard
        .writeText(url)
        .then(() => {
          toast.success("OAuth2 link URL copied to clipboard");
        })
        .catch((err) => {
          console.error("Failed to copy:", err);
          toast.error("Failed to copy OAuth2 Link URL to clipboard");
        });
    } catch (error) {
      console.error(error);
      toast.error("Failed to copy OAuth2 Link URL to clipboard");
    }
  };

  const linkOauth2Account = async (linkedAccountOwnerId: string) => {
    let oauth2LinkURL = "";
    try {
      oauth2LinkURL = await fetchOath2LinkURL(
        linkedAccountOwnerId,
        `${process.env.NEXT_PUBLIC_DEV_PORTAL_URL}/appconfigs/${app.name}`,
      );
      window.location.href = oauth2LinkURL;
    } catch (error) {
      console.error("Error linking OAuth2 account:", error);
      toast.error("Failed to link account");
    }
  };

  const linkAPIAccount = async (
    linkedAccountOwnerId: string,
    linkedAPIKey: string,
  ) => {
    if (!project) {
      throw new Error("No API key available");
    }

    const apiKey = getApiKey(project);

    try {
      await createAPILinkedAccount(
        app.name,
        linkedAccountOwnerId,
        linkedAPIKey,
        apiKey,
      );
      toast.success("Account linked successfully");
      form.reset();
      setOpen(false);
      updateLinkedAccounts();
    } catch (error) {
      console.error("Error linking API account:", error);
      toast.error("Failed to link account");
    }
  };

  const linkNoAuthAccount = async (linkedAccountOwnerId: string) => {
    if (!project) {
      throw new Error("No API key available");
    }

    const apiKey = getApiKey(project);

    try {
      await createNoAuthLinkedAccount(app.name, linkedAccountOwnerId, apiKey);
      toast.success("Account linked successfully");
      form.reset();
      setOpen(false);
      updateLinkedAccounts();
    } catch (error) {
      console.error("Error linking no auth account:", error);
      toast.error("Failed to link account");
    }
  };

  const onSubmit: SubmitHandler<FormValues> = async (values, e) => {
    if (!e) {
      throw new Error("Form submission event is not available");
    }

    const nativeEvent = e.nativeEvent as SubmitEvent;
    const submitter = nativeEvent.submitter as HTMLButtonElement;

    switch (submitter.name) {
      case FORM_SUBMIT_COPY_OAUTH2_LINK_URL:
        await copyOAuth2LinkURL(values.linkedAccountOwnerId);
        break;
      case FORM_SUBMIT_LINK_OAUTH2_ACCOUNT:
        await linkOauth2Account(values.linkedAccountOwnerId);
        break;
      case FORM_SUBMIT_API_KEY:
        await linkAPIAccount(
          values.linkedAccountOwnerId,
          values.apiKey as string,
        );
        break;
      case FORM_SUBMIT_NO_AUTH:
        await linkNoAuthAccount(values.linkedAccountOwnerId);
        break;
    }
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(open) => {
        setOpen(open);
        form.reset();
      }}
    >
      <div className="flex items-center gap-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="cursor-pointer">
              <BsQuestionCircle className="h-4 w-4 text-muted-foreground" />
            </span>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p className="text-xs">{"Add an end-user account."}</p>
          </TooltipContent>
        </Tooltip>
        <DialogTrigger asChild>
          <Button>
            <GoPlus />
            Add Account
          </Button>
        </DialogTrigger>
      </div>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Account</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              form.handleSubmit(onSubmit)(e);
            }}
            className="grid gap-4 py-4"
          >
            <FormField
              control={form.control}
              name="appName"
              render={({}) => (
                <FormItem>
                  <FormLabel>App Name</FormLabel>
                  <div className="w-fit bg-muted px-2 py-1 rounded-md">
                    {app.display_name}
                  </div>
                  {/* <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                    disabled
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select app" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value={app.display_name}>
                        {app.display_name}
                      </SelectItem>
                    </SelectContent>
                  </Select> */}
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="linkedAccountOwnerId"
              render={({ field }) => (
                <FormItem>
                  <div className="flex items-center gap-2">
                    <FormLabel>Linked Account Owner ID</FormLabel>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span className="cursor-pointer">
                          <BsQuestionCircle className="h-4 w-4 text-muted-foreground" />
                        </span>
                      </TooltipTrigger>
                      <TooltipContent side="top">
                        <p className="text-xs">
                          {"Input a name or label for your end user."}
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <FormControl>
                    <Input placeholder="linked account owner id" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="authType"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Auth Type</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select auth type" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {app.security_schemes.map((scheme) => (
                        <SelectItem key={scheme} value={scheme}>
                          {scheme}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {authType === "api_key" && (
              <FormField
                control={form.control}
                name="apiKey"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>API Key</FormLabel>
                    <FormControl>
                      <Input placeholder="api key" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setOpen(false)}
                type="button"
              >
                Cancel
              </Button>

              {authType === "oauth2" && (
                <Button
                  type="submit"
                  name={FORM_SUBMIT_COPY_OAUTH2_LINK_URL}
                  variant={"outline"}
                >
                  <GoCopy />
                  Copy OAuth2 URL
                </Button>
              )}

              <Button
                type="submit"
                name={(() => {
                  switch (authType) {
                    case "oauth2":
                      return FORM_SUBMIT_LINK_OAUTH2_ACCOUNT;
                    case "no_auth":
                      return FORM_SUBMIT_NO_AUTH;
                    case "api_key":
                      return FORM_SUBMIT_API_KEY;
                    default:
                      return FORM_SUBMIT_API_KEY;
                  }
                })()}
              >
                {authType === "oauth2" ? "Start OAuth2 Flow" : "Save"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
