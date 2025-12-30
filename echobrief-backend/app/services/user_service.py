from datetime import datetime, timezone
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.security import hash_password, verify_password
from ..models.topics import Topic
from ..models.users import User, UserTopic
from ..schemas.users import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

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

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update user profile"""
        user = await self.get_user_by_id(user_id)

        update_data = user_data.model_dump(exclude_unset=True)

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
        user = await self.get_user_by_id(user_id)
        current_topics = await self.get_user_topics(user_id)
        if user.plan_type == "free" and len(current_topics) >= 1:
            raise HTTPException(
                status_code=400,
                detail="Free plan limited to 1 topic. Upgrade to add more topics.",
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

    async def get_all_users(self) -> Sequence[User]:
        """Get all users (admin only)"""
        query = select(User)
        result = await self.session.exec(query)
        return result.all()
