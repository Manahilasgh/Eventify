
"use client";

import { useEffect, useState } from "react";
import { getEvents } from "@/lib/events";
import type { Event } from "@/types/event";
import EventCard from "@/components/EventCard";

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] =
    useState("all");

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const data = await getEvents();
        setEvents(data);
      } catch {
        setError(
          "Unable to load events. Please try again later."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  // Extract unique categories from published events
  const categories = Array.from(
    new Map(
      events.map((event) => [
        event.category,
        event.category_name,
      ])
    )
  );

  // Apply search and category filters
  const filteredEvents = events.filter((event) => {
    const query = search.trim().toLowerCase();

    const matchesSearch =
      event.title.toLowerCase().includes(query) ||
      event.description.toLowerCase().includes(query) ||
      event.location.toLowerCase().includes(query);

    const matchesCategory =
      selectedCategory === "all" ||
      String(event.category) === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  return (
    <main className="min-h-[80vh] bg-gray-50">

      <section className="bg-indigo-50 px-6 py-12">
        <div className="mx-auto max-w-7xl">

          <h1 className="text-4xl font-bold text-indigo-900">
            Explore Events
          </h1>

          <p className="mt-3 text-gray-600">
            Discover your next unforgettable experience.
          </p>

          <div className="mt-8 flex flex-col gap-4 sm:flex-row">

            <input
              type="search"
              placeholder="Search events or locations..."
              aria-label="Search events"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 rounded-lg border bg-white px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500"
            />

            <select
              aria-label="Filter by category"
              value={selectedCategory}
              onChange={(e) =>
                setSelectedCategory(e.target.value)
              }
              className="rounded-lg border bg-white px-4 py-3 outline-none focus:ring-2 focus:ring-indigo-500 sm:w-56"
            >
              <option value="all">
                All Categories
              </option>

              {categories.map(([id, name]) => (
                <option key={id} value={String(id)}>
                  {name}
                </option>
              ))}
            </select>

          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-10">

        {loading ? (
          <div className="py-20 text-center text-gray-500">
            Loading events...
          </div>
        ) : error ? (
          <div
            role="alert"
            className="rounded-lg bg-red-50 p-4 text-red-600"
          >
            {error}
          </div>
        ) : (
          <>
            <p className="mb-6 text-sm text-gray-500">
              {filteredEvents.length}{" "}
              {filteredEvents.length === 1
                ? "event"
                : "events"} found
            </p>

            {filteredEvents.length === 0 ? (
              <div className="rounded-xl border bg-white py-16 text-center">

                <h2 className="text-xl font-semibold text-gray-700">
                  No events found
                </h2>

                <p className="mt-2 text-gray-500">
                  Try changing your search or category.
                </p>

                <button
                  onClick={() => {
                    setSearch("");
                    setSelectedCategory("all");
                  }}
                  className="mt-5 rounded-lg bg-indigo-600 px-5 py-2 text-white hover:bg-indigo-700"
                >
                  Clear Filters
                </button>

              </div>
            ) : (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {filteredEvents.map((event) => (
                  <EventCard
                    key={event.id}
                    event={event}
                  />
                ))}
              </div>
            )}
          </>
        )}

      </section>
    </main>
  );
}
