
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { useAuth } from "@/app/auth-context";
import { getMyBookings } from "@/lib/bookings";
import type { Booking } from "@/types/booking";
import BookingCard from "@/components/BookingCard";

export default function MyBookingsPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");

  const fetchBookings = async () => {
    const data = await getMyBookings();
    setBookings(data);
  };

  useEffect(() => {
    if (authLoading) return;

    if (!user) {
      router.replace("/login");
      return;
    }

    if (user.role !== "customer") {
      router.replace("/");
      return;
    }

    const loadBookings = async () => {
      setLoading(true);
      setError("");

      try {
        await fetchBookings();
      } catch {
        setError("Unable to load bookings.");
      } finally {
        setLoading(false);
      }
    };

    loadBookings();
  }, [user, authLoading, router]);

  const filteredBookings = bookings.filter(
    (booking) =>
      filter === "all" || booking.status === filter
  );

  if (authLoading || !user || user.role !== "customer") {
    return <p className="p-10 text-center">Loading...</p>;
  }

  return (
    <main className="mx-auto min-h-[80vh] max-w-6xl px-6 py-10">
      <h1 className="text-4xl font-bold text-gray-800">
        My Bookings
      </h1>

      <p className="mt-2 text-gray-500">
        View and manage your event bookings.
      </p>

      <div className="my-6 flex flex-wrap gap-3">
        {["all", "confirmed", "cancelled"].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`rounded-lg px-5 py-2 text-sm capitalize ${
              filter === status
                ? "bg-indigo-600 text-white"
                : "border bg-white text-gray-600"
            }`}
          >
            {status}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="py-10 text-center text-gray-500">
          Loading bookings...
        </p>
      ) : error ? (
        <p className="rounded-lg bg-red-50 p-4 text-red-600">
          {error}
        </p>
      ) : filteredBookings.length === 0 ? (
        <div className="rounded-xl border bg-white p-12 text-center">
          <h2 className="text-xl font-semibold">
            No bookings found
          </h2>

          <Link
            href="/events"
            className="mt-5 inline-block rounded-lg bg-indigo-600 px-5 py-3 text-white"
          >
            Explore Events
          </Link>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {filteredBookings.map((booking) => (
            <BookingCard
              key={booking.id}
              booking={booking}
              onCancelled={fetchBookings}
            />
          ))}
        </div>
      )}
    </main>
  );
}
