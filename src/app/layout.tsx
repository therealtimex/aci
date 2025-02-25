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
import type { Metadata } from "next";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ACI.DEV",
  description:
    "ACI.dev is an agent-computer interface (ACI) platform that allows developers to easily connect AI with 3rd party software by tool-calling APIs.",
  icons: {
    icon: [
      {
        rel: "icon",
        type: "image/x-icon",
        url: "/favicon-light.ico",
        media: "(prefers-color-scheme: light)",
      },
      {
        rel: "icon",
        type: "image/x-icon",
        url: "/favicon-dark.ico",
        media: "(prefers-color-scheme: dark)",
      },
      {
        rel: "icon",
        sizes: "16x16",
        url: "/favicon-16x16.png",
      },
      {
        rel: "icon",
        sizes: "32x32",
        url: "/favicon-32x32.png",
      },
      {
        url: "/android-chrome-192x192.png",
        sizes: "192x192",
        type: "image/png",
      },
      {
        url: "/android-chrome-512x512.png",
        sizes: "512x512",
        type: "image/png",
      },
    ],
    apple: [
      {
        rel: "apple-touch-icon",
        sizes: "180x180",
        url: "/apple-touch-icon.png",
      },
    ],
    other: [{ rel: "manifest", url: "/site.webmanifest" }],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
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
