"""
Unit tests for OpenAI TTS API client.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from src.api.openai_tts import OpenAITTS


class TestOpenAITTSInitialization:
    """Test suite for OpenAITTS initialization."""

    def test_init_with_api_key(self, mock_env_vars):
        """Test initialization with explicit API key."""
        api_key = "sk-test-explicit-key"
        with patch('src.api.openai_tts.OpenAI'):
            tts = OpenAITTS(api_key=api_key)
            assert tts.api_key == api_key

    def test_init_with_env_var(self, mock_env_vars):
        """Test initialization with API key from environment."""
        with patch('src.api.openai_tts.OpenAI'):
            tts = OpenAITTS()
            assert tts.api_key == mock_env_vars["OPENAI_API_KEY"]

    def test_init_without_api_key_raises_error(self, monkeypatch):
        """Test that initialization fails without API key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(ValueError) as exc_info:
            OpenAITTS()

        assert "API key not found" in str(exc_info.value)

    def test_init_creates_openai_client(self, mock_env_vars):
        """Test that initialization creates OpenAI client."""
        with patch('src.api.openai_tts.OpenAI') as mock_openai:
            tts = OpenAITTS()
            mock_openai.assert_called_once_with(api_key=tts.api_key)


class TestOpenAITTSConstants:
    """Test suite for OpenAITTS class constants."""

    def test_voices_list(self):
        """Test that VOICES list contains all expected voices."""
        expected_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        assert OpenAITTS.VOICES == expected_voices
        assert len(OpenAITTS.VOICES) == 6

    def test_voice_info_complete(self):
        """Test that VOICE_INFO has descriptions for all voices."""
        for voice in OpenAITTS.VOICES:
            assert voice in OpenAITTS.VOICE_INFO
            assert isinstance(OpenAITTS.VOICE_INFO[voice], str)
            assert len(OpenAITTS.VOICE_INFO[voice]) > 0

    def test_voice_descriptions_content(self):
        """Test that voice descriptions are meaningful."""
        # Check a few specific voices
        assert "neutral" in OpenAITTS.VOICE_INFO["alloy"].lower()
        assert "storytelling" in OpenAITTS.VOICE_INFO["fable"].lower()
        assert "deep" in OpenAITTS.VOICE_INFO["onyx"].lower()


class TestGenerateSpeech:
    """Test suite for generate_speech method."""

    def test_generate_speech_success(self, mock_env_vars, mock_openai_client):
        """Test successful speech generation."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            result = tts.generate_speech("Hello world")

            assert isinstance(result, bytes)
            assert len(result) > 0
            mock_openai_client.audio.speech.create.assert_called_once()

    def test_generate_speech_default_parameters(self, mock_env_vars, mock_openai_client):
        """Test that default parameters are used correctly."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            tts.generate_speech("Test text")

            call_args = mock_openai_client.audio.speech.create.call_args
            assert call_args.kwargs["voice"] == "nova"
            assert call_args.kwargs["speed"] == 1.0
            assert call_args.kwargs["model"] == "tts-1"

    def test_generate_speech_custom_parameters(self, mock_env_vars, mock_openai_client):
        """Test speech generation with custom parameters."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            tts.generate_speech(
                "Test text",
                voice="alloy",
                speed=1.5,
                quality="hd"
            )

            call_args = mock_openai_client.audio.speech.create.call_args
            assert call_args.kwargs["voice"] == "alloy"
            assert call_args.kwargs["speed"] == 1.5
            assert call_args.kwargs["model"] == "tts-1-hd"

    @pytest.mark.parametrize("voice", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
    def test_generate_speech_all_voices(self, mock_env_vars, mock_openai_client, voice):
        """Test speech generation with all available voices."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            result = tts.generate_speech("Test", voice=voice)

            assert isinstance(result, bytes)
            call_args = mock_openai_client.audio.speech.create.call_args
            assert call_args.kwargs["voice"] == voice

    def test_generate_speech_invalid_voice_raises_error(self, mock_env_vars):
        """Test that invalid voice raises ValueError."""
        with patch('src.api.openai_tts.OpenAI'):
            tts = OpenAITTS()

            with pytest.raises(ValueError) as exc_info:
                tts.generate_speech("Test", voice="invalid_voice")

            assert "Invalid voice" in str(exc_info.value)

    @pytest.mark.parametrize("speed", [0.25, 0.5, 1.0, 1.5, 2.0, 4.0])
    def test_generate_speech_valid_speeds(self, mock_env_vars, mock_openai_client, speed):
        """Test speech generation with valid speed values."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            result = tts.generate_speech("Test", speed=speed)

            assert isinstance(result, bytes)
            call_args = mock_openai_client.audio.speech.create.call_args
            assert call_args.kwargs["speed"] == speed

    @pytest.mark.parametrize("speed", [0.24, 0.0, 4.1, 5.0, -1.0])
    def test_generate_speech_invalid_speed_raises_error(self, mock_env_vars, speed):
        """Test that invalid speed raises ValueError."""
        with patch('src.api.openai_tts.OpenAI'):
            tts = OpenAITTS()

            with pytest.raises(ValueError) as exc_info:
                tts.generate_speech("Test", speed=speed)

            assert "Speed must be between" in str(exc_info.value)

    def test_generate_speech_standard_quality(self, mock_env_vars, mock_openai_client):
        """Test that standard quality uses tts-1 model."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            tts.generate_speech("Test", quality="standard")

            call_args = mock_openai_client.audio.speech.create.call_args
            assert call_args.kwargs["model"] == "tts-1"

    def test_generate_speech_hd_quality(self, mock_env_vars, mock_openai_client):
        """Test that HD quality uses tts-1-hd model."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            tts.generate_speech("Test", quality="hd")

            call_args = mock_openai_client.audio.speech.create.call_args
            assert call_args.kwargs["model"] == "tts-1-hd"

    def test_generate_speech_invalid_quality_raises_error(self, mock_env_vars):
        """Test that invalid quality raises ValueError."""
        with patch('src.api.openai_tts.OpenAI'):
            tts = OpenAITTS()

            with pytest.raises(ValueError) as exc_info:
                tts.generate_speech("Test", quality="ultra")

            assert "Quality must be" in str(exc_info.value)

    def test_generate_speech_mp3_format(self, mock_env_vars, mock_openai_client):
        """Test that MP3 format is requested."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            tts.generate_speech("Test")

            call_args = mock_openai_client.audio.speech.create.call_args
            assert call_args.kwargs["response_format"] == "mp3"

    def test_generate_speech_api_error_handling(self, mock_env_vars):
        """Test that API errors are properly handled."""
        mock_client = MagicMock()
        mock_client.audio.speech.create.side_effect = Exception("API Error")

        with patch('src.api.openai_tts.OpenAI', return_value=mock_client):
            tts = OpenAITTS()

            with pytest.raises(Exception) as exc_info:
                tts.generate_speech("Test")

            assert "OpenAI TTS API error" in str(exc_info.value)


class TestGenerateSpeechToFile:
    """Test suite for generate_speech_to_file method."""

    def test_generate_speech_to_file_success(self, mock_env_vars, mock_openai_client, temp_dir):
        """Test successful file generation."""
        output_path = temp_dir / "output.mp3"

        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            result_path = tts.generate_speech_to_file("Test", str(output_path))

            assert result_path == Path(output_path)
            assert output_path.exists()
            assert output_path.read_bytes() == mock_openai_client.audio.speech.create().content

    def test_generate_speech_to_file_creates_directory(self, mock_env_vars, mock_openai_client, temp_dir):
        """Test that output directory is created if it doesn't exist."""
        output_path = temp_dir / "subdir" / "nested" / "output.mp3"
        assert not output_path.parent.exists()

        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            result_path = tts.generate_speech_to_file("Test", str(output_path))

            assert output_path.parent.exists()
            assert output_path.exists()

    def test_generate_speech_to_file_with_parameters(self, mock_env_vars, mock_openai_client, temp_dir):
        """Test file generation with custom parameters."""
        output_path = temp_dir / "output.mp3"

        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            tts.generate_speech_to_file(
                "Test",
                str(output_path),
                voice="alloy",
                speed=1.5,
                quality="hd"
            )

            call_args = mock_openai_client.audio.speech.create.call_args
            assert call_args.kwargs["voice"] == "alloy"
            assert call_args.kwargs["speed"] == 1.5
            assert call_args.kwargs["model"] == "tts-1-hd"

    def test_generate_speech_to_file_returns_path_object(self, mock_env_vars, mock_openai_client, temp_dir):
        """Test that method returns Path object."""
        output_path = temp_dir / "output.mp3"

        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            result = tts.generate_speech_to_file("Test", str(output_path))

            assert isinstance(result, Path)


class TestTestAPIKey:
    """Test suite for test_api_key method."""

    def test_api_key_valid(self, mock_env_vars, mock_openai_client):
        """Test API key validation with valid key."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            result = tts.test_api_key()

            assert result is True
            mock_openai_client.audio.speech.create.assert_called_once()

    def test_api_key_invalid(self, mock_env_vars):
        """Test API key validation with invalid key."""
        mock_client = MagicMock()
        mock_client.audio.speech.create.side_effect = Exception("Invalid API key")

        with patch('src.api.openai_tts.OpenAI', return_value=mock_client):
            tts = OpenAITTS()
            result = tts.test_api_key()

            assert result is False

    def test_api_key_test_uses_minimal_call(self, mock_env_vars, mock_openai_client):
        """Test that API key test uses minimal API call."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            tts.test_api_key()

            call_args = mock_openai_client.audio.speech.create.call_args
            # Should use short text to minimize cost
            assert call_args.kwargs["input"] == "test"


class TestClassMethods:
    """Test suite for class methods."""

    def test_get_voice_description(self):
        """Test getting voice description."""
        desc = OpenAITTS.get_voice_description("nova")
        assert isinstance(desc, str)
        assert len(desc) > 0
        assert desc == OpenAITTS.VOICE_INFO["nova"]

    def test_get_voice_description_unknown_voice(self):
        """Test getting description for unknown voice."""
        desc = OpenAITTS.get_voice_description("unknown")
        assert desc == "Unknown voice"

    def test_list_voices(self):
        """Test listing all voices with descriptions."""
        voices = OpenAITTS.list_voices()

        assert isinstance(voices, list)
        assert len(voices) == 6

        for voice_info in voices:
            assert "name" in voice_info
            assert "description" in voice_info
            assert voice_info["name"] in OpenAITTS.VOICES

    def test_list_voices_structure(self):
        """Test that list_voices returns correct structure."""
        voices = OpenAITTS.list_voices()

        nova_info = next((v for v in voices if v["name"] == "nova"), None)
        assert nova_info is not None
        assert nova_info["description"] == OpenAITTS.VOICE_INFO["nova"]


class TestOpenAITTSIntegration:
    """Integration tests for OpenAITTS workflows."""

    def test_complete_generation_workflow(self, mock_env_vars, mock_openai_client, temp_dir):
        """Test complete speech generation workflow."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            # Initialize client
            tts = OpenAITTS()

            # Test API key
            assert tts.test_api_key() is True

            # Generate speech
            audio_bytes = tts.generate_speech(
                "This is a test document.",
                voice="nova",
                speed=1.0,
                quality="standard"
            )

            assert isinstance(audio_bytes, bytes)
            assert len(audio_bytes) > 0

            # Save to file
            output_path = temp_dir / "test_output.mp3"
            saved_path = tts.generate_speech_to_file(
                "This is a test document.",
                str(output_path),
                voice="nova",
                speed=1.0,
                quality="standard"
            )

            assert saved_path.exists()
            assert saved_path.read_bytes() == audio_bytes

    def test_multiple_voice_comparison(self, mock_env_vars, mock_openai_client):
        """Test generating same text with different voices."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            text = "Test document"

            results = {}
            for voice in ["nova", "alloy", "echo"]:
                audio = tts.generate_speech(text, voice=voice)
                results[voice] = audio

            # All should generate audio
            assert all(isinstance(audio, bytes) for audio in results.values())

    def test_quality_comparison(self, mock_env_vars, mock_openai_client):
        """Test generating same text with different quality settings."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            text = "Test document"

            standard = tts.generate_speech(text, quality="standard")
            hd = tts.generate_speech(text, quality="hd")

            assert isinstance(standard, bytes)
            assert isinstance(hd, bytes)

            # Verify correct models were called
            calls = mock_openai_client.audio.speech.create.call_args_list
            assert calls[0].kwargs["model"] == "tts-1"
            assert calls[1].kwargs["model"] == "tts-1-hd"

    def test_speed_variations(self, mock_env_vars, mock_openai_client):
        """Test generating with different speed settings."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            text = "Test document"

            for speed in [0.5, 1.0, 1.5, 2.0]:
                audio = tts.generate_speech(text, speed=speed)
                assert isinstance(audio, bytes)

    @pytest.mark.parametrize("text,voice,speed,quality", [
        ("Short text", "nova", 1.0, "standard"),
        ("Longer text for testing purposes", "alloy", 1.5, "hd"),
        ("A" * 1000, "echo", 0.5, "standard"),
        ("Different content here", "fable", 2.0, "hd"),
    ])
    def test_various_parameter_combinations(
        self, mock_env_vars, mock_openai_client, text, voice, speed, quality
    ):
        """Test various valid parameter combinations."""
        with patch('src.api.openai_tts.OpenAI', return_value=mock_openai_client):
            tts = OpenAITTS()
            audio = tts.generate_speech(text, voice=voice, speed=speed, quality=quality)

            assert isinstance(audio, bytes)
            assert len(audio) > 0
