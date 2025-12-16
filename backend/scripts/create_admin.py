#!/usr/bin/env python3
"""
Script to create an admin user in the database.
Radhe Radhe! 🙏

Usage:
    python scripts/create_admin.py
    python scripts/create_admin.py --email admin@example.com --name "Admin User"
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.domain.user.entity import User, UserRole
from app.infrastructure.user.repository import MongoDBUserRepository
from app.infrastructure.user.mapper import UserMapper


async def create_admin_user(email: str = None, name: str = None, mobile: str = None):
    """Create an admin user in the database."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "lifeschool_db")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Create repository
        user_repository = MongoDBUserRepository(db)
        
        # Get user input if not provided
        if not email:
            email = input("Enter admin email: ").strip()
        if not name:
            name = input("Enter admin name: ").strip()
        if not mobile:
            mobile_input = input("Enter admin mobile (10 digits, optional): ").strip()
            mobile = mobile_input if mobile_input else None
        
        # Validate email
        if not email or "@" not in email:
            print("❌ Invalid email address")
            return False
        
        # Validate mobile if provided
        if mobile:
            mobile_clean = mobile.replace(" ", "").replace("-", "")
            if not mobile_clean.isdigit() or len(mobile_clean) != 10:
                print("❌ Mobile number must be exactly 10 digits")
                return False
            mobile = mobile_clean
        
        # Check if user already exists
        existing_user = await user_repository.get_by_email(email)
        if existing_user:
            print(f"⚠️  User with email {email} already exists!")
            
            # Update to admin if not already admin
            if existing_user.role != UserRole.ADMIN:
                update_choice = input(f"  Current role: {existing_user.role.value}. Update to ADMIN? (y/n): ").strip().lower()
                if update_choice == 'y':
                    existing_user.role = UserRole.ADMIN
                    if mobile and not existing_user.mobile:
                        existing_user.update_mobile(mobile)
                    await user_repository.update(existing_user)
                    print(f"✅ User {email} updated to ADMIN role")
                    return True
                else:
                    print("❌ Operation cancelled")
                    return False
            else:
                print(f"✅ User {email} is already an ADMIN")
                return True
        
        # Create new admin user
        admin_user = User(
            email=email,
            name=name,
            mobile=mobile,
            role=UserRole.ADMIN,
        )
        
        await user_repository.create(admin_user)
        
        print(f"\n✅ Admin user created successfully!")
        print(f"   Email: {admin_user.email}")
        print(f"   Name: {admin_user.name}")
        print(f"   Role: {admin_user.role.value}")
        print(f"   Mobile: {admin_user.mobile or 'Not set'}")
        print(f"   ID: {admin_user.id}")
        print(f"\n📝 You can now login with this email to access admin features.")
        
        return True
        
    except ValueError as e:
        print(f"❌ Validation error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        client.close()


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create an admin user in the database")
    parser.add_argument("--email", help="Admin email address")
    parser.add_argument("--name", help="Admin name")
    parser.add_argument("--mobile", help="Admin mobile number (10 digits)")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("Create Admin User")
    print("Radhe Radhe! 🙏")
    print("=" * 50)
    print()
    
    result = asyncio.run(create_admin_user(
        email=args.email,
        name=args.name,
        mobile=args.mobile
    ))
    
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()


