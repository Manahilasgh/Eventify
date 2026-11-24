
"use client";

import { useState } from "react";
import Link from "next/link";
import axios from "axios";
import type { Booking } from "@/types/booking";
import { formatDate, formatPrice } from "@/lib/utils";
import { cancelBooking } from "@/lib/bookings";

interface BookingCardProps {
  booking: Booking;
  onCancelled: () => Promise<void>;
}

export default function BookingCard({
  booking,
  onCancelled,
}: BookingCardProps) {
  const [cancelling, setCancelling] = useState(false);
  const [error, setError] = useState("");
  const [cancelled, setCancelled] = useState(false);

  const isCancelled =
    cancelled || booking.status === "cancelled";

  const handleCancel = async () => {
    if (cancelling || isCancelled) return;

    if (!window.confirm("Are you sure you want to cancel this booking?")) {
      return;
    }

    setCancelling(true);
    setError("");

    try {
      await cancelBooking(booking.id);
      setCancelled(true);

      try {
        await onCancelled();
      } catch {
        setError("Booking cancelled. Refresh to update the list.");
      }
    } catch (err) {
      const data = axios.isAxiosError(err)
        ? err.response?.data
        : null;

      setError(
        typeof data === "object" && data !== null
          ? Object.values(data).join(" ")
          : "Unable to cancel booking."
      );
    } finally {
      setCancelling(false);
    }
  };

  return (
    <article className="rounded-xl border bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <h2 className="text-xl font-bold text-gray-800">
          {booking.event_title}
        </h2>

        <span
          className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${
            isCancelled
              ? "bg-red-50 text-red-600"
              : "bg-green-50 text-green-700"
          }`}
        >
          {isCancelled ? "cancelled" : booking.status}
        </span>
      </div>

      <div className="mt-5 space-y-2 text-sm text-gray-600">
        <p>Booking ID: #{booking.id}</p>
        <p>Ticket Type: {booking.ticket_type_name}</p>
        <p>Quantity: {booking.quantity}</p>
        <p>Booked on: {formatDate(booking.created_at)}</p>
      </div>

      <div className="mt-5 border-t pt-4">
        <p className="text-lg font-bold text-indigo-600">
          Total: {formatPrice(booking.total_price)}
        </p>
      </div>

      {error && (
        <p className="mt-3 rounded-lg bg-red-50 p-3 text-sm text-red-600">
          {error}
        </p>
      )}

      <div className="mt-5 flex flex-wrap gap-3">
        <Link
          href={`/events/${booking.event_id}`}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white"
        >
          View Event
        </Link>

        {!isCancelled && (
          <button
            onClick={handleCancel}
            disabled={cancelling}
            className="rounded-lg border border-red-500 px-4 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50"
          >
            {cancelling ? "Cancelling..." : "Cancel Booking"}
          </button>
        )}
      </div>
    </article>
  );
}
