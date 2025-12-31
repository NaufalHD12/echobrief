import logging
import re

import edge_tts
from sqlmodel.ext.asyncio.session import AsyncSession

logger = logging.getLogger(__name__)


class TTSService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate_audio(
        self, text: str, output_path: str, voice: str = "en-US-JennyNeural"
    ) -> dict:
        """
        Generate audio from text using Edge TTS

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            voice: Voice to use for TTS

        Returns:
            dict: Result with duration and success status
        """

        try:
            # Clean text for better TTS
            cleaned_text = self._clean_text_for_tts(text)

            # Initialize Edge TTS
            communicate = edge_tts.Communicate(cleaned_text, voice)

            # Generate Audio File
            await communicate.save(output_path)

            # Get audio duration
            duration_seconds = self._estimate_audio_duration(cleaned_text)

            logger.info(
                f"TTS generated successfully: {output_path}, duration: {duration_seconds}"
            )
            return {
                "success": True,
                "duration_seconds": duration_seconds,
                "file_path": output_path,
            }

        except Exception as e:
            logger.error(f"TTS generation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": 0,
                "file_path": None,
            }

    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better tts output"""
        # Remove extra white space
        text = re.sub(r"\s+", " ", text.strip())

        # Ensure proper sentences endings
        if not text.endswith((".", "!", "?")):
            text += "."

        return text

    def _estimate_audio_duration(self, text: str) -> int:
        """Estimate audio duration based on text length"""
        # Average speaking rate: ~150 words per minute
        # Edge TTS is usually around 150-180 words per minute
        word_count = len(text.split())
        estimated_seconds = (word_count / 150) * 60

        # Add buffer for pauses and natural speech
        return max(int(estimated_seconds * 1.2), 10)  # min 10 seconds

    async def get_available_voices(self) -> list:
        """Get list of available Edge TTS voices"""
        try:
            voices = await edge_tts.list_voices()
            return [voice["ShortName"] for voice in voices]
        except Exception as e:
            logger.error(f"Failed to get voices: {e}")
            return ["en-US-JennyNeural"]  # Default fallback
