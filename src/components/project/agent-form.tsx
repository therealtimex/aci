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
import { Textarea } from "@/components/ui/textarea";
// import { MultiSelect } from "@/components/ui/multi-select"; // Import MultiSelect component
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useState, useEffect } from "react";
import ReactJson from "react-json-view";
import { IdDisplay } from "../apps/id-display";

const formSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().min(1, "Description is required"),
  excluded_apps: z.array(z.string()).default([]),
  excluded_functions: z.array(z.string()).default([]),
  custom_instructions: z
    .record(z.string())
    .refine((obj) => Object.keys(obj).every((key) => typeof key === "string"), {
      message: "All keys must be strings.",
    })
    .refine(
      (obj) => Object.values(obj).every((value) => typeof value === "string"),
      {
        message: "All values must be strings.",
      },
    )
    .default({}),
});

type FormValues = z.infer<typeof formSchema>;

interface AgentFormProps {
  children: React.ReactNode;
  onSubmit: (values: FormValues) => Promise<void>;
  initialValues?: Partial<FormValues>;
  title: string;
  validAppNames: string[];
}

export function AgentForm({
  children,
  onSubmit,
  initialValues,
  title,
  validAppNames,
}: AgentFormProps) {
  const [open, setOpen] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: initialValues?.name ?? "",
      description: initialValues?.description ?? "",
      excluded_apps: initialValues?.excluded_apps ?? [],
      excluded_functions: initialValues?.excluded_functions ?? [],
      custom_instructions: initialValues?.custom_instructions ?? {},
    },
  });

  const handleSubmit: SubmitHandler<FormValues> = async (values) => {
    try {
      // Validate custom_instructions keys against validAppNames
      const invalidKeys = Object.keys(values.custom_instructions).filter(
        (key) => !validAppNames.includes(key),
      );

      if (invalidKeys.length > 0) {
        form.setError("custom_instructions", {
          type: "manual",
          message: `Invalid app names in custom instructions: ${invalidKeys.join(", ")}. Must be one of: ${validAppNames.join(", ")}`,
        });
        return;
      }

      await onSubmit(values);
      setOpen(false);
      form.reset();
    } catch (error) {
      console.error("Error submitting form:", error);
    }
  };

  // Reset form values when dialog opens
  useEffect(() => {
    if (open) {
      form.reset({
        name: initialValues?.name ?? "",
        description: initialValues?.description ?? "",
        excluded_apps: initialValues?.excluded_apps ?? [],
        excluded_functions: initialValues?.excluded_functions ?? [],
        custom_instructions: initialValues?.custom_instructions ?? {},
      });
    }
  }, [open, initialValues, form]);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleSubmit)}
            className="space-y-4"
          >
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* <FormField
              control={form.control}
              name="excluded_apps"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Excluded Apps</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder="Enter apps to exclude" /> 
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="excluded_functions"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Excluded Functions</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder="Enter functions to exclude" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            /> */}

            <FormField
              control={form.control}
              name="custom_instructions"
              render={({ field: { value, onChange } }) => (
                <FormItem>
                  <FormLabel>Custom Instructions</FormLabel>
                  <FormDescription>
                    Custom instructions are in the &#123;app_name:
                    instruction&#125;. Valid app names are:
                    {validAppNames.map((name) => (
                      <IdDisplay key={name} id={name} />
                    ))}
                  </FormDescription>
                  <FormControl>
                    <ReactJson
                      style={{ wordBreak: "break-all" }}
                      name={false}
                      src={value}
                      onEdit={(edit) => onChange(edit.updated_src)}
                      onAdd={(add) => onChange(add.updated_src)}
                      onDelete={(del) => onChange(del.updated_src)}
                      displayDataTypes={false}
                      enableClipboard={true}
                      defaultValue=""
                    />
                  </FormControl>
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
