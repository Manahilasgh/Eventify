import api from "@/lib/api";
import type { Booking } from "@/types/booking";

interface BookingData {
  ticket_type: number;
  quantity: number;
}

export const createBooking = async (
  data: BookingData
): Promise<Booking> => {
  const response = await api.post("/api/bookings/", data);
  return response.data;
};

export const getMyBookings = async (): Promise<Booking[]> => {
  const response = await api.get("/api/bookings/my-bookings/");
  return response.data;
};

export const cancelBooking = async (id: number) => {
  const response = await api.put(`/api/bookings/${id}/cancel/`);
  return response.data;
};