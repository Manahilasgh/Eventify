
"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/app/auth-context";

export default function Navbar() {
  const router = useRouter();
  const { user, loading, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.replace("/");
  };

  return (
    <header className="sticky top-0 z-50 border-b bg-white shadow-sm">
      <nav className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4">

        <Link
          href="/"
          className="text-2xl font-bold text-indigo-600"
        >
          Eventify
        </Link>

        <div className="flex flex-wrap items-center gap-5 text-sm font-medium text-gray-700">

          <Link href="/" className="hover:text-indigo-600">
            Home
          </Link>

          <Link
            href="/events"
            className="hover:text-indigo-600"
            >
            Events
          </Link>

          {!loading && (
            <>
              {user ? (
                <>
                {user.role === "customer" && (
                <Link
                    href="/my-bookings"
                    className="hover:text-indigo-600"
                >
                    My Bookings
                </Link>
                )}
                {user.role === "customer" && (
                <Link
                    href="/become-organizer"
                    className="hover:text-indigo-600"
                >
                    Become Organizer
                </Link>
                )}
                {user.role === "organizer" && (
                <Link
                    href="/organizer/dashboard"
                    className="hover:text-indigo-600"
                >
                    Dashboard
                </Link>
                )}
                  <span className="rounded-full bg-indigo-50 px-3 py-1 capitalize text-indigo-600">
                    {user.role}
                  </span>

                  <span>
                    Hi, {user.first_name}
                  </span>

                  <button
                    onClick={handleLogout}
                    className="rounded-lg border border-red-500 px-4 py-2 text-red-500 hover:bg-red-50"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="hover:text-indigo-600"
                  >
                    Login
                  </Link>

                  <Link
                    href="/register"
                    className="rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700"
                  >
                    Register
                  </Link>
                </>
              )}
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
