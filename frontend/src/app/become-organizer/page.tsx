
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

import { useAuth } from "@/app/auth-context";
import { applyOrganizer } from "@/lib/organizers";

export default function BecomeOrganizerPage() {
  const router = useRouter();
  const { user, loading } = useAuth();

  const [organizationName, setOrganizationName] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (loading) return;

    if (!user) {
      router.replace("/login");
    } else if (user.role !== "customer") {
      router.replace("/");
    }
  }, [user, loading, router]);

  const handleSubmit = async (
    e: React.FormEvent<HTMLFormElement>
  ) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await applyOrganizer({
        organization_name: organizationName.trim(),
        description: description.trim(),
      });

      setSuccess(true);
    } catch (err) {
      const data = axios.isAxiosError(err)
        ? err.response?.data
        : null;

      setError(
        typeof data === "object" && data !== null
          ? Object.values(data).join(" ")
          : "Unable to submit application."
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (loading || !user || user.role !== "customer") {
    return <p className="p-10 text-center">Loading...</p>;
  }

  return (
    <main className="mx-auto min-h-[80vh] max-w-2xl px-6 py-12">
      <div className="rounded-xl border bg-white p-8 shadow-sm">

        <h1 className="text-3xl font-bold text-indigo-600">
          Become an Organizer
        </h1>

        <p className="mb-6 mt-3 text-gray-500">
          Apply to create and manage your own events.
        </p>

        {success ? (
          <div className="rounded-lg bg-green-50 p-5 text-green-700">
            <h2 className="font-semibold">
              Application submitted successfully!
            </h2>

            <p className="mt-2 text-sm">
              Your application is pending admin approval.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">

            {error && (
              <p className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
                {error}
              </p>
            )}

            <div>
              <label
                htmlFor="organization"
                className="mb-2 block font-medium"
              >
                Organization Name
              </label>

              <input
                id="organization"
                value={organizationName}
                onChange={(e) =>
                  setOrganizationName(e.target.value)
                }
                required
                className="w-full rounded-lg border p-3"
              />
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
                value={description}
                onChange={(e) =>
                  setDescription(e.target.value)
                }
                rows={5}
                required
                className="w-full rounded-lg border p-3"
                placeholder="Tell us about your organization..."
              />
            </div>

            <button
              type="submit"
              disabled={
                submitting ||
                !organizationName.trim() ||
                !description.trim()
              }
              className="w-full rounded-lg bg-indigo-600 p-3 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {submitting
                ? "Submitting..."
                : "Submit Application"}
            </button>

          </form>
        )}
      </div>
    </main>
  );
}
