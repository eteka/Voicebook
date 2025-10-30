"""OpenAI Text-to-Speech API client."""

import os
from pathlib import Path
from typing import Optional, Literal
from openai import OpenAI

VoiceType = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
QualityType = Literal["standard", "hd"]


class OpenAITTS:
    """OpenAI TTS API wrapper."""

    # Voice descriptions for UI
    VOICE_INFO = {
        "alloy": "Neutral and balanced (suitable for any content)",
        "echo": "Clear and articulate (great for technical content)",
        "fable": "Warm and expressive (storytelling)",
        "onyx": "Deep and authoritative (formal documents)",
        "nova": "Friendly and conversational (recommended default)",
        "shimmer": "Smooth and professional (business content)"
    }

    # Available voices
    VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI TTS client.

        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        self.client = OpenAI(api_key=self.api_key)

    def generate_speech(
        self,
        text: str,
        voice: VoiceType = "nova",
        speed: float = 1.0,
        quality: QualityType = "standard"
    ) -> bytes:
        """
        Generate speech from text using OpenAI TTS API.

        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            speed: Playback speed (0.25 to 4.0)
            quality: "standard" (tts-1) or "hd" (tts-1-hd)

        Returns:
            Audio data as bytes (MP3 format)

        Raises:
            ValueError: If parameters are invalid
            Exception: If API call fails
        """
        # Validate parameters
        if voice not in self.VOICES:
            raise ValueError(f"Invalid voice. Choose from: {', '.join(self.VOICES)}")

        if not 0.25 <= speed <= 4.0:
            raise ValueError("Speed must be between 0.25 and 4.0")

        if quality not in ["standard", "hd"]:
            raise ValueError("Quality must be 'standard' or 'hd'")

        # Select model based on quality
        model = "tts-1" if quality == "standard" else "tts-1-hd"

        try:
            # Make API call
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )

            # Return audio bytes
            return response.content

        except Exception as e:
            raise Exception(f"OpenAI TTS API error: {str(e)}")

    def generate_speech_to_file(
        self,
        text: str,
        output_path: str,
        voice: VoiceType = "nova",
        speed: float = 1.0,
        quality: QualityType = "standard"
    ) -> Path:
        """
        Generate speech and save directly to file.

        Args:
            text: Text to convert
            output_path: Path to save audio file
            voice: Voice to use
            speed: Playback speed
            quality: Quality setting

        Returns:
            Path to saved audio file
        """
        audio_data = self.generate_speech(text, voice, speed, quality)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(audio_data)

        return output_path

    def test_api_key(self) -> bool:
        """
        Test if API key is valid by making a minimal API call.

        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Make minimal API call with short text
            self.generate_speech("test", voice="alloy")
            return True
        except Exception:
            return False

    @classmethod
    def get_voice_description(cls, voice: str) -> str:
        """Get description for a voice."""
        return cls.VOICE_INFO.get(voice, "Unknown voice")

    @classmethod
    def list_voices(cls) -> list[dict]:
        """Get list of available voices with descriptions."""
        return [
            {"name": voice, "description": cls.VOICE_INFO[voice]}
            for voice in cls.VOICES
        ]
