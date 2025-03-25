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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const formSchema = z.object({
  security_scheme: z.string().min(1, "Security Scheme is required"),
});

type FormValues = z.infer<typeof formSchema>;

interface ConfigureAppPopupProps {
  children: React.ReactNode;
  configureApp: (security_scheme: string) => Promise<void>;
  name: string;
  security_schemes: string[];
}

export function ConfigureAppPopup({
  children,
  configureApp,
  name,
  security_schemes,
}: ConfigureAppPopupProps) {
  const [open, setOpen] = useState(false);
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      security_scheme: security_schemes?.[0] ?? "",
    },
  });

  const handleSubmit: SubmitHandler<FormValues> = async (values) => {
    try {
      await configureApp(values.security_scheme);
      setOpen(false);
      form.reset();
    } catch (error) {
      console.error("Error submitting form:", error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Configure App</DialogTitle>
          <p className="text-sm text-gray-500 mt-2">
            Add an app to your project
          </p>
        </DialogHeader>

        <div className="mb-4">
          <div className="text-sm">API Provider</div>
          <div className="p-2 border rounded bg-gray-100">{name}</div>
        </div>

        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleSubmit)}
            className="space-y-4"
          >
            <FormField
              control={form.control}
              name="security_scheme"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Supported Auth Type</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select Auth Type" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {security_schemes.map((scheme, index) => (
                        <SelectItem key={index} value={scheme}>
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
              <Button type="submit">Save</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
