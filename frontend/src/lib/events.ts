import api from "@/lib/api";
import type { Event, Category } from "@/types/event";

export const getEvents = async (): Promise<Event[]> => {
  const response = await api.get<Event[]>("/api/events/");
  return response.data;
};

export const getEventById = async (
  id: number
): Promise<Event> => {
  const response = await api.get<Event>(`/api/events/${id}/`);
  return response.data;
};
export const getMyEvents = async (): Promise<Event[]> => {
  const response = await api.get<Event[]>(
    "/api/events/my-events/"
  );
  return response.data;
};

export const publishEvent = async (id: number) => {
  const response = await api.post(
    `/api/events/${id}/publish/`
  );
  return response.data;
};

export const deleteEvent = async (id: number) => {
  await api.delete(`/api/events/${id}/`);
};

export interface EventData {
  title: string;
  description: string;
  category: number;
  venue_name: string;
  location: string;
  start_datetime: string;
  end_datetime: string;
}

export const getCategories = async (): Promise<Category[]> => {
  const response = await api.get("/api/events/categories/");
  return response.data;
};

export const createEvent = async (
  data: EventData
): Promise<Event> => {
  const response = await api.post("/api/events/", data);
  return response.data;
};

export const updateEvent = async (
  id: number,
  data: EventData
): Promise<Event> => {
  const response = await api.patch(`/api/events/${id}/`, data);
  return response.data;
};