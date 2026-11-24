
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import axios from "axios";

import { useAuth } from "@/app/auth-context";
import { getEventById } from "@/lib/events";
import {
  getTickets,
  createTicket,
  updateTicket,
  deleteTicket,
} from "@/lib/tickets";

import type { Event, TicketType } from "@/types/event";
import { formatPrice } from "@/lib/utils";

const initialForm = {
  name: "",
  price: "",
  quantity: "",
};

export default function ManageTicketsPage() {
  const params = useParams<{ id: string }>();
  const eventId = Number(params.id);
  const { user } = useAuth();

  const [event, setEvent] = useState<Event | null>(null);
  const [tickets, setTickets] = useState<TicketType[]>([]);
  const [form, setForm] = useState(initialForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setEvent(null);
      setError("");

      try {
        const eventData = await getEventById(eventId);

        if (eventData.organizer !== user?.id) {
          setError("Access denied.");
          return;
        }

        const ticketData = await getTickets(eventId);

        setEvent(eventData);
        setTickets(ticketData);
      } catch {
        setError("Unable to load event or tickets.");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [eventId, user?.id]);

  const refreshTickets = async () => {
    const data = await getTickets(eventId);
    setTickets(data);
  };

  const resetForm = () => {
    setForm(initialForm);
    setEditingId(null);
  };

  const handleError = (err: unknown) => {
    const data = axios.isAxiosError(err)
      ? err.response?.data
      : null;

    setError(
      data && typeof data === "object"
        ? Object.values(data).join(" ")
        : "Unable to complete action."
    );
  };

  const handleEdit = (ticket: TicketType) => {
    setEditingId(ticket.id);
    setForm({
      name: ticket.name,
      price: String(ticket.price),
      quantity: String(ticket.quantity),
    });

    setError("");
    setSuccess("");
  };

  const handleSubmit = async (
    e: React.FormEvent<HTMLFormElement>
  ) => {
    e.preventDefault();

    if (busy) return;

    setError("");
    setSuccess("");

    const quantity = Number(form.quantity);

    const existingTicket = tickets.find(
      ticket => ticket.id === editingId
    );

    if (existingTicket) {
      const booked =
        existingTicket.quantity -
        existingTicket.available_quantity;

      if (quantity < booked) {
        setError(
          `Quantity cannot be less than ${booked} booked tickets.`
        );
        return;
      }
    }

    const data = {
      name: form.name.trim(),
      price: form.price,
      quantity,
    };

    setBusy(true);

    try {
      if (editingId !== null) {
        await updateTicket(eventId, editingId, data);
        setSuccess("Ticket updated successfully.");
      } else {
        await createTicket(eventId, data);
        setSuccess("Ticket created successfully.");
      }

      resetForm();

      try {
        await refreshTickets();
      } catch {
        setError("Ticket saved. Refresh to update the list.");
      }
    } catch (err) {
      handleError(err);
    } finally {
      setBusy(false);
    }
  };

  const handleDelete = async (ticketId: number) => {
    if (busy || !window.confirm("Delete this ticket type?")) {
      return;
    }

    setBusy(true);
    setError("");
    setSuccess("");

    try {
      await deleteTicket(eventId, ticketId);
      setSuccess("Ticket deleted successfully.");

      if (editingId === ticketId) resetForm();

      try {
        await refreshTickets();
      } catch {
        setError("Ticket deleted. Refresh to update the list.");
      }
    } catch (err) {
      handleError(err);
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return <p className="p-10 text-center">Loading...</p>;
  }

  if (!event) {
    return (
      <p className="p-10 text-center text-red-600">
        {error || "Event not found."}
      </p>
    );
  }

  return (
    <main className="mx-auto min-h-[80vh] max-w-6xl px-6 py-10">
      <Link
        href="/organizer/dashboard"
        className="text-sm text-indigo-600"
      >
        &larr; Back to Dashboard
      </Link>

      <h1 className="mt-5 text-3xl font-bold">
        Manage Tickets
      </h1>

      <p className="mt-2 text-gray-500">{event.title}</p>

      {error && (
        <p className="mt-5 rounded-lg bg-red-50 p-4 text-red-600">
          {error}
        </p>
      )}

      {success && (
        <p className="mt-5 rounded-lg bg-green-50 p-4 text-green-700">
          {success}
        </p>
      )}

      <div className="mt-8 grid gap-8 lg:grid-cols-2">
        {/* Ticket form */}
        <div className="h-fit rounded-xl border bg-white p-6">
          <h2 className="mb-5 text-xl font-bold">
            {editingId !== null ? "Edit Ticket" : "Add Ticket"}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-2 block font-medium">
                Ticket Name
              </label>

              <input
                value={form.name}
                onChange={e =>
                  setForm({ ...form, name: e.target.value })
                }
                placeholder="General Admission"
                required
                className="w-full rounded-lg border p-3"
              />
            </div>

            <div>
              <label className="mb-2 block font-medium">
                Price (PKR)
              </label>

              <input
                type="number"
                min="0"
                step="0.01"
                value={form.price}
                onChange={e =>
                  setForm({ ...form, price: e.target.value })
                }
                required
                className="w-full rounded-lg border p-3"
              />
            </div>

            <div>
              <label className="mb-2 block font-medium">
                Total Quantity
              </label>

              <input
                type="number"
                min="1"
                step="1"
                value={form.quantity}
                onChange={e =>
                  setForm({ ...form, quantity: e.target.value })
                }
                required
                className="w-full rounded-lg border p-3"
              />
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={busy || !form.name.trim()}
                className="rounded-lg bg-indigo-600 px-5 py-3 text-white disabled:opacity-50"
              >
                {busy
                  ? "Saving..."
                  : editingId !== null
                    ? "Save Changes"
                    : "Add Ticket"}
              </button>

              {editingId !== null && (
                <button
                  type="button"
                  disabled={busy}
                  onClick={resetForm}
                  className="rounded-lg border px-5 py-3"
                >
                  Cancel
                </button>
              )}
            </div>
          </form>
        </div>

        {/* Existing tickets */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold">
            Existing Tickets ({tickets.length})
          </h2>

          {tickets.length === 0 && (
            <p className="rounded-xl border bg-white p-6 text-gray-500">
              No ticket types added yet.
            </p>
          )}

          {tickets.map(ticket => (
            <article
              key={ticket.id}
              className="rounded-xl border bg-white p-6"
            >
              <h3 className="text-lg font-bold">
                {ticket.name}
              </h3>

              <p className="mt-2 text-xl font-bold text-indigo-600">
                {formatPrice(ticket.price)}
              </p>

              <div className="mt-4 space-y-1 text-sm text-gray-600">
                <p>Total Quantity: {ticket.quantity}</p>

                <p>
                  Booked:{" "}
                  {ticket.quantity - ticket.available_quantity}
                </p>

                <p>
                  Available: {ticket.available_quantity}
                </p>
              </div>

              <div className="mt-4 flex gap-3">
                <button
                  disabled={busy}
                  onClick={() => handleEdit(ticket)}
                  className="rounded-lg border px-4 py-2 text-sm"
                >
                  Edit
                </button>

                <button
                  disabled={busy}
                  onClick={() => handleDelete(ticket.id)}
                  className="rounded-lg border border-red-500 px-4 py-2 text-sm text-red-600 disabled:opacity-50"
                >
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      </div>
    </main>
  );
}
