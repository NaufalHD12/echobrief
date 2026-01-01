#!/usr/bin/env python3
"""
Script to create an admin user for EchoBrief.
Usage: python scripts/create_admin_user.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import async_session
from app.models.users import UserRole
from app.services.user_service import UserService
from app.schemas.users import UserCreate


async def create_admin_user():
    """Create admin user with default credentials"""

    # Default admin credentials
    email = "admin@echobrief.com"
    username = "admin"
    password = "Admin123"  # Change this in production!

    print(f"Creating admin user: {email}")

    async with async_session() as session:
        user_service = UserService(session)

        # Check if admin already exists
        existing_user = await user_service.get_user_by_email(email)
        if existing_user:
            print(f"Admin user {email} already exists!")
            return

        # Create admin user
        admin_data = UserCreate(
            email=email,
            username=username,
            password=password
        )

        admin_user = await user_service.create_user(admin_data)

        # Update role to admin
        admin_user.role = UserRole.ADMIN.value
        session.add(admin_user)
        await session.commit()

        print("✅ Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("⚠️  CHANGE THE PASSWORD AFTER FIRST LOGIN!")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
