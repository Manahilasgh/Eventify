
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import axios from "axios";

import { getEventById } from "@/lib/events";
import { formatDate, formatTime } from "@/lib/utils";
import type { Event } from "@/types/event";
import TicketCard from "@/components/TicketCard";

export default function EventDetailsPage() {
  const params = useParams<{ id: string }>();
  const eventId = Number(params.id);

  const [event, setEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchEvent = async () => {
      setLoading(true);
      setError("");
      setEvent(null);

      try {
        const data = await getEventById(eventId);
        setEvent(data);
      } catch (err) {
        if (
          axios.isAxiosError(err) &&
          err.response?.status === 404
        ) {
          setError("Event not found.");
        } else {
          setError("Unable to load event details.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchEvent();
  }, [eventId]);

  if (loading) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center">
        <p className="text-gray-500">
          Loading event details...
        </p>
      </main>
    );
  }

  if (error || !event) {
    return (
      <main className="flex min-h-[70vh] flex-col items-center justify-center px-6">

        <h1 className="text-2xl font-bold text-gray-800">
          {error || "Event not found."}
        </h1>

        <Link
          href="/events"
          className="mt-6 rounded-lg bg-indigo-600 px-5 py-3 text-white hover:bg-indigo-700"
        >
          Back to Events
        </Link>

      </main>
    );
  }

  const eventStarted =
    new Date(event.start_datetime).getTime() <= Date.now();

 const refreshEvent = async () => {
      const data = await getEventById(eventId);
      setEvent(data);
        };

      if (!Number.isSafeInteger(eventId) || eventId <= 0) {
        setError("Invalid event ID.");
        setLoading(false);
        return;
      }

  return (
    <main className="min-h-[80vh] bg-gray-50">

      {/* Event banner */}
      <section className="bg-gradient-to-br from-indigo-700 to-purple-700 px-6 py-16 text-white">

        <div className="mx-auto max-w-6xl">

          <Link
            href="/events"
            className="text-sm text-indigo-100 hover:underline"
          >
            &larr; Back to Events
          </Link>

          <div className="mt-8">
            <span className="rounded-full bg-white/20 px-4 py-2 text-sm">
              {event.category_name}
            </span>
          </div>

          <h1 className="mt-6 text-4xl font-bold md:text-5xl">
            {event.title}
          </h1>

          <p className="mt-4 text-lg text-indigo-100">
            {event.venue_name}, {event.location}
          </p>

          <p className="mt-2 text-indigo-100">
            {formatDate(event.start_datetime)}
            {" • "}
            {formatTime(event.start_datetime)}
          </p>

        </div>
      </section>

      {/* Main event content */}
      <section className="mx-auto grid max-w-6xl gap-8 px-6 py-10 lg:grid-cols-3">

        {/* Left column */}
        <div className="space-y-8 lg:col-span-2">

          <div className="rounded-xl border bg-white p-6 shadow-sm">

            <h2 className="mb-4 text-2xl font-bold text-gray-800">
              About this event
            </h2>

            <p className="whitespace-pre-line leading-relaxed text-gray-600">
              {event.description}
            </p>

          </div>

          {/* Event information */}
          <div className="rounded-xl border bg-white p-6 shadow-sm">

            <h2 className="mb-6 text-2xl font-bold text-gray-800">
              Event Information
            </h2>

            <div className="grid gap-6 sm:grid-cols-2">

              <div>
                <p className="text-sm text-gray-500">
                  Start Date & Time
                </p>
                <p className="mt-1 font-medium">
                  {formatDate(event.start_datetime)}
                </p>
                <p className="text-gray-600">
                  {formatTime(event.start_datetime)}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-500">
                  End Date & Time
                </p>
                <p className="mt-1 font-medium">
                  {formatDate(event.end_datetime)}
                </p>
                <p className="text-gray-600">
                  {formatTime(event.end_datetime)}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-500">
                  Venue
                </p>
                <p className="mt-1 font-medium">
                  {event.venue_name}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-500">
                  Location
                </p>
                <p className="mt-1 font-medium">
                  {event.location}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-500">
                  Category
                </p>
                <p className="mt-1 font-medium">
                  {event.category_name}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-500">
                  Organized by
                </p>
                <p className="mt-1 break-all font-medium">
                  {event.organizer_email}
                </p>
              </div>

            </div>
          </div>

        </div>

        {/* Right column: Tickets */}
        <aside>

          <h2 className="mb-5 text-2xl font-bold text-gray-800">
            Tickets
          </h2>

          {eventStarted && (
            <div className="mb-4 rounded-lg bg-yellow-50 p-4 text-sm text-yellow-800">
              This event has already started.
              Ticket booking is closed.
            </div>
          )}

          {event.ticket_types.length === 0 ? (
            <div className="rounded-xl border bg-white p-6 text-center">

              <h3 className="font-semibold text-gray-700">
                {eventStarted
                  ? "No tickets available"
                  : "Tickets coming soon"}
              </h3>

              <p className="mt-2 text-sm text-gray-500">
                {eventStarted
                  ? "Booking is closed for this event."
                  : "The organizer has not added ticket types yet."}
              </p>

            </div>
          ) : (
            <div className="space-y-4">
              {event.ticket_types.map((ticket) => (
            <TicketCard
                key={ticket.id}
                ticket={ticket}
                eventStarted={eventStarted}
                onBookingSuccess={refreshEvent}
            />
            ))}
            </div>
          )}

        </aside>

      </section>
    </main>
  );
}
