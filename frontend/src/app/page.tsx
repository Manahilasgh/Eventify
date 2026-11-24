
import Link from "next/link";

export default function HomePage() {
  return (
    <main>
      <section className="bg-gradient-to-br from-indigo-700 to-purple-700 px-6 py-28 text-center text-white">

        <span className="rounded-full bg-white/20 px-4 py-2 text-sm">
          Your next experience starts here
        </span>

        <h1 className="mx-auto mt-8 max-w-3xl text-4xl font-bold leading-tight md:text-6xl">
          Discover events.
          <br />
          Create unforgettable memories.
        </h1>

        <p className="mx-auto mt-6 max-w-xl text-lg text-indigo-100">
          Find exciting events, connect with people,
          and book your tickets effortlessly with Eventify.
        </p>

        <Link
        href="/events"
        className="mt-8 inline-block rounded-lg bg-white px-8 py-3 font-semibold text-indigo-700 hover:bg-indigo-50"
        >
        Explore Events
        </Link>

      </section>

      <section className="mx-auto max-w-6xl px-6 py-16">

        <h2 className="mb-10 text-center text-3xl font-bold text-gray-800">
          Why Eventify?
        </h2>

        <div className="grid gap-6 md:grid-cols-3">
          {[
            {
              title: "Discover Events",
              description:
                "Explore exciting events across different categories.",
            },
            {
              title: "Easy Booking",
              description:
                "Reserve your tickets with a simple booking process.",
            },
            {
              title: "Organize Events",
              description:
                "Become an organizer and manage your own events.",
            },
          ].map((feature) => (
            <div
              key={feature.title}
              className="rounded-xl border bg-white p-6 shadow-sm"
            >
              <h3 className="mb-3 text-xl font-semibold text-indigo-600">
                {feature.title}
              </h3>

              <p className="text-gray-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

      </section>
    </main>
  );
}
