"""
Unit tests for input validation utilities.
"""

import pytest
import tempfile
from pathlib import Path
from src.utils.validators import (
    FileValidator,
    TextValidator,
    APIKeyValidator,
    ValidationError
)


class TestFileValidator:
    """Test suite for FileValidator class."""

    def test_supported_extensions(self):
        """Test that supported extensions are defined correctly."""
        assert '.txt' in FileValidator.SUPPORTED_EXTENSIONS
        assert '.pdf' in FileValidator.SUPPORTED_EXTENSIONS
        assert '.docx' in FileValidator.SUPPORTED_EXTENSIONS
        assert len(FileValidator.SUPPORTED_EXTENSIONS) == 3

    def test_validate_file_success(self, sample_txt_file):
        """Test successful file validation."""
        is_valid, error = FileValidator.validate_file(str(sample_txt_file))
        assert is_valid is True
        assert error is None

    def test_validate_file_not_exists(self):
        """Test validation fails for non-existent file."""
        is_valid, error = FileValidator.validate_file("/path/to/nonexistent/file.txt")
        assert is_valid is False
        assert "does not exist" in error

    def test_validate_file_unsupported_extension(self, unsupported_file):
        """Test validation fails for unsupported file type."""
        is_valid, error = FileValidator.validate_file(str(unsupported_file))
        assert is_valid is False
        assert "Unsupported file type" in error
        assert "Supported:" in error

    def test_validate_file_too_large(self, temp_dir):
        """Test validation fails for files exceeding size limit."""
        # Create a file larger than 50MB
        large_file = temp_dir / "large.txt"
        # Write 51MB of data
        with open(large_file, 'w') as f:
            f.write("A" * (51 * 1024 * 1024))

        is_valid, error = FileValidator.validate_file(str(large_file), max_size_mb=50)
        assert is_valid is False
        assert "too large" in error
        assert "51" in error  # Should show actual size

    def test_validate_file_custom_size_limit(self, sample_txt_file):
        """Test validation with custom size limit."""
        # File should be valid with normal limit
        is_valid, error = FileValidator.validate_file(str(sample_txt_file), max_size_mb=50)
        assert is_valid is True

        # But invalid with very small limit
        is_valid, error = FileValidator.validate_file(str(sample_txt_file), max_size_mb=0.0001)
        assert is_valid is False
        assert "too large" in error

    def test_validate_extension_valid(self):
        """Test extension validation for valid files."""
        assert FileValidator.validate_extension("document.txt") is True
        assert FileValidator.validate_extension("book.pdf") is True
        assert FileValidator.validate_extension("report.docx") is True

    def test_validate_extension_case_insensitive(self):
        """Test extension validation is case-insensitive."""
        assert FileValidator.validate_extension("file.TXT") is True
        assert FileValidator.validate_extension("file.Pdf") is True
        assert FileValidator.validate_extension("file.DOCX") is True
        assert FileValidator.validate_extension("file.TxT") is True

    def test_validate_extension_invalid(self):
        """Test extension validation for invalid files."""
        assert FileValidator.validate_extension("file.xyz") is False
        assert FileValidator.validate_extension("file.jpg") is False
        assert FileValidator.validate_extension("file.mp3") is False
        assert FileValidator.validate_extension("file") is False
        assert FileValidator.validate_extension("") is False

    def test_validate_extension_multiple_dots(self):
        """Test extension validation with multiple dots in filename."""
        assert FileValidator.validate_extension("my.file.name.txt") is True
        assert FileValidator.validate_extension("my.file.name.xyz") is False

    @pytest.mark.parametrize("filename,expected", [
        ("test.txt", True),
        ("test.pdf", True),
        ("test.docx", True),
        ("test.TXT", True),
        ("test.PDF", True),
        ("test.jpg", False),
        ("test.exe", False),
        ("test", False),
    ])
    def test_validate_extension_parametrized(self, filename, expected):
        """Test extension validation with various filenames."""
        assert FileValidator.validate_extension(filename) == expected


class TestTextValidator:
    """Test suite for TextValidator class."""

    def test_validate_text_success(self, sample_text):
        """Test successful text validation."""
        is_valid, error = TextValidator.validate_text(sample_text)
        assert is_valid is True
        assert error is None

    def test_validate_text_empty_string(self):
        """Test validation fails for empty string."""
        is_valid, error = TextValidator.validate_text("")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_text_whitespace_only(self):
        """Test validation fails for whitespace-only string."""
        is_valid, error = TextValidator.validate_text("   \n\t  ")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_text_too_long(self):
        """Test validation fails when text exceeds character limit."""
        long_text = "A" * 500001  # One char over default limit
        is_valid, error = TextValidator.validate_text(long_text)
        assert is_valid is False
        assert "too long" in error.lower()
        assert "500,001" in error  # Should show actual count
        assert "500,000" in error  # Should show max

    def test_validate_text_custom_max_chars(self):
        """Test validation with custom character limit."""
        text = "A" * 1000

        # Should pass with higher limit
        is_valid, error = TextValidator.validate_text(text, max_chars=2000)
        assert is_valid is True

        # Should fail with lower limit
        is_valid, error = TextValidator.validate_text(text, max_chars=500)
        assert is_valid is False
        assert "too long" in error.lower()

    def test_validate_text_very_short_warning(self):
        """Test warning for very short text (< 100 chars)."""
        short_text = "Hi"
        is_valid, error = TextValidator.validate_text(short_text)
        assert is_valid is True
        assert error is not None  # Should have a warning
        assert "⚠️" in error
        assert "Warning" in error
        assert "short" in error.lower()

    def test_validate_text_exactly_100_chars(self):
        """Test text with exactly 100 characters (boundary)."""
        text = "A" * 100
        is_valid, error = TextValidator.validate_text(text)
        assert is_valid is True
        # At exactly 100, might or might not warn depending on implementation
        # The code checks < 100, so 100 should not warn

    def test_validate_text_99_chars(self):
        """Test text with 99 characters (should warn)."""
        text = "A" * 99
        is_valid, error = TextValidator.validate_text(text)
        assert is_valid is True
        assert error is not None
        assert "⚠️" in error

    def test_validate_text_normal_length(self):
        """Test text with normal length (no warnings)."""
        text = "This is a normal piece of text. " * 10  # Well over 100 chars
        is_valid, error = TextValidator.validate_text(text)
        assert is_valid is True
        assert error is None

    @pytest.mark.parametrize("text,should_be_valid", [
        ("Hello world", True),  # Normal text
        ("A" * 100, True),      # 100 chars
        ("A" * 500000, True),   # At limit
        ("A" * 500001, False),  # Over limit
        ("", False),            # Empty
        ("   ", False),         # Whitespace only
    ])
    def test_validate_text_parametrized(self, text, should_be_valid):
        """Test text validation with various inputs."""
        is_valid, error = TextValidator.validate_text(text)
        assert is_valid == should_be_valid


class TestAPIKeyValidator:
    """Test suite for APIKeyValidator class."""

    def test_validate_openai_key_success(self, valid_api_key):
        """Test successful API key validation."""
        is_valid, error = APIKeyValidator.validate_openai_key(valid_api_key)
        assert is_valid is True
        assert error is None

    def test_validate_openai_key_empty(self):
        """Test validation fails for empty API key."""
        is_valid, error = APIKeyValidator.validate_openai_key("")
        assert is_valid is False
        assert "missing" in error.lower()

    def test_validate_openai_key_wrong_prefix(self):
        """Test validation fails if key doesn't start with 'sk-'."""
        is_valid, error = APIKeyValidator.validate_openai_key("pk-1234567890abcdefghij")
        assert is_valid is False
        assert "sk-" in error

    def test_validate_openai_key_too_short(self):
        """Test validation fails for keys that are too short."""
        is_valid, error = APIKeyValidator.validate_openai_key("sk-short")
        assert is_valid is False
        assert "too short" in error.lower()

    def test_validate_openai_key_exactly_20_chars(self):
        """Test API key with exactly 20 characters (boundary)."""
        # "sk-" + 17 more chars = 20 total
        key = "sk-12345678901234567"
        is_valid, error = APIKeyValidator.validate_openai_key(key)
        assert is_valid is True
        assert error is None

    def test_validate_openai_key_19_chars(self):
        """Test API key with 19 characters (too short)."""
        key = "sk-1234567890123456"
        is_valid, error = APIKeyValidator.validate_openai_key(key)
        assert is_valid is False

    @pytest.mark.parametrize("api_key,expected_valid", [
        ("sk-proj-1234567890abcdefghijklmnop", True),
        ("sk-1234567890abcdefghijk", True),
        ("sk-" + "a" * 50, True),  # Long key is fine
        ("sk-short", False),  # Too short
        ("invalid-key", False),  # Wrong prefix
        ("", False),  # Empty
        ("sk-", False),  # Just prefix
    ])
    def test_validate_openai_key_parametrized(self, api_key, expected_valid):
        """Test API key validation with various inputs."""
        is_valid, error = APIKeyValidator.validate_openai_key(api_key)
        assert is_valid == expected_valid

    def test_validate_openai_key_realistic_format(self):
        """Test with realistic OpenAI key format."""
        # OpenAI keys typically look like: sk-proj-<long_string>
        realistic_key = "sk-proj-" + "A" * 40
        is_valid, error = APIKeyValidator.validate_openai_key(realistic_key)
        assert is_valid is True
        assert error is None


class TestValidationError:
    """Test suite for ValidationError exception."""

    def test_validation_error_is_exception(self):
        """Test that ValidationError is an Exception."""
        assert issubclass(ValidationError, Exception)

    def test_validation_error_can_be_raised(self):
        """Test that ValidationError can be raised and caught."""
        with pytest.raises(ValidationError):
            raise ValidationError("Test error")

    def test_validation_error_message(self):
        """Test that ValidationError carries a message."""
        message = "Test validation error"
        try:
            raise ValidationError(message)
        except ValidationError as e:
            assert str(e) == message


class TestValidatorsIntegration:
    """Integration tests for validators working together."""

    def test_complete_validation_workflow_success(self, sample_txt_file, valid_api_key):
        """Test complete validation workflow with valid inputs."""
        # Validate API key
        api_valid, api_error = APIKeyValidator.validate_openai_key(valid_api_key)
        assert api_valid is True

        # Validate file
        file_valid, file_error = FileValidator.validate_file(str(sample_txt_file))
        assert file_valid is True

        # Read and validate text
        text = sample_txt_file.read_text()
        text_valid, text_error = TextValidator.validate_text(text)
        assert text_valid is True

    def test_complete_validation_workflow_with_failures(self, temp_dir):
        """Test validation workflow catches various errors."""
        # Invalid API key
        api_valid, _ = APIKeyValidator.validate_openai_key("invalid")
        assert api_valid is False

        # Invalid file
        file_valid, _ = FileValidator.validate_file("/nonexistent/file.txt")
        assert file_valid is False

        # Invalid text
        text_valid, _ = TextValidator.validate_text("")
        assert text_valid is False

    def test_realistic_user_input_validation(self, temp_dir):
        """Test realistic user input validation scenario."""
        # Create a valid test file
        test_file = temp_dir / "user_document.txt"
        test_file.write_text("This is a user's document. " * 100)

        # Validate extension first (fast check)
        if not FileValidator.validate_extension(str(test_file)):
            pytest.fail("Extension should be valid")

        # Validate full file
        file_valid, file_error = FileValidator.validate_file(str(test_file))
        assert file_valid is True

        # Read and validate content
        content = test_file.read_text()
        text_valid, text_error = TextValidator.validate_text(content)
        assert text_valid is True

    def test_edge_case_handling(self):
        """Test edge cases across all validators."""
        # API key edge cases
        assert APIKeyValidator.validate_openai_key("sk-" + "a" * 17)[0] is True  # Min valid
        assert APIKeyValidator.validate_openai_key("sk-" + "a" * 16)[0] is False  # Too short

        # Text edge cases
        assert TextValidator.validate_text("A" * 500000)[0] is True  # At limit
        assert TextValidator.validate_text("A" * 500001)[0] is False  # Over limit

        # Extension edge cases
        assert FileValidator.validate_extension("file.txt") is True
        assert FileValidator.validate_extension("file.TXT") is True
        assert FileValidator.validate_extension("file.txt.backup") is False
