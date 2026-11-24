
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import axios from "axios";

import { useAuth } from "@/app/auth-context";
import {
  getMyEvents,
  publishEvent,
  deleteEvent,
} from "@/lib/events";

import type { Event } from "@/types/event";
import { formatDate } from "@/lib/utils";

export default function OrganizerDashboard() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);

  const fetchEvents = async () => {
    const data = await getMyEvents();
    setEvents(data);
  };

  useEffect(() => {
    if (authLoading) return;

    if (!user) {
      router.replace("/login");
      return;
    }

    if (user.role !== "organizer") {
      router.replace("/");
      return;
    }

    fetchEvents()
      .catch(() => setError("Unable to load events."))
      .finally(() => setLoading(false));
  }, [user, authLoading, router]);

  const handleAction = async (
    id: number,
    action: "publish" | "delete"
  ) => {
    if (busy) return;

    if (
      action === "delete" &&
      !window.confirm("Delete this event permanently?")
    ) {
      return;
    }

    setBusy(true);
    setError("");
    setSuccess("");

    try {
      if (action === "publish") {
        await publishEvent(id);
        setSuccess("Event published successfully.");
      } else {
        await deleteEvent(id);
        setSuccess("Event deleted successfully.");
      }

      try {
        await fetchEvents();
      } catch {
        setError("Action completed. Refresh to update the list.");
      }
    } catch (err) {
      const data = axios.isAxiosError(err)
        ? err.response?.data
        : null;

      setError(
        data && typeof data === "object"
          ? Object.values(data).join(" ")
          : "Unable to complete action."
      );
    } finally {
      setBusy(false);
    }
  };

  if (authLoading || !user || user.role !== "organizer") {
    return <p className="p-10 text-center">Loading...</p>;
  }

  const stats = [
    { label: "Total Events", count: events.length },
    {
      label: "Published",
      count: events.filter(e => e.status === "published").length,
    },
    {
      label: "Drafts",
      count: events.filter(e => e.status === "draft").length,
    },
  ];

  return (
    <main className="mx-auto min-h-[80vh] max-w-7xl px-6 py-10">

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">
            Organizer Dashboard
          </h1>
          <p className="mt-2 text-gray-500">
            Manage your events and tickets.
          </p>
        </div>

        <Link
          href="/organizer/events/create"
          className="rounded-lg bg-indigo-600 px-5 py-3 text-white"
        >
          + Create Event
        </Link>
      </div>

      <div className="my-8 grid gap-4 sm:grid-cols-3">
        {stats.map(stat => (
          <div
            key={stat.label}
            className="rounded-xl border bg-white p-6"
          >
            <p className="text-gray-500">{stat.label}</p>
            <p className="mt-2 text-3xl font-bold text-indigo-600">
              {stat.count}
            </p>
          </div>
        ))}
      </div>

      {error && (
        <p className="mb-4 rounded-lg bg-red-50 p-4 text-red-600">
          {error}
        </p>
      )}

      {success && (
        <p className="mb-4 rounded-lg bg-green-50 p-4 text-green-700">
          {success}
        </p>
      )}

      <h2 className="mb-5 text-2xl font-bold">My Events</h2>

      {loading ? (
        <p>Loading events...</p>
      ) : events.length === 0 ? (
        <p className="rounded-xl border bg-white p-10 text-center text-gray-500">
          You haven't created any events yet.
        </p>
      ) : (
        <div className="space-y-4">
          {events.map(event => (
            <article
              key={event.id}
              className="rounded-xl border bg-white p-6 shadow-sm"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h3 className="text-xl font-bold">
                  {event.title}
                </h3>

                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${
                    event.status === "published"
                      ? "bg-green-50 text-green-700"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  {event.status}
                </span>
              </div>

              <div className="mt-3 space-y-1 text-sm text-gray-600">
                <p>Category: {event.category_name}</p>
                <p>Location: {event.location}</p>
                <p>Date: {formatDate(event.start_datetime)}</p>
                <p>Ticket Types: {event.ticket_types.length}</p>
              </div>

              <div className="mt-5 flex flex-wrap gap-3">

                <Link
                  href={`/organizer/events/${event.id}/edit`}
                  className="rounded-lg border px-4 py-2 text-sm"
                >
                  Edit
                </Link>

                <Link
                  href={`/organizer/events/${event.id}/tickets`}
                  className="rounded-lg border border-indigo-600 px-4 py-2 text-sm text-indigo-600"
                >
                  Manage Tickets
                </Link>

                {event.status === "draft" && (
                  <button
                    disabled={busy}
                    onClick={() => handleAction(event.id, "publish")}
                    className="rounded-lg bg-green-600 px-4 py-2 text-sm text-white disabled:opacity-50"
                  >
                    Publish
                  </button>
                )}

                {event.status === "published" && (
                  <Link
                    href={`/events/${event.id}`}
                    className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white"
                  >
                    View Event
                  </Link>
                )}

                <button
                  disabled={busy}
                  onClick={() => handleAction(event.id, "delete")}
                  className="rounded-lg border border-red-500 px-4 py-2 text-sm text-red-600 disabled:opacity-50"
                >
                  Delete
                </button>

              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
