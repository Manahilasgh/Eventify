# Eventify — Event Ticketing & Booking Platform

Eventify is a full-stack event management and ticket booking platform built with Django REST Framework, Next.js, and PostgreSQL. It allows customers to discover events and book tickets, while approved organizers can create events, manage ticket types, and control ticket availability.

## Features

### Customer
- User registration and JWT authentication
- Browse and filter published events
- View event details and ticket availability
- Book tickets with automatic price calculation
- View booking history and cancel bookings
- Apply to become an event organizer

### Organizer
- Organizer dashboard
- Create, edit, delete, and publish events
- Create and manage custom ticket types
- Monitor booked and available ticket quantities

### Admin
- Approve or reject organizer applications
- Manage users, events, categories, and bookings through Django Admin

### Backend
- RESTful API architecture
- Custom email-based user model
- JWT access and refresh tokens
- Role-based access control
- Object-level permissions
- Database transactions and row-level locking
- Overbooking prevention
- Automatic ticket availability management
- Data validation and protected database relationships

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Styling | Tailwind CSS |
| Backend | Django, Django REST Framework |
| Database | PostgreSQL |
| Authentication | Simple JWT |
| API Client | Axios |
| State Management | React Context API |
| Dependency Management | Pipenv, npm |
| Version Control | Git, GitHub |

## Project Structure

```text
Eventify/
├── apps/
│   ├── accounts/
│   ├── events/
│   └── bookings/
├── config/
├── frontend/
│   └── src/
│       ├── app/
│       ├── components/
│       ├── lib/
│       └── types/
├── manage.py
├── Pipfile
├── Pipfile.lock
├── .env.example
├── .gitignore
└── README.md
```

## Local Installation

### Prerequisites

- Python
- Pipenv
- PostgreSQL
- Node.js 20+
- npm

### Backend Setup

Clone the repository and navigate to the project directory.

```bash
git clone <repository-url>
cd Eventify
pipenv install
```

Create a PostgreSQL database named `eventify_db`.

Copy the environment configuration:

```bash
cp .env.example .env
```

Update the environment variables with your PostgreSQL credentials and Django secret key.

Apply migrations and create an admin account:

```bash
pipenv run python manage.py migrate
pipenv run python manage.py createsuperuser
```

Start the backend server:

```bash
pipenv run python manage.py runserver
```

Backend: http://127.0.0.1:8000

Admin panel: http://127.0.0.1:8000/admin/

Create event categories through Django Admin before creating events.

### Frontend Setup

```bash
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

Frontend: http://localhost:3000

## API Endpoints

### Authentication

| Method | Endpoint |
|---|---|
| POST | /api/auth/register/ |
| POST | /api/auth/login/ |
| POST | /api/auth/refresh/ |
| GET | /api/auth/me/ |
| POST | /api/auth/apply-organizer/ |

### Events

| Method | Endpoint |
|---|---|
| GET | /api/events/ |
| POST | /api/events/ |
| GET | /api/events/categories/ |
| GET | /api/events/my-events/ |
| GET | /api/events/{id}/ |
| PATCH | /api/events/{id}/ |
| DELETE | /api/events/{id}/ |
| POST | /api/events/{id}/publish/ |

### Tickets

| Method | Endpoint |
|---|---|
| GET | /api/events/{event_id}/tickets/ |
| POST | /api/events/{event_id}/tickets/ |
| PATCH | /api/events/{event_id}/tickets/{ticket_id}/ |
| DELETE | /api/events/{event_id}/tickets/{ticket_id}/ |

### Bookings

| Method | Endpoint |
|---|---|
| POST | /api/bookings/ |
| GET | /api/bookings/my-bookings/ |
| GET | /api/bookings/{id}/ |
| PATCH | /api/bookings/{id}/cancel/ |

## Application Workflow

1. A user registers as a customer.
2. The customer can browse events and book available tickets.
3. A customer can submit an organizer application.
4. An admin reviews and approves the application.
5. The approved organizer creates an event and adds ticket types.
6. The organizer publishes the event.
7. Customers book tickets for the published event.
8. Ticket availability decreases after successful bookings and is restored when bookings are cancelled.

## Testing

Backend:

```bash
pipenv run python manage.py check
pipenv run python manage.py test
```

Frontend:

```bash
cd frontend
npx tsc --noEmit
npm run build
```

## Project Scope

Eventify is a learning-focused full-stack application demonstrating Django REST Framework, database relationships, authentication, authorization, transaction management, and frontend-backend integration.

Real payment processing is outside the current project scope.