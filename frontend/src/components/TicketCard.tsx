
"use client";

import { useState } from "react";
import Link from "next/link";
import axios from "axios";

import type { TicketType } from "@/types/event";
import { formatPrice } from "@/lib/utils";
import { useAuth } from "@/app/auth-context";
import { createBooking } from "@/lib/bookings";

interface TicketCardProps {
  ticket: TicketType;
  eventStarted: boolean;
  onBookingSuccess: () => Promise<void>;
}

export default function TicketCard({
  ticket,
  eventStarted,
  onBookingSuccess,
}: TicketCardProps) {
  const { user, loading } = useAuth();

  const [quantity, setQuantity] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const isSoldOut = ticket.available_quantity <= 0;
  const totalPrice = Number(ticket.price) * quantity;

  const handleBooking = async () => {
    setError("");
    setSuccess("");

    if (
      !user ||
      user.role !== "customer" ||
      eventStarted ||
      submitting ||
      !Number.isInteger(quantity) ||
      quantity < 1 ||
      quantity > ticket.available_quantity
    ) {
      return;
    }

    setSubmitting(true);

    try {
      await createBooking({
        ticket_type: ticket.id,
        quantity,
      });
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const data = err.response?.data;

        setError(
          typeof data === "object" && data !== null
            ? Object.entries(data)
                .map(([key, value]) => `${key}: ${value}`)
                .join("\n")
            : "Booking failed. Please try again."
        );
      } else {
        setError("Something went wrong.");
      }

      setSubmitting(false);
      return;
    }

    setSuccess("Booking confirmed successfully!");
    setQuantity(1);

    try {
      await onBookingSuccess();
    } catch {
      setError("Booking confirmed. Refresh to update availability.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-800">
        {ticket.name}
      </h3>

      <p className="mt-2 text-2xl font-bold text-indigo-600">
        {Number(ticket.price) === 0
          ? "Free"
          : formatPrice(ticket.price)}
      </p>

      <p className="text-sm text-gray-500">Per ticket</p>

      <p className="mt-3 text-sm text-gray-600">
        {ticket.available_quantity} tickets remaining
      </p>

      {error && (
        <div className="mt-3 whitespace-pre-line rounded-lg bg-red-50 p-3 text-sm text-red-600">
          {error}
        </div>
      )}

      {success && (
        <div className="mt-3 rounded-lg bg-green-50 p-3 text-sm text-green-700">
          {success}
        </div>
      )}

      <div className="mt-4 border-t pt-4">
        {eventStarted ? (
          <p className="text-gray-500">Booking closed</p>
        ) : isSoldOut ? (
          <p className="text-red-600">Sold out</p>
        ) : loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : !user ? (
          <Link
            href="/login"
            className="block rounded-lg bg-indigo-600 p-3 text-center text-white"
          >
            Login to Book
          </Link>
        ) : user.role !== "customer" ? (
          <p className="text-sm text-gray-500">
            Only customers can book tickets.
          </p>
        ) : (
          <div className="space-y-4">
            <label
              htmlFor={`quantity-${ticket.id}`}
              className="block text-sm font-medium"
            >
              Quantity
            </label>

            <input
              id={`quantity-${ticket.id}`}
              type="number"
              min={1}
              max={ticket.available_quantity}
              value={quantity}
              disabled={submitting}
              onChange={(e) =>
                setQuantity(Number(e.target.value))
              }
              className="w-full rounded-lg border p-2"
            />

            <div className="flex justify-between font-semibold">
              <span>Total</span>
              <span>{formatPrice(totalPrice)}</span>
            </div>

            <button
              onClick={handleBooking}
              disabled={
                submitting ||
                !Number.isInteger(quantity) ||
                quantity < 1 ||
                quantity > ticket.available_quantity
              }
              className="w-full rounded-lg bg-indigo-600 p-3 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {submitting ? "Booking..." : "Book Now"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
