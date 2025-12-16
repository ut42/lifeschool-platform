#!/usr/bin/env python3
"""
Quick setup test script for LifeSchool Platform
Radhe Radhe! 🙏
"""

import sys
import subprocess
import asyncio
from pathlib import Path

def test_backend():
    """Test backend setup."""
    print("🔍 Testing Backend Setup...")
    
    backend_path = Path(__file__).parent / "backend"
    venv_python = backend_path / "venv" / "bin" / "python"
    
    if not venv_python.exists():
        print("❌ Backend virtual environment not found!")
        print("   Run: cd backend && python3 -m venv venv")
        return False
    
    # Test imports
    try:
        result = subprocess.run(
            [str(venv_python), "-c", "from app.main import app; print('✅ Backend imports OK')"],
            capture_output=True,
            text=True,
            cwd=str(backend_path)
        )
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print(f"❌ Backend import failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_frontend():
    """Test frontend setup."""
    print("\n🔍 Testing Frontend Setup...")
    
    frontend_path = Path(__file__).parent / "frontend"
    node_modules = frontend_path / "node_modules"
    
    if not node_modules.exists():
        print("⚠️  Frontend dependencies not installed")
        print("   Run: cd frontend && npm install")
        return False
    
    print("✅ Frontend dependencies found")
    return True

async def test_mongodb():
    """Test MongoDB connection."""
    print("\n🔍 Testing MongoDB Connection...")
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
        await client.admin.command('ping')
        client.close()
        print("✅ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   Make sure MongoDB is running: mongod")
        return False

def main():
    print("=" * 50)
    print("LifeSchool Platform - Setup Test")
    print("Radhe Radhe! 🙏")
    print("=" * 50)
    print()
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    mongodb_ok = asyncio.run(test_mongodb())
    
    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Backend:  {'✅ OK' if backend_ok else '❌ FAIL'}")
    print(f"  Frontend: {'✅ OK' if frontend_ok else '❌ FAIL'}")
    print(f"  MongoDB:  {'✅ OK' if mongodb_ok else '❌ FAIL'}")
    print("=" * 50)
    
    if backend_ok and frontend_ok and mongodb_ok:
        print("\n🎉 All checks passed! You're ready to start the servers.")
        print("\nTo start:")
        print("  Terminal 1: ./start_backend.sh")
        print("  Terminal 2: ./start_frontend.sh")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

