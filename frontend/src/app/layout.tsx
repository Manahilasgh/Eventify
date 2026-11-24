
import "./globals.css";
import type { Metadata } from "next";
import { AuthProvider } from "./auth-context";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "Eventify",
  description: "Event Ticketing & Booking Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col bg-gray-50">
        <AuthProvider>
          <Navbar />

          <div className="flex-1">
            {children}
          </div>

          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}
