export interface Category {
  id: number;
  name: string;
  description: string;
}

export interface TicketType {
  id: number;
  event: number;
  name: string;
  price: string;
  quantity: number;
  available_quantity: number;
  created_at: string;
}

export interface Event {
  id: number;
  title: string;
  description: string;
  organizer: number;
  category: number;
  category_name: string;
  organizer_email: string;
  venue_name: string;
  location: string;
  start_datetime: string;
  end_datetime: string;
  status: string;
  ticket_types: TicketType[];
  created_at: string;
}