"use client";

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { ProjectProvider } from "@/components/context/project";

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
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ProjectProvider>
          <div>
            <SidebarProvider>
              <AppSidebar />
              <main className="w-full mr-2 my-2 border rounded-lg border-gray-400 border-opacity-30">
                <Header />
                {children}
              </main>
            </SidebarProvider>
          </div>
        </ProjectProvider>
        <Footer />
      </body>
    </html>
  );
}
