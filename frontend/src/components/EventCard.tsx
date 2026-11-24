
import Link from "next/link";
import type { Event } from "@/types/event";
import { formatDate, formatTime } from "@/lib/utils";

interface EventCardProps {
  event: Event;
}

export default function EventCard({
  event,
}: EventCardProps) {
  const hasTickets = event.ticket_types.length > 0;

  const hasAvailableTickets = event.ticket_types.some(
    (ticket) => ticket.available_quantity > 0
  );

  const hasStarted =
    new Date(event.start_datetime).getTime() <= Date.now();

  return (
    <article className="flex flex-col overflow-hidden rounded-xl border bg-white shadow-sm transition hover:shadow-lg">

      <div className="flex h-36 items-center justify-center bg-gradient-to-br from-indigo-600 to-purple-600">
        <span className="px-4 text-center text-xl font-semibold text-white">
          {event.category_name}
        </span>
      </div>

      <div className="flex flex-1 flex-col p-5">

        <span className="mb-3 w-fit rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-600">
          {event.category_name}
        </span>

        <h2 className="mb-2 text-xl font-bold text-gray-800">
          {event.title}
        </h2>

        <p className="mb-4 line-clamp-2 text-sm text-gray-500">
          {event.description}
        </p>

        <div className="space-y-2 text-sm text-gray-600">
          <p>
            Date: {formatDate(event.start_datetime)}
          </p>

          <p>
            Time: {formatTime(event.start_datetime)}
          </p>

          <p>
            Venue: {event.venue_name}
          </p>

          <p>
            Location: {event.location}
          </p>
        </div>

        <div className="my-4 border-t" />

        <div className="mb-4 text-sm font-medium">
          {hasStarted ? (
            <span className="text-gray-500">
              Event already started
            </span>
          ) : !hasTickets ? (
            <span className="text-gray-500">
              Tickets coming soon
            </span>
          ) : hasAvailableTickets ? (
            <span className="text-green-600">
              Tickets available
            </span>
          ) : (
            <span className="text-red-500">
              Sold out
            </span>
          )}
        </div>

        <Link
          href={`/events/${event.id}`}
          className="mt-auto block rounded-lg bg-indigo-600 px-4 py-3 text-center text-sm font-medium text-white hover:bg-indigo-700"
        >
          View Details
        </Link>

      </div>
    </article>
  );
}
