"""Input validation utilities."""

import os
from typing import Tuple, Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class FileValidator:
    """Validate uploaded files."""

    SUPPORTED_EXTENSIONS = {'.txt', '.pdf', '.docx'}

    @staticmethod
    def validate_file(file_path: str, max_size_mb: int = 50) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file.

        Args:
            file_path: Path to file
            max_size_mb: Maximum file size in MB

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file exists
        if not os.path.exists(file_path):
            return False, "File does not exist"

        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        if ext not in FileValidator.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file type. Supported: {', '.join(FileValidator.SUPPORTED_EXTENSIONS)}"

        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"File too large ({file_size_mb:.1f}MB). Maximum: {max_size_mb}MB"

        return True, None

    @staticmethod
    def validate_extension(filename: str) -> bool:
        """Check if file extension is supported."""
        _, ext = os.path.splitext(filename.lower())
        return ext in FileValidator.SUPPORTED_EXTENSIONS


class TextValidator:
    """Validate text content."""

    @staticmethod
    def validate_text(text: str, max_chars: int = 500000) -> Tuple[bool, Optional[str]]:
        """
        Validate text content.

        Args:
            text: Text to validate
            max_chars: Maximum character count

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Text is empty"

        char_count = len(text)

        if char_count > max_chars:
            return False, f"Text too long ({char_count:,} characters). Maximum: {max_chars:,}"

        # Warn if very short
        if char_count < 100:
            return True, "⚠️ Warning: Text is very short (less than 100 characters)"

        return True, None


class APIKeyValidator:
    """Validate API configuration."""

    @staticmethod
    def validate_openai_key(api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Validate OpenAI API key format.

        Args:
            api_key: API key to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not api_key:
            return False, "API key is missing"

        if not api_key.startswith("sk-"):
            return False, "Invalid API key format (should start with 'sk-')"

        if len(api_key) < 20:
            return False, "API key appears to be too short"

        return True, None
