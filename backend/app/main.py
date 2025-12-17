import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from .api.admin.registrations import router as admin_registrations_router
from .api.admin.enrollments import router as admin_enrollments_router
from .api.admin.exports import router as admin_exports_router
from .api.auth import router as auth_router
from .api.exams import router as exams_router
from .api.payments import router as payments_router
from .api.content import router as content_router, admin_router as admin_content_router
from .core.dependencies import set_exam_repository, set_registration_repository, set_user_repository, set_content_repository
from .infrastructure.exam.repository import MongoDBExamRepository
from .infrastructure.registration.repository import MongoDBRegistrationRepository
from .infrastructure.user.repository import MongoDBUserRepository
from .infrastructure.content.repository import MongoDBContentRepository

# Load environment variables
load_dotenv()

# MongoDB connection
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "lifeschool_db")

client: AsyncIOMotorClient = None
db = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global client, db
    
    # Startup
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DATABASE_NAME]
    
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.exams.create_index("id", unique=True)
    await db.exam_registrations.create_index("id", unique=True)
    await db.exam_registrations.create_index([("user_id", 1), ("exam_id", 1)], unique=True)
    await db.exam_registrations.create_index("user_id")
    await db.content.create_index("id", unique=True)
    await db.content.create_index("content_type")
    await db.content.create_index("status")
    await db.content.create_index("created_at")
    
    # Set repositories
    user_repository = MongoDBUserRepository(db)
    set_user_repository(user_repository)
    
    exam_repository = MongoDBExamRepository(db)
    set_exam_repository(exam_repository)
    
    registration_repository = MongoDBRegistrationRepository(db)
    set_registration_repository(registration_repository)
    
    content_repository = MongoDBContentRepository(db)
    set_content_repository(content_repository)
    
    yield
    
    # Shutdown
    if client:
        client.close()


app = FastAPI(
    title="LifeSchool Exam Registration Platform",
    description="Sprint-1 to Sprint-7: Authentication, User Profile, Exam Management, Registration, Payments, Enrollment, CSV Export, CMS-Lite",
    version="7.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(exams_router)
app.include_router(admin_registrations_router)
app.include_router(admin_enrollments_router)
app.include_router(admin_exports_router)
app.include_router(payments_router)
app.include_router(content_router)
app.include_router(admin_content_router)
# Note: Registration endpoints are in exams.py (POST /exams/{exam_id}/register) 
# and auth.py (GET /auth/me/registrations) to match API requirements


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Radhe Radhe! 🙏 LifeSchool Exam Registration Platform API",
        "version": "7.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

