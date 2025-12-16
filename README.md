# LifeSchool Exam Registration Platform

**Radhe Radhe! 🙏**

Full-stack exam registration platform with separate frontend and backend codebases.

## Project Structure

```
lifeSchool app/
├── backend/          # FastAPI backend (Clean Architecture)
├── frontend/         # React frontend (Vite)
└── README.md         # This file
```

## Quick Start

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start MongoDB (if running locally):
```bash
mongod
```

5. Run the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend: `http://localhost:3000`

## Architecture

### Backend
- **Clean Architecture** (Domain / Application / Infrastructure / API)
- **FastAPI** + **Motor** + **MongoDB**
- **JWT** authentication
- **TDD** approach with pytest

### Frontend
- **React 18** with **Vite**
- **React Router** for navigation
- **Axios** for API calls
- Modern, responsive UI

## Features (Sprint-1)

✅ Mock Google SSO login
✅ User creation on first login
✅ JWT token authentication
✅ Mobile number update (10-digit validation)
✅ Profile completion tracking
✅ Protected routes

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Test Coverage

```bash
pytest --cov=app --cov-report=html
```

## API Endpoints

- `POST /auth/google` - Mock Google login
- `POST /auth/mobile` - Update mobile number (auth required)
- `GET /auth/me` - Get current user profile (auth required)

See `backend/README.md` for detailed API documentation.

## Development Notes

- Google SSO is mocked (no real Google API integration)
- MongoDB required for backend
- JWT tokens expire after 30 days
- Mobile number must be exactly 10 digits

## License

Private project - LifeSchool Platform

---

**Radhe Radhe! 🙏**

