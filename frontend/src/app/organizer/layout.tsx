"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/auth-context";

export default function OrganizerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;

    if (!user) {
      router.replace("/login");
    } else if (user.role !== "organizer") {
      router.replace("/");
    }
  }, [user, loading, router]);

  if (loading || !user || user.role !== "organizer") {
    return <p className="p-10 text-center">Loading...</p>;
  }

  return <>{children}</>;
}