# Quick Start Guide

**Radhe Radhe! 🙏**

This guide will help you get the LifeSchool platform up and running quickly.

## Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **MongoDB** (running locally or remote)

## Backend Setup (5 minutes)

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

5. **Start MongoDB** (if running locally):
```bash
mongod
# Or use MongoDB Atlas connection string in .env
```

6. **Run the backend:**
```bash
# Option 1: Using the run script
./run.sh

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

## Frontend Setup (3 minutes)

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Run specific test file:
```bash
pytest tests/auth/test_google_login.py
```

## Usage

1. **Open frontend:** `http://localhost:3000`
2. **Login:** Enter email and name (Google SSO is mocked)
3. **Complete Profile:** Add 10-digit mobile number
4. **View Profile:** See your complete profile

## API Testing

Use the Swagger UI at `http://localhost:8000/docs` to test API endpoints directly.

### Example API Calls:

**1. Login (Mock Google):**
```bash
curl -X POST "http://localhost:8000/auth/google" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "name": "Test User"}'
```

**2. Update Mobile (requires token):**
```bash
curl -X POST "http://localhost:8000/auth/mobile" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"mobile": "1234567890"}'
```

**3. Get Profile (requires token):**
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Troubleshooting

### Backend Issues

- **MongoDB Connection Error:** Make sure MongoDB is running or update `DATABASE_URL` in `.env`
- **Port Already in Use:** Change port in `uvicorn` command or `.env`
- **Import Errors:** Make sure virtual environment is activated

### Frontend Issues

- **API Connection Error:** Make sure backend is running on port 8000
- **CORS Errors:** Check backend CORS settings in `app/main.py`
- **Build Errors:** Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

## Project Structure

```
lifeSchool app/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── domain/      # Domain entities
│   │   ├── application/ # Application services
│   │   ├── infrastructure/ # MongoDB implementation
│   │   ├── api/         # FastAPI routes
│   │   └── core/        # Security, dependencies
│   ├── tests/           # Test files
│   └── requirements.txt
│
└── frontend/            # React frontend
    ├── src/
    │   ├── components/  # React components
    │   ├── contexts/    # Auth context
    │   ├── pages/       # Page components
    │   └── services/    # API service
    └── package.json
```

## Next Steps

- Review the code structure
- Run tests to verify everything works
- Customize as needed for your requirements

**Radhe Radhe! 🙏**

