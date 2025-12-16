# LifeSchool Exam Registration Platform - Backend

**Radhe Radhe! 🙏**

Backend API for the LifeSchool exam registration platform, implementing Sprint-1: Authentication & User Profile.

## Architecture

This project follows **Clean Architecture** principles:

- **Domain Layer**: Core business entities and repository interfaces (framework-agnostic)
- **Application Layer**: Use cases and DTOs
- **Infrastructure Layer**: MongoDB implementation, external services
- **API Layer**: FastAPI routes (thin controllers)

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB (via Motor)
- **Authentication**: JWT (HS256)
- **Testing**: pytest + pytest-asyncio

## Setup

### Prerequisites

- Python 3.10+
- MongoDB (running locally or remote)
- pip

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start MongoDB (if running locally):
```bash
mongod
```

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

### POST /auth/google
Mock Google login endpoint.

**Request:**
```json
{
  "email": "user@example.com",
  "name": "User Name"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "mobile": null,
    "role": "USER",
    "created_at": "2024-01-01T00:00:00",
    "is_profile_complete": false
  }
}
```

### POST /auth/mobile
Update user's mobile number (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "mobile": "1234567890"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "mobile": "1234567890",
  "role": "USER",
  "created_at": "2024-01-01T00:00:00",
  "is_profile_complete": true
}
```

### GET /auth/me
Get current user's profile (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "mobile": "1234567890",
  "role": "USER",
  "created_at": "2024-01-01T00:00:00",
  "is_profile_complete": true
}
```

## Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Project Structure

```
backend/
├── app/
│   ├── domain/           # Domain entities and interfaces
│   │   └── user/
│   ├── application/      # Application services and DTOs
│   │   └── user/
│   ├── infrastructure/   # MongoDB implementation
│   │   └── user/
│   ├── api/              # FastAPI routes
│   │   └── auth.py
│   ├── core/             # Security, dependencies
│   └── main.py           # FastAPI app
├── tests/                # Test files
│   └── auth/
├── requirements.txt
├── pytest.ini
└── README.md
```

## Development Principles

1. **TDD**: Tests written before or alongside implementation
2. **Clean Architecture**: Domain layer is framework-agnostic
3. **No Business Logic in Controllers**: All logic in application/domain layers
4. **Unit Testable**: All code testable without FastAPI
5. **Minimal but Extensible**: Code is simple but allows for future growth

## Notes

- Google SSO is currently mocked (no real Google API integration)
- JWT tokens expire after 30 days
- Mobile number must be exactly 10 digits
- Profile is considered complete only after mobile number is provided

## License

Private project - LifeSchool Platform

