"use client";

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { ProjectProvider } from "@/components/context/project";
import Protected from "@/components/auth/protected";
import { UserProvider } from "@/components/context/user";
import { Toaster } from "@/components/ui/sonner";
import { Analytics } from "@vercel/analytics/next";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <title>ACI.DEV Platform</title>
        <meta
          name="description"
          content="ACI.dev is an agent-computer interface (ACI) platform that allows developers to easily connect AI with 3rd party software by tool-calling APIs."
        />

        <link
          rel="icon"
          type="image/x-icon"
          href="/favicon-light.ico"
          media="(prefers-color-scheme: light)"
        />
        <link
          rel="icon"
          type="image/x-icon"
          href="/favicon-dark.ico"
          media="(prefers-color-scheme: dark)"
        />
        <link rel="icon" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="icon" sizes="32x32" href="/favicon-32x32.png" />

        <link
          rel="icon"
          sizes="192x192"
          href="/android-chrome-192x192.png"
          type="image/png"
        />
        <link
          rel="icon"
          sizes="512x512"
          href="/android-chrome-512x512.png"
          type="image/png"
        />

        <link
          rel="apple-touch-icon"
          sizes="180x180"
          href="/apple-touch-icon.png"
        />

        <link rel="manifest" href="/site.webmanifest" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <UserProvider>
          <ProjectProvider>
            <Protected>
              <SidebarProvider>
                <AppSidebar />
                <SidebarInset>
                  <main className="w-full h-full mr-2 border rounded-lg border-gray-400 border-opacity-30 bg-white">
                    <Header />
                    {children}
                    <Analytics />
                  </main>
                </SidebarInset>
              </SidebarProvider>
            </Protected>
          </ProjectProvider>
          <Footer />
        </UserProvider>
        <Toaster />
      </body>
    </html>
  );
}
