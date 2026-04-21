# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-21

### Added
- Initial microservices architecture for the Bus Ticket App.
- Auth service with JWT authentication.
- Trip service for managing bus schedules and seat inventory.
- Booking service for ticket reservations.
- Payment service with mock credit card processing.
- Notification service for email alerts.
- API Gateway (Nginx) for centralized routing.
- Frontend React-like vanilla JS interface.
- GitHub Actions CI/CD pipeline.
- Docker Compose orchestration for local development.

### Fixed
- Authentication failure caused by missing environment containers (Postgres, Redis, Kafka).
- JSON parsing error on frontend due to backend 500/HTML error pages.
- DNS resolution issue in Nginx after container restarts.
- `AttributeError` in `trip-service` WebSocket manager (`broadcast` vs `broadcast_trip_update`).
- JWT expiration extended to 24 hours to prevent frequent session timeouts during development.

### Changed
- Standardized Kafka bootstrap server hostnames to `kafka:29092`.
- Added host-to-container volume mappings for all microservices to enable hot-reloading.
- Renamed default branch from `master` to `main`.
