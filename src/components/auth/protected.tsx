"use client";

import React from "react";
import { useUser } from "@/components/context/user";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import { Input } from "../ui/input";
import { checkSignUpCode } from "@/lib/api/user";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

const formSchema = z.object({
  signUpCode: z.string().min(1, "Sign Up Code is required"),
});

type FormValues = z.infer<typeof formSchema>;

const Protected = ({ children }: Readonly<{ children: React.ReactNode }>) => {
  // TODO: make this loads faster
  const { user, login, signup } = useUser();

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      signUpCode: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    if (!(await checkSignUpCode(values.signUpCode))) {
      form.setError("signUpCode", {
        message: "Invalid Sign Up Code",
      });
      return;
    }
    signup(values.signUpCode);
  }

  return (
    <>
      {user ? (
        <div>{children}</div>
      ) : (
        <div className="w-full flex flex-col items-center justify-center h-screen">
          <Image
            src="/logo.svg"
            alt="Aipotheosis Labs Logo"
            width={200}
            height={40}
            priority
            className="object-contain m-4"
          />
          <h1 className="text-2xl font-bold">Authentication Required</h1>
          <p className="mb-4">Please sign up or log in to access this page</p>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="flex gap-2">
              <FormField
                control={form.control}
                name="signUpCode"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Input placeholder="Sign Up Code" {...field} />
                    </FormControl>
                    <FormDescription></FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit">Sign Up</Button>
            </form>
          </Form>

          <Button onClick={login}>Log in</Button>
        </div>
      )}
    </>
  );
};

export default Protected;
