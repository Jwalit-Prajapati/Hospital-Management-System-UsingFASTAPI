# 🏥 Hospital Management System

A RESTful **Healthcare Appointment System API** built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**. It provides role-based management of patients, doctors, appointments, doctor availability, and medical records, secured with JWT authentication.

## ✨ Features

- **JWT Authentication** — Register/login with hashed passwords (bcrypt) and bearer-token protected routes.
- **Role-based Access** — `Admin`, `Doctor`, `Patient`, and `Staff` roles, with appointment visibility scoped per role.
- **Patient Management** — Create, read, update, delete, and search patient records.
- **Doctor Management** — CRUD for doctors, filter by specialization, and manage weekly availability slots.
- **Appointment Scheduling** — Book appointments with automatic doctor-availability and time-conflict checks, status tracking (`Scheduled`, `Confirmed`, `Cancelled`, `Completed`, `No Show`), and available-slot lookup.
- **Email Notifications** — Automated emails for appointment scheduling, rescheduling, and cancellation using `fastapi-mail`.
- **Medical Records** — Store diagnosis, treatment, and prescription notes linked to patients and appointments.
- **Redis Caching** — High-performance caching of frequently accessed data to reduce database load.
- **Rate Limiting** — API rate limiting to prevent abuse and ensure service availability.
- **Auto-generated API docs** — Interactive Swagger UI and ReDoc via FastAPI.
- **Health check endpoint** — Verify API and database connectivity.

## 🛠 Tech Stack

| Layer          | Technology                                  |
|----------------|----------------------------------------------|
| Framework      | [FastAPI](https://fastapi.tiangolo.com/)     |
| Language       | Python 3.11+                                 |
| Database       | PostgreSQL                                   |
| Cache          | Redis                                        |
| ORM            | SQLAlchemy                                   |
| Validation     | Pydantic / pydantic-settings                 |
| Auth           | JWT (`python-jose`) + `passlib[bcrypt]`      |
| Email          | `fastapi-mail`                               |
| Migrations     | Alembic                                      |
| Server         | Uvicorn                                      |

## 📁 Project Structure

```
Hospital Management/
└── Backend/
    ├── app/
    │   ├── api/
    │   │   ├── deps.py              # Auth & role dependencies
    │   │   └── routes/
    │   │       ├── auth.py          # Login, register, /me
    │   │       ├── patient.py       # Patient CRUD + search
    │   │       ├── doctor.py        # Doctor CRUD + availability
    │   │       └── appointment.py   # Appointment CRUD + slots
    │   ├── core/
    │   │   ├── cache.py             # Redis caching configuration
    │   │   ├── config.py            # App settings (env-based)
    │   │   ├── email.py             # Email notification service
    │   │   ├── rate_limiter.py      # API rate limiting logic
    │   │   └── security.py          # Password hashing, JWT creation
    │   ├── crud/                    # Database access layer
    │   │   ├── crud_base.py         # Generic CRUD base class
    │   │   ├── crud_user.py         # User queries & authentication
    │   │   ├── crud_patient.py      # Patient queries
    │   │   ├── crud_doctor.py       # Doctor & availability queries
    │   │   └── crud_appointment.py  # Appointment queries & conflict checks
    │   ├── db/
    │   │   ├── models.py            # SQLAlchemy models
    │   │   └── session.py           # DB engine/session
    │   ├── schemas/                 # Pydantic request/response schemas
    │   └── main.py                  # FastAPI app entrypoint
    └── requirements.txt
```

## 🗂 Data Model

| Model            | Description                                                              |
|-------------------|---------------------------------------------------------------------------|
| `User`            | Login identity with `role` (Admin/Doctor/Patient/Staff) and hashed password |
| `Patient`         | Personal, contact, and insurance details                                |
| `Doctor`          | Profile, specialization, and linked availability slots                  |
| `Availability`    | Doctor's weekly recurring time slots                                    |
| `Appointment`     | Links a patient and doctor with a time range and status                 |
| `MedicalRecord`   | Diagnosis, treatment, and prescriptions tied to a patient/appointment   |

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (running instance + an empty database)
- Redis (running instance for caching and rate limiting)

### 1. Clone the repository

```bash
git clone <repository-url>
cd "Hospital Management/Backend"
```

### 2. Create a virtual environment & install dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file inside `Backend/`:

```env
POSTGRES_SERVER=localhost:5432
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=hospital_management

SECRET_KEY=your_super_secret_key

REDIS_URL=redis://localhost:6379/0

MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=your_email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=Hospital Management System
```

> `SECRET_KEY` is used to sign JWT access tokens — generate a strong random value for production (e.g. `openssl rand -hex 32`).

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

Tables are created automatically on startup via SQLAlchemy metadata.

The API will be available at **http://localhost:8000**.

## 📖 API Documentation

Once running, interactive documentation is available at:

- **Swagger UI** — `http://localhost:8000/docs`
- **ReDoc** — `http://localhost:8000/redoc`
- **OpenAPI schema** — `http://localhost:8000/openapi.json`
- **Health check** — `http://localhost:8000/health`

## 🔑 Authentication

All routes except `/api/v1/auth/login` and `/api/v1/auth/register` require a bearer token.

1. Register a user: `POST /api/v1/auth/register`
2. Log in to obtain a token: `POST /api/v1/auth/login`
3. Pass the token on subsequent requests:

```
Authorization: Bearer <access_token>
```

## 🔗 Key Endpoints

| Method | Endpoint                                              | Description                          |
|--------|--------------------------------------------------------|---------------------------------------|
| POST   | `/api/v1/auth/register`                                | Register a new user                  |
| POST   | `/api/v1/auth/login`                                    | Log in and receive a JWT             |
| GET    | `/api/v1/auth/me`                                       | Get the current authenticated user   |
| GET    | `/api/v1/patients/`                                     | List patients                        |
| POST   | `/api/v1/patients/`                                     | Create a patient                     |
| GET    | `/api/v1/patients/{id}`                                 | Get patient by ID                    |
| PUT    | `/api/v1/patients/{id}`                                 | Update a patient                     |
| DELETE | `/api/v1/patients/{id}`                                 | Delete a patient                     |
| GET    | `/api/v1/patients/search`                               | Search patients                      |
| GET    | `/api/v1/doctors/`                                      | List doctors                         |
| POST   | `/api/v1/doctors/`                                      | Create a doctor                      |
| GET    | `/api/v1/doctors/{id}`                                  | Get doctor with availability         |
| PUT    | `/api/v1/doctors/{id}`                                  | Update a doctor                      |
| DELETE | `/api/v1/doctors/{id}`                                  | Delete a doctor                      |
| POST   | `/api/v1/doctors/{id}/availability`                     | Add doctor availability slot         |
| GET    | `/api/v1/doctors/specialization/{specialization}`       | Filter doctors by specialization     |
| GET    | `/api/v1/appointments/`                                 | List appointments (scoped by role)   |
| POST   | `/api/v1/appointments/`                                 | Book an appointment                  |
| GET    | `/api/v1/appointments/{id}`                              | Get appointment details              |
| PUT    | `/api/v1/appointments/{id}`                              | Update an appointment                |
| DELETE | `/api/v1/appointments/{id}`                              | Cancel/delete an appointment         |
| PUT    | `/api/v1/appointments/{id}/status`                       | Update appointment status            |
| GET    | `/api/v1/appointments/doctor/{doctor_id}/available-slots`| Get a doctor's open slots on a date |

