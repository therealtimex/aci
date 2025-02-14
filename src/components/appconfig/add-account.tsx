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

const formSchema = z.object({
  appName: z.string().min(1, "App name is required"),
  authType: z.enum(["api_key", "oauth2"]),
  linkedAccountOwnerId: z.string().min(1, "Account owner ID is required"),
  //   apiKey: z.string().min(0, "API Key is required"),
});

type FormValues = z.infer<typeof formSchema>;

interface AddAccountProps {
  app: App;
  updateLinkedAccounts: () => void;
}

const FORM_SUBMIT_COPY_OAUTH2_LINK_URL = "copyOAuth2LinkURL";
const FORM_SUBMIT_LINK_OAUTH2_ACCOUNT = "linkOAuth2";
const FORM_SUBMIT_API_KEY = "apiKey";

export function AddAccountForm({ app, updateLinkedAccounts }: AddAccountProps) {
  const { project } = useProject();
  const [open, setOpen] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      appName: app.display_name,
      authType: app.security_schemes[0] as "api_key" | "oauth2",
      linkedAccountOwnerId: "",
      //   apiKey: "",
    },
  });

  const authType = form.watch("authType");

  const fetchOath2LinkURL = async (
    linkedAccountOwnerId: string,
    afterOAuth2LinkRedirectURL?: string,
  ): Promise<string> => {
    if (linkedAccountOwnerId === "") {
      throw new Error("Account owner ID is required");
    }

    if (
      !project ||
      !project.agents ||
      project.agents.length === 0 ||
      !project.agents[0].api_keys ||
      project.agents[0].api_keys.length === 0
    ) {
      throw new Error("No API key available");
    }

    const params = new URLSearchParams();
    params.append("app_name", app.name);
    params.append("linked_account_owner_id", linkedAccountOwnerId);
    if (afterOAuth2LinkRedirectURL) {
      params.append(
        "after_oauth2_link_redirect_url",
        afterOAuth2LinkRedirectURL,
      );
    }

    const response = await fetch(
      `${
        process.env.NEXT_PUBLIC_API_URL
      }/v1/linked-accounts/oauth2?${params.toString()}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "X-API-KEY": project.agents[0].api_keys[0].key,
        },
      },
    );
    const data = await response.json();
    return data.url;
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
        `${process.env.NEXT_PUBLIC_DEV_PORTAL_URL}/appconfig/${app.name}`,
      );
      window.location.href = oauth2LinkURL;
    } catch (error) {
      console.error("Error linking OAuth2 account:", error);
      toast.error("Failed to link account");
    }
  };

  const linkAPIAccount = async (linkedAccountOwnerId: string) => {
    if (
      !project ||
      !project.agents ||
      project.agents.length === 0 ||
      !project.agents[0].api_keys ||
      project.agents[0].api_keys.length === 0
    ) {
      throw new Error("No API key available");
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/v1/linked-accounts/default`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-KEY": project.agents[0].api_keys[0].key,
        },
        body: JSON.stringify({
          app_name: app.name,
          linked_account_owner_id: linkedAccountOwnerId,
        }),
      },
    );

    if (!response.ok) {
      console.error(`Failed to create linked account: ${response.statusText}`);
      toast.error("Failed to link account");
      return;
    }

    toast.success("Account linked successfully");
    form.reset();
    setOpen(false);
    updateLinkedAccounts();
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
        await linkAPIAccount(values.linkedAccountOwnerId);
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
      <DialogTrigger asChild>
        <Button>
          <GoPlus className="mr-2" /> Add Account
        </Button>
      </DialogTrigger>
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
              render={({ field }) => (
                <FormItem>
                  <FormLabel>App Name</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
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
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="linkedAccountOwnerId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Account Owner ID</FormLabel>
                  <FormControl>
                    <Input placeholder="account owner id" {...field} />
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
                name={
                  authType === "oauth2"
                    ? FORM_SUBMIT_LINK_OAUTH2_ACCOUNT
                    : FORM_SUBMIT_API_KEY
                }
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
