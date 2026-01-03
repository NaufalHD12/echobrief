import hashlib
import os
from pathlib import Path
from typing import Optional
from uuid import UUID

import httpx
from PIL import Image


class AvatarService:
    """Service for handling user avatars"""

    def __init__(self):
        self.avatar_dir = Path("avatar")
        self.avatar_dir.mkdir(exist_ok=True)

    def _get_user_avatar_dir(self, user_id: UUID) -> Path:
        """Get avatar directory for specific user"""
        user_dir = self.avatar_dir / str(user_id)
        user_dir.mkdir(exist_ok=True)
        return user_dir

    def generate_default_avatar_svg(self, username: str) -> str:
        """
        Generate SVG avatar based on username initials

        Returns SVG string that can be served directly or saved as file
        """
        # Get first letter of username (uppercase)
        initial = username[0].upper() if username else "?"

        # Generate color based on username hash
        hash_obj = hashlib.md5(username.encode())
        hue = int(hash_obj.hexdigest(), 16) % 360

        # Create SVG
        svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="50" fill="hsl({hue}, 70%, 50%)"/>
  <text x="50" y="65" font-family="Arial, sans-serif" font-size="40" font-weight="bold"
        text-anchor="middle" fill="white">{initial}</text>
</svg>"""

        return svg

    def save_default_avatar(self, user_id: UUID, username: str) -> str:
        """
        Generate and save default avatar SVG for user

        Returns filename of saved avatar
        """
        svg_content = self.generate_default_avatar_svg(username)
        user_dir = self._get_user_avatar_dir(user_id)

        # Generate filename
        filename = f"default_{user_id}.svg"
        filepath = user_dir / filename

        # Save SVG
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)

        return filename

    async def download_google_avatar(
        self, user_id: UUID, image_url: str
    ) -> Optional[str]:
        """
        Download avatar from Google profile picture URL

        Returns filename if successful, None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=10.0)
                response.raise_for_status()

                # Check content type
                content_type = response.headers.get("content-type", "")
                if not content_type.startswith("image/"):
                    return None

                # Get file extension
                ext = self._get_image_extension(content_type)
                if not ext:
                    return None

                # Generate filename
                filename = f"google_{user_id}.{ext}"
                user_dir = self._get_user_avatar_dir(user_id)
                filepath = user_dir / filename

                # Save image
                with open(filepath, "wb") as f:
                    f.write(response.content)

                # Validate image
                try:
                    with Image.open(filepath) as img:
                        img.verify()
                except Exception:
                    # Invalid image, remove file
                    os.remove(filepath)
                    return None

                return filename

        except Exception:
            return None

    def _get_image_extension(self, content_type: str) -> Optional[str]:
        """Get file extension from content type"""
        extensions = {
            "image/jpeg": "jpg",
            "image/jpg": "jpg",
            "image/png": "png",
            "image/gif": "gif",
            "image/webp": "webp",
        }
        return extensions.get(content_type.lower())

    def get_avatar_path(self, user_id: UUID, filename: str) -> Optional[Path]:
        """Get full path to avatar file"""
        if not filename:
            return None

        filepath = self._get_user_avatar_dir(user_id) / filename
        if filepath.exists():
            return filepath

        return None

    def delete_avatar(self, user_id: UUID, filename: str) -> bool:
        """Delete avatar file"""
        if not filename or filename.startswith("default_"):
            return False  # Don't delete default avatars

        filepath = self._get_user_avatar_dir(user_id) / filename
        if filepath.exists():
            try:
                os.remove(filepath)
                return True
            except Exception:
                pass

        return False

    def validate_image_file(self, file_path: Path, max_size_mb: float = 5.0) -> bool:
        """Validate uploaded image file"""
        try:
            # Check file size
            if file_path.stat().st_size > max_size_mb * 1024 * 1024:
                return False

            # Validate image
            with Image.open(file_path) as img:
                img.verify()

            return True

        except Exception:
            return False
