import type { Metadata } from "next";
import Link from "next/link";
import { Providers } from "./providers";
import { ToastProvider } from "@/components/ui/toast";
import "./globals.css";

export const metadata: Metadata = {
  title: "BRD Test Pipeline",
  description: "Multi-Agent BRD to Data Pipeline Test Case Generator",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <Providers>
          <ToastProvider>
            <nav className="border-b border-gray-200 bg-white px-6 py-3">
              <div className="mx-auto flex max-w-7xl items-center justify-between">
                <Link href="/" className="text-lg font-semibold">
                  BRD Test Pipeline
                </Link>
                <Link
                  href="/projects"
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Projects
                </Link>
              </div>
            </nav>
            <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
          </ToastProvider>
        </Providers>
      </body>
    </html>
  );
}
