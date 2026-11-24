
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";

import EventForm from "@/components/EventForm";
import { getEventById } from "@/lib/events";
import { useAuth } from "@/app/auth-context";
import type { Event } from "@/types/event";

export default function EditEventPage() {
  const params = useParams<{ id: string }>();
  const eventId = Number(params.id);
  const { user } = useAuth();

  const [event, setEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    setEvent(null);

    getEventById(eventId)
      .then(setEvent)
      .catch(() => setError("Unable to load event."))
      .finally(() => setLoading(false));
  }, [eventId]);

  if (loading) {
    return <p className="p-10 text-center">Loading...</p>;
  }

  if (error || !event || event.organizer !== user?.id) {
    return (
      <div className="p-10 text-center">
        <p className="text-red-600">
          {error || "Event not found or access denied."}
        </p>

        <Link
          href="/organizer/dashboard"
          className="mt-4 inline-block text-indigo-600"
        >
          Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <EventForm key={event.id} event={event} />
    </main>
  );
}
