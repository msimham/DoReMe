import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "DoReMe - Musician Collaboration Platform",
  description: "Connect and collaborate with musicians worldwide",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 lg:ml-64 bg-white">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
