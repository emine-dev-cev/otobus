# 🚌 Bus Ticket Reservation System

A production-ready **microservices** bus ticket reservation application built with Python (FastAPI), PostgreSQL, Redis, Kafka, Docker, and Kubernetes.

---

## 🏗️ Architecture

```
Client
  │
  ▼
API Gateway (Nginx) — port 80
  │
  ├── /auth/*         → Auth Service       :8001
  ├── /users/*        → User Service       :8002
  ├── /trips/*        → Trip Service       :8003
  ├── /bookings/*     → Booking Service    :8004
  ├── /payments/*     → Payment Service    :8005
  └── /notifications/*→ Notification Svc  :8006
              │
      ┌───────┴────────┐
   PostgreSQL         Redis
              │
            Kafka
              │
    Notification Service (consumer)
```

---

## 🛠️ Tech Stack

| Layer         | Technology         |
|---------------|--------------------|
| Backend       | Python 3.11, FastAPI |
| Database      | PostgreSQL 15      |
| Cache         | Redis 7            |
| Message Queue | Apache Kafka       |
| Gateway       | Nginx              |
| Container     | Docker             |
| Orchestration | Kubernetes         |
| CI/CD         | GitHub Actions     |

---

## 📁 Project Structure

```
bus-ticket-app/
│
├── services/
│   ├── auth-service/          # JWT auth (register/login)
│   ├── user-service/          # User profile management
│   ├── trip-service/          # Bus trips & seat inventory
│   ├── booking-service/       # Ticket reservations
│   ├── payment-service/       # Mock payment processing
│   ├── notification-service/  # Email/SMS via Kafka events
│   └── api-gateway/           # Nginx reverse proxy
│
├── k8s/                       # Kubernetes manifests
│   ├── postgres.yaml
│   ├── redis.yaml
│   ├── kafka.yaml
│   ├── *-deployment.yaml      # Per-service deployments
│   └── ingress.yaml
│
├── docker-compose.yml         # Local development
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start (Local Dev)

### Prerequisites
- Docker Desktop
- Docker Compose v2

### 1. Clone the repository
```bash
git clone https://github.com/username/bus-ticket-app.git
cd bus-ticket-app
```

### 2. Start all services
```bash
docker-compose up --build
```

### 3. Access the APIs

| Service      | URL                              |
|--------------|----------------------------------|
| API Gateway  | http://localhost:80              |
| Auth Docs    | http://localhost:8001/docs       |
| User Docs    | http://localhost:8002/docs       |
| Trip Docs    | http://localhost:8003/docs       |
| Booking Docs | http://localhost:8004/docs       |
| Payment Docs | http://localhost:8005/docs       |
| Notify Docs  | http://localhost:8006/docs       |

---

## 🔄 End-to-End Flow

```
1. POST /auth/register      → Create account
2. POST /auth/login         → Get JWT token
3. GET  /trips?from=IST&to=ANK → Browse trips
4. POST /bookings           → Reserve a seat
   └── Kafka: booking.created
5. POST /payments           → Process payment
   └── Kafka: payment.success
6. Notification Service     → Sends confirmation email/SMS
```

---

## ☸️ Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace bus-ticket

# Apply all manifests
kubectl apply -f k8s/ -n bus-ticket

# Check pods
kubectl get pods -n bus-ticket

# Access via ingress
# Add to /etc/hosts: 127.0.0.1 bus-ticket.local
curl http://bus-ticket.local/auth/health
```

---

## 🔑 Environment Variables

Each service uses `.env` files. Example for Auth Service:

```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/auth_db
SECRET_KEY=your-super-secret-jwt-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://redis:6379
```

---

## 📡 API Reference

### Auth Service
| Method | Endpoint         | Description        |
|--------|------------------|--------------------|
| POST   | /auth/register   | Register new user  |
| POST   | /auth/login      | Login, get JWT     |
| POST   | /auth/refresh    | Refresh token      |
| GET    | /auth/health     | Health check       |

### Trip Service
| Method | Endpoint          | Description           |
|--------|-------------------|-----------------------|
| GET    | /trips            | List all trips        |
| GET    | /trips/{id}       | Trip details + seats  |
| POST   | /trips            | Create trip (admin)   |

### Booking Service
| Method | Endpoint          | Description        |
|--------|-------------------|--------------------|
| POST   | /bookings         | Create booking     |
| GET    | /bookings/me      | My bookings        |
| DELETE | /bookings/{id}    | Cancel booking     |

---

## 🧪 Testing

```bash
# Run tests for a specific service
cd services/auth-service
pip install -r requirements.txt
pytest tests/ -v
```

---

## 📜 Git Setup

```bash
git init
git add .
git commit -m "initial commit: microservices bus ticket app"
git branch -M main
git remote add origin https://github.com/username/bus-ticket-app.git
git push -u origin main
```

---

## 📄 License

MIT License — feel free to use and extend.
