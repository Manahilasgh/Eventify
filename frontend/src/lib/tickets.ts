import api from "@/lib/api";
import type { TicketType } from "@/types/event";

export interface TicketData {
  name: string;
  price: string;
  quantity: number;
}

export const getTickets = async (
  eventId: number
): Promise<TicketType[]> => {
  const response = await api.get(
    `/api/events/${eventId}/tickets/`
  );
  return response.data;
};

export const createTicket = async (
  eventId: number,
  data: TicketData
): Promise<TicketType> => {
  const response = await api.post(
    `/api/events/${eventId}/tickets/`,
    data
  );
  return response.data;
};

export const updateTicket = async (
  eventId: number,
  ticketId: number,
  data: TicketData
): Promise<TicketType> => {
  const response = await api.patch(
    `/api/events/${eventId}/tickets/${ticketId}/`,
    data
  );
  return response.data;
};

export const deleteTicket = async (
  eventId: number,
  ticketId: number
) => {
  await api.delete(
    `/api/events/${eventId}/tickets/${ticketId}/`
  );
};