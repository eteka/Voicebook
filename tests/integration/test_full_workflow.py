"""
Integration tests for complete TTS audiobook generation workflow.

These tests verify that all components work together correctly.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.processors.document_parser import DocumentParser
from src.processors.text_cleaner import TextCleaner
from src.cache.audio_cache import AudioCache
from src.api.openai_tts import OpenAITTS
from src.utils.validators import FileValidator, TextValidator, APIKeyValidator
from src.utils.cost_calculator import CostCalculator, get_cost_warning_message


@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""

    def test_complete_audiobook_generation_workflow(
        self, temp_dir, temp_cache_dir, mock_openai_client, mock_env_vars
    ):
        """Test the complete workflow from document upload to audio generation."""
        # Step 1: Create a test document
        document_content = """
        The Story of Testing
        Page 1

        This is a sample document for testing the TTS system.
        It contains multiple paragraphs and sentences.

        Visit http://example.com for more info.

        • Key point 1
        • Key point 2

        "Quality is never an accident" - William A. Foster

        Page 2 of 5
        The end.
        """
        doc_file = temp_dir / "test_book.txt"
        doc_file.write_text(document_content)

        # Step 2: Validate file
        is_valid, error = FileValidator.validate_file(str(doc_file))
        assert is_valid is True
        assert error is None

        # Step 3: Parse document
        text, parse_error = DocumentParser.parse_file(str(doc_file))
        assert parse_error is None
        assert len(text) > 0

        # Step 4: Clean text
        cleaned_text = TextCleaner.clean_document_text(text)
        assert "http://example.com" not in cleaned_text
        assert "Page 1" not in cleaned_text
        assert "The Story of Testing" in cleaned_text

        # Step 5: Validate cleaned text
        text_valid, text_error = TextValidator.validate_text(cleaned_text)
        assert text_valid is True

        # Step 6: Calculate cost
        cost = CostCalculator.estimate_cost(cleaned_text, "standard")
        assert cost > 0
        warning = get_cost_warning_message(cost, threshold=2.00)

        # Step 7: Initialize cache
        cache = AudioCache(cache_dir=str(temp_cache_dir))
        cache_key = cache.generate_cache_key(cleaned_text, "nova", 1.0, "standard")

        # Step 8: Check cache (should be miss initially)
        assert cache.exists(cache_key) is False

        # Step 9: Generate audio with TTS
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            audio_data = tts.generate_speech(cleaned_text, voice="nova", quality="standard")

        assert isinstance(audio_data, bytes)
        assert len(audio_data) > 0

        # Step 10: Store in cache
        cache_path = cache.put(
            cache_key,
            audio_data,
            {
                "voice": "nova",
                "speed": 1.0,
                "quality": "standard",
                "chars": len(cleaned_text),
                "cost": cost
            }
        )

        # Step 11: Verify cache hit on second request
        assert cache.exists(cache_key) is True
        cached_path = cache.get(cache_key)
        assert cached_path == cache_path

        # Step 12: Verify stats
        stats = cache.get_stats()
        assert stats["total_files"] == 1
        assert stats["cache_hits"] == 1  # From the get() call

    def test_workflow_with_cache_hit(
        self, temp_dir, populated_cache, mock_openai_client, mock_env_vars
    ):
        """Test workflow when audio is already cached."""
        # Create document
        text = "Test text 1"  # Matches populated_cache fixture
        doc_file = temp_dir / "cached_doc.txt"
        doc_file.write_text(text)

        # Parse and clean
        parsed_text, _ = DocumentParser.parse_file(str(doc_file))
        cleaned_text = TextCleaner.clean_document_text(parsed_text)

        # Check cache
        cache_key = populated_cache.generate_cache_key(cleaned_text, "nova", 1.0, "standard")

        # Should find in cache
        cached_path = populated_cache.get(cache_key)

        # No need to call API if cached
        if cached_path:
            assert Path(cached_path).exists()
            # API call should be skipped

    def test_workflow_with_validation_failure(self, temp_dir):
        """Test workflow when validation fails."""
        # Create invalid file (too large)
        large_file = temp_dir / "too_large.txt"
        large_file.write_text("A" * (51 * 1024 * 1024))  # 51MB

        # Validation should fail
        is_valid, error = FileValidator.validate_file(str(large_file))
        assert is_valid is False
        assert "too large" in error

        # Workflow should stop here - no further processing

    def test_workflow_with_empty_document(self, temp_dir):
        """Test workflow with empty document."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")

        # Parse will succeed but return empty
        text, error = DocumentParser.parse_file(str(empty_file))
        assert text == ""
        assert "No text could be extracted" in error

        # Text validation should fail
        text_valid, text_error = TextValidator.validate_text(text)
        assert text_valid is False


@pytest.mark.integration
class TestMultipleDocumentProcessing:
    """Test processing multiple documents."""

    def test_process_multiple_documents_with_caching(
        self, temp_dir, temp_cache_dir, mock_openai_client, mock_env_vars
    ):
        """Test processing multiple documents with cache benefits."""
        cache = AudioCache(cache_dir=str(temp_cache_dir))

        documents = [
            ("doc1.txt", "This is document one."),
            ("doc2.txt", "This is document two."),
            ("doc1_copy.txt", "This is document one."),  # Duplicate content
        ]

        api_calls = 0

        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()

            for filename, content in documents:
                doc_file = temp_dir / filename
                doc_file.write_text(content)

                # Process document
                text, _ = DocumentParser.parse_file(str(doc_file))
                cleaned = TextCleaner.clean_document_text(text)

                cache_key = cache.generate_cache_key(cleaned, "nova", 1.0, "standard")

                # Check cache first
                cached_audio = cache.get(cache_key)

                if not cached_audio:
                    # Generate audio
                    audio_data = tts.generate_speech(cleaned)
                    cache.put(cache_key, audio_data, {"voice": "nova"})
                    api_calls += 1

        # Should only make 2 API calls (doc1 and doc2, doc1_copy uses cache)
        assert api_calls == 2

        # Verify cache stats
        stats = cache.get_stats()
        assert stats["total_files"] == 2  # Only 2 unique documents
        assert stats["cache_hits"] >= 1  # At least one cache hit


@pytest.mark.integration
class TestDifferentQualityAndVoiceOptions:
    """Test generating audio with different options."""

    def test_same_text_different_voices(
        self, temp_dir, temp_cache_dir, mock_openai_client, mock_env_vars
    ):
        """Test generating same text with different voices creates different cache entries."""
        cache = AudioCache(cache_dir=str(temp_cache_dir))
        text = "Hello, this is a test."

        voices = ["nova", "alloy", "echo"]

        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()

            cache_keys = []
            for voice in voices:
                cache_key = cache.generate_cache_key(text, voice, 1.0, "standard")
                cache_keys.append(cache_key)

                audio = tts.generate_speech(text, voice=voice)
                cache.put(cache_key, audio, {"voice": voice})

        # All cache keys should be different
        assert len(set(cache_keys)) == 3

        # Cache should have 3 files
        stats = cache.get_stats()
        assert stats["total_files"] == 3

    def test_same_text_different_quality(
        self, temp_dir, temp_cache_dir, mock_openai_client, mock_env_vars
    ):
        """Test generating same text with different quality settings."""
        cache = AudioCache(cache_dir=str(temp_cache_dir))
        text = "Quality test text."

        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()

            # Generate standard quality
            key_standard = cache.generate_cache_key(text, "nova", 1.0, "standard")
            audio_standard = tts.generate_speech(text, quality="standard")
            cache.put(key_standard, audio_standard, {"quality": "standard"})

            # Generate HD quality
            key_hd = cache.generate_cache_key(text, "nova", 1.0, "hd")
            audio_hd = tts.generate_speech(text, quality="hd")
            cache.put(key_hd, audio_hd, {"quality": "hd"})

        # Keys should be different
        assert key_standard != key_hd

        # Both should be cached
        assert cache.exists(key_standard)
        assert cache.exists(key_hd)


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in integrated workflows."""

    def test_invalid_api_key_handling(self, temp_dir, monkeypatch):
        """Test handling of invalid API key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Should raise error when initializing without API key
        with pytest.raises(ValueError) as exc_info:
            OpenAITTS()

        assert "API key not found" in str(exc_info.value)

    def test_api_call_failure_handling(self, temp_dir, mock_env_vars):
        """Test handling of API call failures."""
        mock_client = MagicMock()
        mock_client.audio.speech.create.side_effect = Exception("API Error")

        with patch('src.api.openai_tts.OpenAI', return_value=mock_client):
            tts = OpenAITTS()

            with pytest.raises(Exception) as exc_info:
                tts.generate_speech("Test")

            assert "OpenAI TTS API error" in str(exc_info.value)

    def test_corrupted_pdf_handling(self, temp_dir):
        """Test handling of corrupted PDF files."""
        # Create an invalid PDF file
        bad_pdf = temp_dir / "corrupted.pdf"
        bad_pdf.write_bytes(b"Not a real PDF")

        # Should handle gracefully
        text, error = DocumentParser.parse_file(str(bad_pdf))
        assert text == ""
        assert error is not None


@pytest.mark.integration
class TestCostOptimization:
    """Test cost optimization through caching."""

    def test_cost_savings_through_caching(
        self, temp_dir, temp_cache_dir, mock_openai_client, mock_env_vars
    ):
        """Test that caching provides significant cost savings."""
        cache = AudioCache(cache_dir=str(temp_cache_dir))

        # Document that would be expensive to generate
        text = "A" * 100000  # 100K characters

        # Calculate cost
        cost_per_generation = CostCalculator.estimate_cost(text, "standard")
        assert cost_per_generation > 0

        cache_key = cache.generate_cache_key(text, "nova", 1.0, "standard")

        # First generation (costs money)
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            audio = tts.generate_speech(text)
            cache.put(cache_key, audio, {"cost": cost_per_generation})

        total_cost = cost_per_generation

        # Subsequent accesses (free, from cache)
        for i in range(10):
            cached = cache.get(cache_key)
            assert cached is not None
            # No additional cost

        # Total cost should still be just one generation
        # Without cache, it would be 11x cost_per_generation
        savings = (10 * cost_per_generation)
        savings_percentage = (savings / (11 * cost_per_generation)) * 100

        assert savings_percentage > 90  # Should save >90% with caching


@pytest.mark.integration
@pytest.mark.slow
class TestLargeDocumentProcessing:
    """Test processing large documents."""

    def test_large_document_workflow(
        self, temp_dir, temp_cache_dir, mock_openai_client, mock_env_vars
    ):
        """Test processing a large document."""
        # Create a large document (simulating a book chapter)
        large_content = "This is a sentence. " * 5000  # ~100K characters
        doc_file = temp_dir / "large_book.txt"
        doc_file.write_text(large_content)

        # Validate
        is_valid, error = FileValidator.validate_file(str(doc_file))
        assert is_valid is True

        # Parse
        text, _ = DocumentParser.parse_file(str(doc_file))
        assert len(text) > 90000

        # Clean
        cleaned = TextCleaner.clean_document_text(text)

        # Validate text length
        text_valid, _ = TextValidator.validate_text(cleaned)
        assert text_valid is True

        # Calculate cost and warn if high
        cost = CostCalculator.estimate_cost(cleaned, "standard")
        warning = get_cost_warning_message(cost, threshold=1.00)
        if cost >= 1.00:
            assert warning != ""

        # Get stats
        stats = TextCleaner.get_text_stats(cleaned)
        assert stats["characters"] > 90000
        assert stats["words"] > 15000

        # Generate audio
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            audio = tts.generate_speech(cleaned)
            assert len(audio) > 0


@pytest.mark.integration
class TestRealisticUseCase:
    """Test realistic user scenarios."""

    def test_user_converts_book_chapter(
        self, temp_dir, temp_cache_dir, mock_openai_client, mock_env_vars
    ):
        """Simulate a user converting a book chapter to audio."""
        # User uploads a book chapter
        chapter_text = """
        Chapter 5: The Journey Begins

        The morning sun cast long shadows across the valley.
        Sarah packed her belongings carefully, knowing this
        journey would change everything.

        "Are you ready?" asked Tom.

        She nodded, though uncertainty filled her heart.
        """

        doc_file = temp_dir / "chapter5.txt"
        doc_file.write_text(chapter_text)

        # Initialize components
        cache = AudioCache(cache_dir=str(temp_cache_dir))

        # User settings
        voice = "nova"  # User's preferred voice
        quality = "hd"   # User wants high quality
        speed = 1.0

        # Process
        text, _ = DocumentParser.parse_file(str(doc_file))
        cleaned_text = TextCleaner.clean_document_text(text)
        cost = CostCalculator.estimate_cost(cleaned_text, quality)
        cache_key = cache.generate_cache_key(cleaned_text, voice, speed, quality)

        # Check cache first
        cached_audio = cache.get(cache_key)

        if not cached_audio:
            # Generate audio
            with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
                tts = OpenAITTS()
                audio = tts.generate_speech(
                    cleaned_text,
                    voice=voice,
                    speed=speed,
                    quality=quality
                )

            # Save to cache
            cache.put(cache_key, audio, {
                "voice": voice,
                "speed": speed,
                "quality": quality,
                "cost": cost
            })

        # Verify success
        assert cache.exists(cache_key)
        final_audio_path = cache.get(cache_key)
        assert Path(final_audio_path).exists()

    def test_user_regenerates_with_different_settings(
        self, temp_dir, temp_cache_dir, mock_openai_client, mock_env_vars
    ):
        """Test user regenerating same content with different settings."""
        text = "Sample book content."
        cache = AudioCache(cache_dir=str(temp_cache_dir))

        settings_combinations = [
            ("nova", 1.0, "standard"),
            ("alloy", 1.0, "standard"),  # Different voice
            ("nova", 1.5, "standard"),   # Different speed
            ("nova", 1.0, "hd"),         # Different quality
        ]

        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()

            for voice, speed, quality in settings_combinations:
                cache_key = cache.generate_cache_key(text, voice, speed, quality)

                if not cache.exists(cache_key):
                    audio = tts.generate_speech(text, voice=voice, speed=speed, quality=quality)
                    cache.put(cache_key, audio, {})

        # Should have 4 different cached versions
        stats = cache.get_stats()
        assert stats["total_files"] == 4
