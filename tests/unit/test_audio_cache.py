"""
Unit tests for audio caching system.
"""

import pytest
import json
from pathlib import Path
from src.cache.audio_cache import AudioCache


class TestAudioCacheInitialization:
    """Test suite for AudioCache initialization."""

    def test_init_with_custom_directory(self, temp_cache_dir):
        """Test initialization with custom cache directory."""
        cache = AudioCache(cache_dir=str(temp_cache_dir))
        assert cache.cache_dir == temp_cache_dir
        assert temp_cache_dir.exists()

    def test_init_with_default_directory(self, monkeypatch, temp_dir):
        """Test initialization with default cache directory."""
        test_cache = temp_dir / "default_cache"
        monkeypatch.setenv("CACHE_DIRECTORY", str(test_cache))
        cache = AudioCache()
        assert cache.cache_dir == test_cache
        assert test_cache.exists()

    def test_init_creates_directory_if_not_exists(self, temp_dir):
        """Test that initialization creates cache directory if it doesn't exist."""
        cache_dir = temp_dir / "new_cache"
        assert not cache_dir.exists()

        cache = AudioCache(cache_dir=str(cache_dir))
        assert cache_dir.exists()

    def test_init_creates_metadata_file(self, temp_cache_dir):
        """Test that initialization creates metadata.json file."""
        cache = AudioCache(cache_dir=str(temp_cache_dir))
        metadata_file = temp_cache_dir / "metadata.json"
        assert metadata_file.exists()

        # Check metadata is valid JSON
        with open(metadata_file, 'r') as f:
            data = json.load(f)
            assert isinstance(data, dict)

    def test_init_preserves_existing_metadata(self, temp_cache_dir):
        """Test that initialization doesn't overwrite existing metadata."""
        metadata_file = temp_cache_dir / "metadata.json"
        existing_data = {"cache_hits": 42, "files": {}}

        with open(metadata_file, 'w') as f:
            json.dump(existing_data, f)

        cache = AudioCache(cache_dir=str(temp_cache_dir))
        metadata = cache._load_metadata()
        assert metadata["cache_hits"] == 42


class TestCacheKeyGeneration:
    """Test suite for cache key generation."""

    def test_generate_cache_key_consistency(self, audio_cache):
        """Test that same inputs produce same cache key."""
        key1 = audio_cache.generate_cache_key("Hello", "nova", 1.0, "standard")
        key2 = audio_cache.generate_cache_key("Hello", "nova", 1.0, "standard")
        assert key1 == key2

    def test_generate_cache_key_different_text(self, audio_cache):
        """Test that different text produces different key."""
        key1 = audio_cache.generate_cache_key("Hello", "nova", 1.0, "standard")
        key2 = audio_cache.generate_cache_key("World", "nova", 1.0, "standard")
        assert key1 != key2

    def test_generate_cache_key_different_voice(self, audio_cache):
        """Test that different voice produces different key."""
        key1 = audio_cache.generate_cache_key("Hello", "nova", 1.0, "standard")
        key2 = audio_cache.generate_cache_key("Hello", "alloy", 1.0, "standard")
        assert key1 != key2

    def test_generate_cache_key_different_speed(self, audio_cache):
        """Test that different speed produces different key."""
        key1 = audio_cache.generate_cache_key("Hello", "nova", 1.0, "standard")
        key2 = audio_cache.generate_cache_key("Hello", "nova", 1.5, "standard")
        assert key1 != key2

    def test_generate_cache_key_different_quality(self, audio_cache):
        """Test that different quality produces different key."""
        key1 = audio_cache.generate_cache_key("Hello", "nova", 1.0, "standard")
        key2 = audio_cache.generate_cache_key("Hello", "nova", 1.0, "hd")
        assert key1 != key2

    def test_generate_cache_key_format(self, audio_cache):
        """Test that cache key is MD5 hash format."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length
        assert all(c in '0123456789abcdef' for c in key)  # Hex characters

    @pytest.mark.parametrize("text,voice,speed,quality", [
        ("Sample text", "nova", 1.0, "standard"),
        ("Different text", "alloy", 1.5, "hd"),
        ("", "echo", 0.5, "standard"),
        ("A" * 10000, "fable", 2.0, "hd"),
    ])
    def test_generate_cache_key_various_inputs(self, audio_cache, text, voice, speed, quality):
        """Test cache key generation with various valid inputs."""
        key = audio_cache.generate_cache_key(text, voice, speed, quality)
        assert isinstance(key, str)
        assert len(key) == 32


class TestCacheOperations:
    """Test suite for cache get/put/exists operations."""

    def test_exists_returns_false_for_new_key(self, audio_cache):
        """Test that exists returns False for non-existent key."""
        key = audio_cache.generate_cache_key("NonExistent", "nova", 1.0, "standard")
        assert audio_cache.exists(key) is False

    def test_put_stores_audio_data(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that put stores audio data successfully."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        path = audio_cache.put(key, mock_audio_data, sample_metadata)

        assert Path(path).exists()
        assert Path(path).read_bytes() == mock_audio_data

    def test_put_returns_correct_path(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that put returns the correct file path."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        path = audio_cache.put(key, mock_audio_data, sample_metadata)

        expected_path = str(audio_cache.cache_dir / f"{key}.mp3")
        assert path == expected_path

    def test_exists_returns_true_after_put(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that exists returns True after storing data."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        audio_cache.put(key, mock_audio_data, sample_metadata)

        assert audio_cache.exists(key) is True

    def test_get_returns_none_for_missing_key(self, audio_cache):
        """Test that get returns None for non-existent key."""
        key = audio_cache.generate_cache_key("Missing", "nova", 1.0, "standard")
        result = audio_cache.get(key)
        assert result is None

    def test_get_returns_path_after_put(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that get returns correct path after put."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        put_path = audio_cache.put(key, mock_audio_data, sample_metadata)
        get_path = audio_cache.get(key)

        assert get_path == put_path
        assert Path(get_path).exists()

    def test_get_increments_cache_hits(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that get increments the cache hit counter."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        audio_cache.put(key, mock_audio_data, sample_metadata)

        initial_stats = audio_cache.get_stats()
        initial_hits = initial_stats["cache_hits"]

        audio_cache.get(key)

        final_stats = audio_cache.get_stats()
        assert final_stats["cache_hits"] == initial_hits + 1

    def test_get_multiple_times_increments_correctly(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that multiple gets increment cache hits correctly."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        audio_cache.put(key, mock_audio_data, sample_metadata)

        initial_stats = audio_cache.get_stats()
        initial_hits = initial_stats["cache_hits"]

        # Get the cached item 5 times
        for _ in range(5):
            audio_cache.get(key)

        final_stats = audio_cache.get_stats()
        assert final_stats["cache_hits"] == initial_hits + 5

    def test_put_updates_metadata(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that put updates metadata correctly."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        audio_cache.put(key, mock_audio_data, sample_metadata)

        metadata = audio_cache._load_metadata()
        assert "files" in metadata
        assert key in metadata["files"]
        assert metadata["files"][key]["voice"] == "nova"
        assert metadata["files"][key]["speed"] == 1.0


class TestCacheClear:
    """Test suite for cache clearing functionality."""

    def test_clear_empty_cache_returns_zero(self, audio_cache):
        """Test that clearing empty cache returns 0."""
        count = audio_cache.clear()
        assert count == 0

    def test_clear_removes_all_mp3_files(self, populated_cache):
        """Test that clear removes all cached MP3 files."""
        # Verify files exist before clearing
        initial_stats = populated_cache.get_stats()
        assert initial_stats["total_files"] > 0

        count = populated_cache.clear()
        assert count == initial_stats["total_files"]

        # Verify no MP3 files remain
        final_stats = populated_cache.get_stats()
        assert final_stats["total_files"] == 0

    def test_clear_resets_metadata(self, populated_cache):
        """Test that clear resets metadata."""
        populated_cache.clear()

        metadata = populated_cache._load_metadata()
        assert metadata == {} or metadata.get("cache_hits", 0) == 0

    def test_clear_returns_correct_count(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that clear returns the correct number of deleted files."""
        # Add 3 cache entries
        for i in range(3):
            key = audio_cache.generate_cache_key(f"Test {i}", "nova", 1.0, "standard")
            audio_cache.put(key, mock_audio_data, sample_metadata)

        count = audio_cache.clear()
        assert count == 3

    def test_cache_functional_after_clear(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that cache works correctly after being cleared."""
        # Add and clear
        key1 = audio_cache.generate_cache_key("Test 1", "nova", 1.0, "standard")
        audio_cache.put(key1, mock_audio_data, sample_metadata)
        audio_cache.clear()

        # Add new entry after clear
        key2 = audio_cache.generate_cache_key("Test 2", "nova", 1.0, "standard")
        audio_cache.put(key2, mock_audio_data, sample_metadata)

        assert audio_cache.exists(key2) is True
        assert audio_cache.exists(key1) is False


class TestCacheStatistics:
    """Test suite for cache statistics functionality."""

    def test_get_stats_empty_cache(self, audio_cache):
        """Test statistics for empty cache."""
        stats = audio_cache.get_stats()
        assert stats["total_files"] == 0
        assert stats["total_size_mb"] == 0
        assert stats["cache_hits"] == 0

    def test_get_stats_with_cached_files(self, populated_cache):
        """Test statistics with cached files."""
        stats = populated_cache.get_stats()
        assert stats["total_files"] > 0
        assert stats["total_size_mb"] >= 0  # Can be 0 for very small test files
        assert isinstance(stats["total_files"], int)
        assert isinstance(stats["total_size_mb"], float)

    def test_get_stats_file_count(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that stats correctly count files."""
        # Add 3 files
        for i in range(3):
            key = audio_cache.generate_cache_key(f"Test {i}", "nova", 1.0, "standard")
            audio_cache.put(key, mock_audio_data, sample_metadata)

        stats = audio_cache.get_stats()
        assert stats["total_files"] == 3

    def test_get_stats_size_calculation(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that stats correctly calculate total size."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        audio_cache.put(key, mock_audio_data, sample_metadata)

        stats = audio_cache.get_stats()
        expected_size_mb = len(mock_audio_data) / (1024 * 1024)
        # Allow small floating point differences
        assert abs(stats["total_size_mb"] - round(expected_size_mb, 2)) < 0.01

    def test_get_stats_cache_hits_increments(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that cache hits are correctly tracked in stats."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        audio_cache.put(key, mock_audio_data, sample_metadata)

        # Get cache hits before
        stats1 = audio_cache.get_stats()
        hits1 = stats1["cache_hits"]

        # Access cache
        audio_cache.get(key)
        audio_cache.get(key)

        # Get cache hits after
        stats2 = audio_cache.get_stats()
        hits2 = stats2["cache_hits"]

        assert hits2 == hits1 + 2

    def test_get_stats_structure(self, audio_cache):
        """Test that stats return the expected structure."""
        stats = audio_cache.get_stats()
        assert "total_files" in stats
        assert "total_size_mb" in stats
        assert "cache_hits" in stats
        assert len(stats) == 3  # Should have exactly these 3 keys


class TestCacheMetadata:
    """Test suite for cache metadata management."""

    def test_load_metadata_empty_file(self, audio_cache):
        """Test loading metadata from empty/new file."""
        metadata = audio_cache._load_metadata()
        assert isinstance(metadata, dict)

    def test_save_and_load_metadata(self, audio_cache):
        """Test saving and loading metadata."""
        test_data = {"test_key": "test_value", "cache_hits": 10}
        audio_cache._save_metadata(test_data)

        loaded_data = audio_cache._load_metadata()
        assert loaded_data == test_data

    def test_update_metadata_for_cache_entry(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that metadata is updated when adding cache entry."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        audio_cache.put(key, mock_audio_data, sample_metadata)

        metadata = audio_cache._load_metadata()
        assert key in metadata["files"]
        assert metadata["files"][key]["voice"] == sample_metadata["voice"]
        assert metadata["files"][key]["speed"] == sample_metadata["speed"]

    def test_metadata_includes_created_at(self, audio_cache, mock_audio_data, sample_metadata):
        """Test that metadata includes created_at timestamp."""
        key = audio_cache.generate_cache_key("Test", "nova", 1.0, "standard")
        audio_cache.put(key, mock_audio_data, sample_metadata)

        metadata = audio_cache._load_metadata()
        assert "created_at" in metadata["files"][key]

    def test_increment_cache_hits(self, audio_cache):
        """Test incrementing cache hits in metadata."""
        initial_metadata = audio_cache._load_metadata()
        initial_hits = initial_metadata.get("cache_hits", 0)

        audio_cache._increment_cache_hits()

        final_metadata = audio_cache._load_metadata()
        assert final_metadata["cache_hits"] == initial_hits + 1


class TestAudioCacheIntegration:
    """Integration tests for complete cache workflows."""

    def test_full_cache_workflow(self, audio_cache, mock_audio_data, sample_metadata):
        """Test complete cache workflow: put, exists, get."""
        text = "This is a test document for caching."
        voice = "nova"
        speed = 1.0
        quality = "standard"

        # Generate cache key
        key = audio_cache.generate_cache_key(text, voice, speed, quality)

        # Verify doesn't exist yet
        assert audio_cache.exists(key) is False
        assert audio_cache.get(key) is None

        # Store in cache
        path = audio_cache.put(key, mock_audio_data, sample_metadata)
        assert path is not None

        # Verify exists
        assert audio_cache.exists(key) is True

        # Retrieve from cache
        retrieved_path = audio_cache.get(key)
        assert retrieved_path == path

        # Verify data integrity
        assert Path(retrieved_path).read_bytes() == mock_audio_data

    def test_cache_reuse_scenario(self, audio_cache, mock_audio_data, sample_metadata):
        """Test realistic cache reuse scenario."""
        text = "Sample document text"

        # First request - cache miss
        key = audio_cache.generate_cache_key(text, "nova", 1.0, "standard")
        assert audio_cache.get(key) is None

        # Store result
        audio_cache.put(key, mock_audio_data, sample_metadata)

        # Second request - cache hit
        cached_path = audio_cache.get(key)
        assert cached_path is not None

        # Verify cache hits were tracked
        stats = audio_cache.get_stats()
        assert stats["cache_hits"] >= 1

    def test_multiple_different_versions(self, audio_cache, mock_audio_data, sample_metadata):
        """Test caching different versions of same text."""
        text = "Same text"

        # Generate different versions
        key_standard = audio_cache.generate_cache_key(text, "nova", 1.0, "standard")
        key_hd = audio_cache.generate_cache_key(text, "nova", 1.0, "hd")
        key_fast = audio_cache.generate_cache_key(text, "nova", 2.0, "standard")
        key_different_voice = audio_cache.generate_cache_key(text, "alloy", 1.0, "standard")

        # All keys should be different
        assert len({key_standard, key_hd, key_fast, key_different_voice}) == 4

        # Store all versions
        audio_cache.put(key_standard, mock_audio_data, sample_metadata)
        audio_cache.put(key_hd, mock_audio_data, {**sample_metadata, "quality": "hd"})
        audio_cache.put(key_fast, mock_audio_data, {**sample_metadata, "speed": 2.0})
        audio_cache.put(key_different_voice, mock_audio_data, {**sample_metadata, "voice": "alloy"})

        # All should exist independently
        assert audio_cache.exists(key_standard)
        assert audio_cache.exists(key_hd)
        assert audio_cache.exists(key_fast)
        assert audio_cache.exists(key_different_voice)

        stats = audio_cache.get_stats()
        assert stats["total_files"] == 4

    def test_cache_cost_savings_simulation(self, audio_cache, mock_audio_data, sample_metadata):
        """Simulate cost savings from cache hits."""
        text = "Document to be converted multiple times"
        key = audio_cache.generate_cache_key(text, "nova", 1.0, "standard")

        # First generation (costs money)
        api_calls = 1
        audio_cache.put(key, mock_audio_data, sample_metadata)

        # Subsequent retrievals (free, from cache)
        for _ in range(10):
            cached = audio_cache.get(key)
            assert cached is not None
            # No additional API call needed

        stats = audio_cache.get_stats()
        # 10 cache hits means saved 10 API calls
        assert stats["cache_hits"] >= 10
        # Only 1 file stored (not 11)
        assert stats["total_files"] == 1
