"""
Shared test fixtures for Voicebook test suite.

This module provides pytest fixtures used across unit and integration tests.
"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock


# ========================
# Environment Fixtures
# ========================

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-mock-api-key-1234567890")
    monkeypatch.setenv("CACHE_DIRECTORY", "./test_cache")
    return {
        "OPENAI_API_KEY": "sk-test-mock-api-key-1234567890",
        "CACHE_DIRECTORY": "./test_cache"
    }


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_cache_dir(temp_dir):
    """Create a temporary cache directory."""
    cache_dir = temp_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


# ========================
# Sample Data Fixtures
# ========================

@pytest.fixture
def sample_text():
    """Provide sample text for testing."""
    return """
    This is a sample text for testing the Voicebook TTS application.
    It contains multiple sentences to ensure proper text processing.
    The text should be long enough to test various features.
    We need at least a few paragraphs to make it realistic.

    This is the second paragraph of the sample text.
    It demonstrates how the application handles multi-paragraph content.
    """


@pytest.fixture
def short_text():
    """Very short text for edge case testing."""
    return "Test."


@pytest.fixture
def long_text():
    """Long text for testing character limits."""
    return "A" * 100000  # 100K characters


@pytest.fixture
def sample_metadata():
    """Sample metadata for cache testing."""
    return {
        "voice": "nova",
        "speed": 1.0,
        "quality": "standard",
        "chars": 250,
        "cost": 0.00375
    }


# ========================
# Audio Data Fixtures
# ========================

@pytest.fixture
def mock_audio_data():
    """Mock audio data (fake MP3 bytes)."""
    # Simple mock MP3-like data
    return b"ID3\x04\x00\x00\x00\x00\x00\x00" + b"\x00" * 1000


@pytest.fixture
def mock_audio_file(temp_dir, mock_audio_data):
    """Create a mock audio file."""
    audio_file = temp_dir / "test_audio.mp3"
    audio_file.write_bytes(mock_audio_data)
    return audio_file


# ========================
# Document Fixtures
# ========================

@pytest.fixture
def sample_txt_file(temp_dir, sample_text):
    """Create a sample .txt file."""
    txt_file = temp_dir / "sample.txt"
    txt_file.write_text(sample_text)
    return txt_file


@pytest.fixture
def sample_pdf_file(temp_dir):
    """Create a minimal PDF file for testing."""
    pdf_file = temp_dir / "sample.pdf"
    # Minimal valid PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000262 00000 n
0000000356 00000 n
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
444
%%EOF
"""
    pdf_file.write_bytes(pdf_content)
    return pdf_file


@pytest.fixture
def large_file(temp_dir):
    """Create a file larger than the size limit."""
    large_file = temp_dir / "large.txt"
    # Create a file > 50MB
    large_file.write_text("A" * (51 * 1024 * 1024))
    return large_file


@pytest.fixture
def unsupported_file(temp_dir):
    """Create an unsupported file type."""
    unsupported = temp_dir / "test.xyz"
    unsupported.write_text("Unsupported content")
    return unsupported


# ========================
# Mock API Fixtures
# ========================

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing without API calls."""
    mock_client = MagicMock()

    # Mock the speech.create response
    mock_response = Mock()
    mock_response.content = b"fake_audio_data_" + b"\x00" * 1000

    mock_client.audio.speech.create.return_value = mock_response

    return mock_client


@pytest.fixture
def mock_openai_tts(mock_openai_client, monkeypatch):
    """Mock OpenAI TTS client."""
    from src.api.openai_tts import OpenAITTS

    def mock_init(self, api_key=None):
        self.api_key = api_key or "sk-test-mock-key"
        self.client = mock_openai_client

    monkeypatch.setattr(OpenAITTS, "__init__", mock_init)
    return OpenAITTS


# ========================
# Cache Fixtures
# ========================

@pytest.fixture
def audio_cache(temp_cache_dir, monkeypatch):
    """Create an AudioCache instance with temp directory."""
    from src.cache.audio_cache import AudioCache

    monkeypatch.setenv("CACHE_DIRECTORY", str(temp_cache_dir))
    cache = AudioCache(cache_dir=str(temp_cache_dir))

    yield cache

    # Cleanup
    if temp_cache_dir.exists():
        for file in temp_cache_dir.glob("*"):
            try:
                file.unlink()
            except:
                pass


@pytest.fixture
def populated_cache(audio_cache, mock_audio_data, sample_metadata):
    """AudioCache with pre-populated data."""
    # Add some test entries
    cache_key_1 = audio_cache.generate_cache_key("Test text 1", "nova", 1.0, "standard")
    cache_key_2 = audio_cache.generate_cache_key("Test text 2", "alloy", 1.5, "hd")

    audio_cache.put(cache_key_1, mock_audio_data, sample_metadata)
    audio_cache.put(cache_key_2, mock_audio_data, {**sample_metadata, "voice": "alloy"})

    return audio_cache


# ========================
# Parametrized Fixtures
# ========================

@pytest.fixture(params=["alloy", "echo", "fable", "onyx", "nova", "shimmer"])
def voice_name(request):
    """Parametrized fixture for all voice names."""
    return request.param


@pytest.fixture(params=["standard", "hd"])
def quality_option(request):
    """Parametrized fixture for quality options."""
    return request.param


@pytest.fixture(params=[0.25, 0.5, 1.0, 1.5, 2.0, 4.0])
def speed_value(request):
    """Parametrized fixture for speed values."""
    return request.param


# ========================
# Validator Fixtures
# ========================

@pytest.fixture
def valid_api_key():
    """Valid API key format."""
    return "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz"


@pytest.fixture
def invalid_api_keys():
    """List of invalid API keys."""
    return [
        "",
        "invalid",
        "sk-",
        "sk-short",
        "not-sk-key",
        None
    ]


# ========================
# Cleanup Fixtures
# ========================

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset any singleton instances between tests."""
    yield
    # Add any singleton cleanup here if needed


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup any test files created during tests."""
    yield

    # Cleanup test cache directory if it exists
    test_cache = Path("./test_cache")
    if test_cache.exists():
        import shutil
        try:
            shutil.rmtree(test_cache)
        except:
            pass


# ========================
# Mark Fixtures
# ========================

def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "api: marks tests that require API access")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "unit: marks unit tests")
