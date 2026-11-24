export interface Booking {
  id: number;
  event_id: number;
  event_title: string;
  ticket_type: number;
  ticket_type_name: string;
  quantity: number;
  total_price: string;
  status: "confirmed" | "cancelled";
  created_at: string;
}