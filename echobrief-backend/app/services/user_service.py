from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from pathlib import Path

from ..core.security import hash_password, verify_password
from ..models.topics import Topic
from ..models.users import User, UserTopic
from ..schemas.users import UserCreate, UserUpdate
from .avatar_service import AvatarService
from .subscription_service import SubscriptionService


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.avatar_service = AvatarService()

    async def get_user_by_id(self, user_id: UUID) -> User:
        """Get user by ID"""
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email"""
        query = select(User).where(User.email == email)
        result = await self.session.exec(query)
        return result.first()

    async def get_user_by_username(self, username: str) -> User | None:
        """Get user by username"""
        query = select(User).where(User.username == username)
        result = await self.session.exec(query)
        return result.first()

    async def get_user_by_google_id(self, google_id: str) -> User | None:
        """Get user by Google ID"""
        query = select(User).where(User.google_id == google_id)
        result = await self.session.exec(query)
        return result.first()

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user"""
        # Check if email already exists
        if await self.get_user_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        # Check if username already exists
        if await self.get_user_by_username(user_data.username):
            raise HTTPException(status_code=400, detail="Username already taken")

        # Create user
        hashed_password = hash_password(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def create_oauth_user(self, google_id: str, email: str, name: str) -> User:
        """Create new user from OAuth provider"""
        # Check if email already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Check if Google ID already exists
        if await self.get_user_by_google_id(google_id):
            raise HTTPException(status_code=400, detail="Google account already linked")

        # Generate unique username from name
        base_username = name.lower().replace(' ', '_').replace('-', '_')
        username = base_username
        counter = 1
        while await self.get_user_by_username(username):
            username = f"{base_username}_{counter}"
            counter += 1

        # Create user
        user = User(
            email=email,
            username=username,
            google_id=google_id,
            auth_provider="google",
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_or_create_oauth_user(self, google_id: str, email: str, name: str, picture_url: str | None = None) -> User:
        """Get existing OAuth user or create new one"""
        # Try to find by Google ID first
        user = await self.get_user_by_google_id(google_id)
        if user:
            return user

        # Try to find by email (might be existing user wanting to link Google)
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            # Link Google account to existing user
            if existing_user.google_id:
                raise HTTPException(status_code=400, detail="Google account already linked to another user")
            existing_user.google_id = google_id
            existing_user.auth_provider = "google"  # Update to indicate OAuth capability
            self.session.add(existing_user)
            await self.session.commit()
            await self.session.refresh(existing_user)
            return existing_user

        # Create new OAuth user
        user = await self.create_oauth_user(google_id, email, name)

        # Try to download Google avatar if available
        if picture_url:
            try:
                avatar_filename = await self.avatar_service.download_google_avatar(user.id, picture_url)
                if avatar_filename:
                    user.avatar_filename = avatar_filename
                    self.session.add(user)
                    await self.session.commit()
            except Exception:
                # Ignore avatar download errors, user still created successfully
                pass

        return user

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not user.password_hash or not verify_password(password, user.password_hash):
            return None
        return user

    async def update_user_profile(
        self, user_id: UUID, user_data: UserUpdate
    ) -> User:
        """Update user profile (self-update, limited fields)"""
        user = await self.get_user_by_id(user_id)

        update_data = user_data.model_dump(exclude_unset=True)

        # Regular users can only update username
        allowed_fields = {"username"}
        if not set(update_data.keys()).issubset(allowed_fields):
            raise HTTPException(
                status_code=403, detail="Regular users can only update username"
            )

        # Check username uniqueness if being updated
        if "username" in update_data:
            existing = await self.get_user_by_username(update_data["username"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=400, detail="Username already taken")

        user.sqlmodel_update(update_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user_admin(
        self, user_id: UUID, user_data: UserUpdate
    ) -> User:
        """Update user profile (admin operation, all fields allowed)"""
        user = await self.get_user_by_id(user_id)

        update_data = user_data.model_dump(exclude_unset=True)

        # Check username uniqueness if being updated
        if "username" in update_data:
            existing = await self.get_user_by_username(update_data["username"])
            if existing and existing.id != user_id:
                raise HTTPException(status_code=400, detail="Username already taken")

        # Validate plan_type values
        if "plan_type" in update_data:
            if update_data["plan_type"] not in ["free", "paid"]:
                raise HTTPException(
                    status_code=400, detail="plan_type must be 'free' or 'paid'"
                )

        # Validate role values
        if "role" in update_data:
            if update_data["role"] not in ["user", "admin"]:
                raise HTTPException(
                    status_code=400, detail="role must be 'user' or 'admin'"
                )

        user.sqlmodel_update(update_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user(
        self, user_id: UUID, user_data: UserUpdate, current_user: User | None = None
    ) -> User:
        """Legacy method - kept for backward compatibility"""
        # Determine if this is an admin operation
        is_admin = current_user and current_user.role == "admin"

        if is_admin:
            return await self.update_user_admin(user_id, user_data)
        else:
            # For self-update, ensure user can only update their own profile
            if current_user and current_user.id != user_id:
                raise HTTPException(
                    status_code=403, detail="Cannot update another user's profile"
                )
            return await self.update_user_profile(user_id, user_data)

    async def update_last_login(self, user_id: UUID) -> None:
        """Update user's last login timestamp"""
        user = await self.get_user_by_id(user_id)
        user.last_login = datetime.now(timezone.utc)
        self.session.add(user)
        await self.session.commit()

    async def get_user_topics(self, user_id: UUID) -> Sequence[Topic]:
        """Get topics selected by user"""
        query = select(Topic).join(UserTopic).where(UserTopic.user_id == user_id)
        result = await self.session.exec(query)
        return result.all()

    async def add_user_topic(self, user_id: UUID, topic_id: int) -> None:
        """Add topic to user's selection"""
        # Validate topic exists
        topic = await self.session.get(Topic, topic_id)
        if not topic:
            raise HTTPException(status_code=400, detail="Topic not found")

        # Check if already selected
        query = select(UserTopic).where(
            UserTopic.user_id == user_id, UserTopic.topic_id == topic_id
        )
        result = await self.session.exec(query)
        if result.first():
            raise HTTPException(status_code=400, detail="Topic already selected")

        # Check plan limits
        subscription_service = SubscriptionService(self.session)
        effective_plan = await subscription_service.get_user_plan_type(user_id)
        current_topics = await self.get_user_topics(user_id)
        if effective_plan == "free" and len(current_topics) >= 3:
            raise HTTPException(
                status_code=400,
                detail="Free plan limited to 3 topics. Upgrade to add more topics.",
            )

        # Add topic
        user_topic = UserTopic(user_id=user_id, topic_id=topic_id)
        self.session.add(user_topic)
        await self.session.commit()

    async def remove_user_topic(self, user_id: UUID, topic_id: int) -> None:
        """Remove topic from user's selection"""
        query = select(UserTopic).where(
            UserTopic.user_id == user_id, UserTopic.topic_id == topic_id
        )
        result = await self.session.exec(query)
        user_topic = result.first()
        if not user_topic:
            raise HTTPException(status_code=400, detail="Topic not selected")

        await self.session.delete(user_topic)
        await self.session.commit()

    async def get_all_users(self, search: str | None = None, skip: int = 0, limit: int = 10) -> tuple[Sequence[User], int]:
        """Get all users (admin only) with optional search"""
        query = select(User)

        if search:
            search_lower = search.lower()
            # Search in username and email using case-insensitive comparison
            query = query.where(
                (func.lower(User.username).like(f"%{search_lower}%")) |
                (func.lower(User.email).like(f"%{search_lower}%"))
            )

        # Get total count
        total_result = await self.session.exec(
            select(func.count()).select_from(query.subquery())
        )
        total = total_result.one()

        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await self.session.exec(query)
        return result.all(), total

    async def get_user_avatar_url(self, user_id: UUID) -> str:
        """Get user avatar URL"""
        user = await self.get_user_by_id(user_id)

        if user.avatar_filename:
            return f"/avatars/{user_id}/{user.avatar_filename}"
        else:
            # Generate default avatar if not exists
            filename = self.avatar_service.save_default_avatar(user_id, user.username)
            # Update user with default avatar filename
            user.avatar_filename = filename
            self.session.add(user)
            await self.session.commit()
            return f"/avatars/{user_id}/{filename}"

    async def upload_user_avatar(self, user_id: UUID, file_path: str, filename: str) -> str:
        """Upload user avatar"""
        # Validate file
        if not self.avatar_service.validate_image_file(Path(file_path)):
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Generate new filename with timestamp
        import time
        timestamp = int(time.time())
        ext = filename.split('.')[-1].lower()
        new_filename = f"upload_{timestamp}.{ext}"

        # Move file to avatar directory
        user_dir = self.avatar_service._get_user_avatar_dir(user_id)
        new_filepath = user_dir / new_filename

        import shutil
        shutil.move(file_path, new_filepath)

        # Update user avatar filename
        user = await self.get_user_by_id(user_id)
        user.avatar_filename = new_filename
        self.session.add(user)
        await self.session.commit()

        return f"/avatars/{user_id}/{new_filename}"

    async def delete_user_avatar(self, user_id: UUID) -> None:
        """Delete user avatar (back to default)"""
        user = await self.get_user_by_id(user_id)

        if user.avatar_filename and not user.avatar_filename.startswith('default_'):
            # Delete file
            self.avatar_service.delete_avatar(user_id, user.avatar_filename)

            # Reset to default
            filename = self.avatar_service.save_default_avatar(user_id, user.username)
            user.avatar_filename = filename
            self.session.add(user)
            await self.session.commit()
