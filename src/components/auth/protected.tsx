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
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

const formSchema = z.object({
  signUpCode: z.string().min(1, "Sign Up Code is required"),
});

type FormValues = z.infer<typeof formSchema>;

const Protected = ({ children }: Readonly<{ children: React.ReactNode }>) => {
  const [isLogin, setIsLogin] = React.useState(true);
  const toggleLogin = () => setIsLogin(!isLogin);
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
        <div className="w-full flex flex-col items-center justify-center h-screen border">
          <Card
            className={
              " flex flex-col items-center justify-center w-96 border shadow-lg"
            }
          >
            <Image
              src="/aci-dev-full-logo.svg"
              alt="ACI Dev Logo"
              width={200}
              height={40}
              priority
              className="object-contain my-6"
            />
            <Separator orientation="horizontal" />
            <div className="flex items-center flex-col justify-center pb-8">
              {isLogin ? (
                <>
                  <h1 className="text-xl font-bold pt-8">Login to ACI.DEV</h1>
                  <h4 className="text py-6 ">
                    Welcome back! Please login to continue
                  </h4>
                  <Button
                    variant={"outline"}
                    className="w-full font-bold flex items-center justify-center select-none"
                    onClick={login}
                  >
                    <Image
                      src="/icon/google.svg"
                      alt="Google Icon"
                      width={20}
                      height={20}
                      className="mr-2"
                    />
                    Log in with Google
                  </Button>
                </>
              ) : (
                <>
                  <h1 className="text-xl font-bold pt-8">Sign Up to ACI.DEV</h1>
                  <h4 className="text py-6 text-center">
                    Welcome! Please enter your sign up code
                  </h4>
                  <Form {...form}>
                    <form
                      onSubmit={form.handleSubmit(onSubmit)}
                      className="flex flex-col gap-2 mx-0 px-0 w-full"
                    >
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
                      <Button
                        variant={"outline"}
                        className="w-full font-bold flex items-center justify-center select-none"
                        type="submit"
                      >
                        <Image
                          src="/icon/google.svg"
                          alt="Google Icon"
                          width={20}
                          height={20}
                          className="mr-2"
                        />
                        Sign Up with Google
                      </Button>
                    </form>
                  </Form>
                </>
              )}
            </div>
            <Separator orientation="horizontal" />

            <div className="w-full h8 text-center p-1">
              {isLogin ? (
                <>
                  Don&apos;t have an account?
                  <Button
                    variant="link"
                    className="text-[#6269D2] hover:underline font-bold"
                    onClick={toggleLogin}
                  >
                    Sign Up
                  </Button>
                </>
              ) : (
                <>
                  Already have an account?
                  <Button
                    variant="link"
                    className="text-[#6269D2] hover:underline font-bold"
                    onClick={toggleLogin}
                  >
                    Log In
                  </Button>
                </>
              )}
            </div>
          </Card>
        </div>
      )}
    </>
  );
};

export default Protected;
