
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import axios from "axios";

import {
  getCategories,
  createEvent,
  updateEvent,
} from "@/lib/events";

import type { Event, Category } from "@/types/event";

interface EventFormProps {
  event?: Event;
}

const toLocalDateTime = (value: string) => {
  const date = new Date(value);

  return new Date(
    date.getTime() - date.getTimezoneOffset() * 60000
  ).toISOString().slice(0, 16);
};

export default function EventForm({ event }: EventFormProps) {
  const router = useRouter();

  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    title: event?.title || "",
    description: event?.description || "",
    category: event ? String(event.category) : "",
    venue_name: event?.venue_name || "",
    location: event?.location || "",
    start_datetime: event
      ? toLocalDateTime(event.start_datetime)
      : "",
    end_datetime: event
      ? toLocalDateTime(event.end_datetime)
      : "",
  });

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch(() => setError("Unable to load categories."))
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    setForm(prev => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (
    e: React.FormEvent<HTMLFormElement>
  ) => {
    e.preventDefault();
    setError("");

    if (
      new Date(form.end_datetime) <=
      new Date(form.start_datetime)
    ) {
      setError("End time must be after start time.");
      return;
    }

    setSubmitting(true);

    try {
      const data = {
        ...form,
        category: Number(form.category),
        start_datetime: new Date(
          form.start_datetime
        ).toISOString(),
        end_datetime: new Date(
          form.end_datetime
        ).toISOString(),
      };

      if (event) {
        await updateEvent(event.id, data);
      } else {
        await createEvent(data);
      }

      router.replace("/organizer/dashboard");
    } catch (err) {
      const data = axios.isAxiosError(err)
        ? err.response?.data
        : null;

      setError(
        data && typeof data === "object"
          ? Object.entries(data)
              .map(([key, value]) => `${key}: ${value}`)
              .join("\n")
          : "Unable to save event."
      );
    } finally {
      setSubmitting(false);
    }
  };

  const fields = [
    { name: "title", label: "Event Title", type: "text" },
    { name: "venue_name", label: "Venue Name", type: "text" },
    { name: "location", label: "Location", type: "text" },
    {
      name: "start_datetime",
      label: "Start Date & Time",
      type: "datetime-local",
    },
    {
      name: "end_datetime",
      label: "End Date & Time",
      type: "datetime-local",
    },
  ] as const;

  return (
    <div className="rounded-xl border bg-white p-8 shadow-sm">
      <h1 className="mb-6 text-3xl font-bold text-indigo-600">
        {event ? "Edit Event" : "Create Event"}
      </h1>

      {error && (
        <p className="mb-5 whitespace-pre-line rounded-lg bg-red-50 p-3 text-sm text-red-600">
          {error}
        </p>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        {fields.map(field => (
          <div key={field.name}>
            <label
              htmlFor={field.name}
              className="mb-2 block font-medium"
            >
              {field.label}
            </label>

            <input
              id={field.name}
              name={field.name}
              type={field.type}
              value={form[field.name]}
              onChange={handleChange}
              required
              className="w-full rounded-lg border p-3"
            />
          </div>
        ))}

        <div>
          <label
            htmlFor="category"
            className="mb-2 block font-medium"
          >
            Category
          </label>

          <select
            id="category"
            name="category"
            value={form.category}
            onChange={handleChange}
            required
            disabled={loading}
            className="w-full rounded-lg border p-3"
          >
            <option value="">
              {loading ? "Loading..." : "Select Category"}
            </option>

            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="description"
            className="mb-2 block font-medium"
          >
            Description
          </label>

          <textarea
            id="description"
            name="description"
            value={form.description}
            onChange={handleChange}
            required
            rows={5}
            className="w-full rounded-lg border p-3"
          />
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={submitting || loading || !form.category}
            className="rounded-lg bg-indigo-600 px-6 py-3 text-white disabled:opacity-50"
          >
            {submitting
              ? "Saving..."
              : event
                ? "Save Changes"
                : "Create Event"}
          </button>

          <Link
            href="/organizer/dashboard"
            className="rounded-lg border px-6 py-3"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
