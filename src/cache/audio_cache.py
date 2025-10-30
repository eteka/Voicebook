"""
Audio caching system for Voicebook.

Provides hash-based caching to avoid regenerating identical audio files.
Cache key is based on: text content + voice + speed + quality settings.
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile


class AudioCache:
    """Manages audio file caching to reduce API costs."""

    def __init__(self, cache_dir: str = None):
        """
        Initialize audio cache.

        Args:
            cache_dir: Directory to store cached files. Defaults to ./cache
        """
        self.cache_dir = Path(cache_dir or os.getenv("CACHE_DIRECTORY", "./cache"))
        self.cache_dir.mkdir(exist_ok=True)
        
        # Create metadata file if it doesn't exist
        self.metadata_file = self.cache_dir / "metadata.json"
        if not self.metadata_file.exists():
            self._save_metadata({})

    def generate_cache_key(self, text: str, voice: str, speed: float, quality: str) -> str:
        """
        Generate a unique cache key based on input parameters.

        Args:
            text: Input text content
            voice: Voice name (e.g., 'nova', 'alloy')
            speed: Playback speed (0.25 to 4.0)
            quality: Quality setting ('standard' or 'hd')

        Returns:
            MD5 hash as cache key
        """
        # Create a string that uniquely identifies this audio generation request
        cache_string = f"{text}|{voice}|{speed}|{quality}"
        
        # Generate MD5 hash
        return hashlib.md5(cache_string.encode('utf-8')).hexdigest()

    def exists(self, cache_key: str) -> bool:
        """Check if cached audio exists for the given key."""
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        return cache_file.exists()

    def get(self, cache_key: str) -> Optional[str]:
        """
        Retrieve cached audio file path.

        Args:
            cache_key: Cache key from generate_cache_key()

        Returns:
            Path to cached audio file, or None if not found
        """
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        
        if cache_file.exists():
            # Update cache hit counter
            self._increment_cache_hits()
            return str(cache_file)
        
        return None

    def put(self, cache_key: str, audio_data: bytes, metadata: Dict[str, Any]) -> str:
        """
        Store audio data in cache.

        Args:
            cache_key: Cache key from generate_cache_key()
            audio_data: Audio file bytes
            metadata: Additional metadata (voice, speed, quality, cost, etc.)

        Returns:
            Path to cached audio file
        """
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        
        # Write audio data
        with open(cache_file, 'wb') as f:
            f.write(audio_data)
        
        # Update metadata
        self._update_metadata(cache_key, metadata)
        
        return str(cache_file)

    def clear(self) -> int:
        """
        Clear all cached files.

        Returns:
            Number of files deleted
        """
        deleted_count = 0
        
        # Delete all .mp3 files
        for cache_file in self.cache_dir.glob("*.mp3"):
            try:
                cache_file.unlink()
                deleted_count += 1
            except OSError:
                pass
        
        # Reset metadata
        self._save_metadata({})
        
        return deleted_count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        metadata = self._load_metadata()
        
        # Count cached files
        mp3_files = list(self.cache_dir.glob("*.mp3"))
        total_files = len(mp3_files)
        
        # Calculate total size
        total_size_bytes = sum(f.stat().st_size for f in mp3_files if f.exists())
        total_size_mb = round(total_size_bytes / (1024 * 1024), 2)
        
        # Get cache hits
        cache_hits = metadata.get("cache_hits", 0)
        
        return {
            "total_files": total_files,
            "total_size_mb": total_size_mb,
            "cache_hits": cache_hits
        }

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from file."""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _update_metadata(self, cache_key: str, file_metadata: Dict[str, Any]) -> None:
        """Update metadata for a specific cache entry."""
        metadata = self._load_metadata()
        
        if "files" not in metadata:
            metadata["files"] = {}
        
        metadata["files"][cache_key] = {
            **file_metadata,
            "created_at": str(Path(self.cache_dir / f"{cache_key}.mp3").stat().st_mtime)
        }
        
        self._save_metadata(metadata)

    def _increment_cache_hits(self) -> None:
        """Increment the cache hit counter."""
        metadata = self._load_metadata()
        metadata["cache_hits"] = metadata.get("cache_hits", 0) + 1
        self._save_metadata(metadata)