# 🚀 How to Start LifeSchool Platform

**Radhe Radhe! 🙏**

## Quick Start (Easiest Method)

### Option 1: Using the Startup Scripts

**Terminal 1 - Backend:**
```bash
./start_backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start_frontend.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Troubleshooting

### Backend Issues

1. **MongoDB not running:**
   ```bash
   # Check if MongoDB is running
   mongosh --eval "db.adminCommand('ping')"
   
   # If not running, start MongoDB:
   mongod
   # Or use MongoDB Atlas connection string in .env
   ```

2. **Virtual environment not activated:**
   ```bash
   cd backend
   source venv/bin/activate
   ```

3. **Dependencies not installed:**
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Port 8000 already in use:**
   - Stop the process using port 8000, or
   - Change port in the uvicorn command

### Frontend Issues

1. **Dependencies not installed:**
   ```bash
   cd frontend
   npm install
   ```

2. **Port 3000 already in use:**
   - Vite will automatically use the next available port

3. **Backend not running:**
   - Make sure backend is running on port 8000
   - Check backend logs for errors

## Testing

Run backend tests:
```bash
cd backend
source venv/bin/activate
pytest
```

## What to Expect

1. **Backend starts successfully:**
   - You'll see: "Application startup complete"
   - "Uvicorn running on http://0.0.0.0:8000"

2. **Frontend starts successfully:**
   - You'll see: "Local: http://localhost:3000"
   - Browser should open automatically

3. **First Login:**
   - Enter any email and name
   - You'll get a JWT token
   - Then add your 10-digit mobile number

## Need Help?

Check the logs in the terminal windows for error messages. Common issues:
- MongoDB connection errors → Start MongoDB
- Import errors → Install dependencies
- Port conflicts → Stop other services using ports 8000/3000

**Radhe Radhe! 🙏**

