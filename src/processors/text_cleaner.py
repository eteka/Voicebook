"""Text preprocessing and cleaning utilities."""

import re
from typing import Dict


class TextCleaner:
    """Clean and preprocess text for TTS generation."""

    @staticmethod
    def remove_excessive_whitespace(text: str) -> str:
        """Remove excessive whitespace while preserving paragraph breaks."""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)

        # Replace multiple newlines with double newline (paragraph break)
        text = re.sub(r'\n\s*\n+', '\n\n', text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text.strip()

    @staticmethod
    def remove_page_numbers(text: str) -> str:
        """Remove common page number patterns."""
        # Remove standalone numbers on lines (likely page numbers)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

        # Remove "Page X" or "Page X of Y" patterns
        text = re.sub(r'Page\s+\d+(\s+of\s+\d+)?', '', text, flags=re.IGNORECASE)

        return text

    @staticmethod
    def remove_headers_footers(text: str) -> str:
        """Remove repeated headers and footers."""
        lines = text.split('\n')

        if len(lines) < 10:
            return text

        # This is a simple heuristic - in production, more sophisticated methods could be used
        # For now, just return the text as-is
        # A more advanced implementation would detect repeated lines at top/bottom of pages

        return text

    @staticmethod
    def clean_bullet_points(text: str) -> str:
        """Normalize bullet points and list markers."""
        # Replace various bullet characters with standard dash
        text = re.sub(r'^[\u2022\u2023\u2043\u204C\u204D\u2219•○●◆◇■□▪▫]\s*', '- ', text, flags=re.MULTILINE)

        return text

    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text."""
        # Remove http(s) URLs
        text = re.sub(r'https?://\S+', '', text)

        # Remove www URLs
        text = re.sub(r'www\.\S+', '', text)

        return text

    @staticmethod
    def normalize_quotes(text: str) -> str:
        """Normalize quote characters."""
        # Replace smart quotes with regular quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace("'", "'").replace("'", "'")

        return text

    @staticmethod
    def clean_document_text(
        text: str,
        remove_urls: bool = True,
        remove_page_numbers: bool = True,
        normalize_whitespace: bool = True
    ) -> str:
        """
        Clean document text for TTS generation.

        Args:
            text: Input text
            remove_urls: Remove URLs
            remove_page_numbers: Remove page numbers
            normalize_whitespace: Normalize whitespace

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Apply cleaning operations
        if remove_page_numbers:
            text = TextCleaner.remove_page_numbers(text)

        if remove_urls:
            text = TextCleaner.remove_urls(text)

        text = TextCleaner.clean_bullet_points(text)
        text = TextCleaner.normalize_quotes(text)

        if normalize_whitespace:
            text = TextCleaner.remove_excessive_whitespace(text)

        return text

    @staticmethod
    def get_text_stats(text: str) -> Dict[str, int]:
        """
        Get statistics about the text.

        Args:
            text: Input text

        Returns:
            Dictionary with text statistics
        """
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]

        return {
            "characters": len(text),
            "characters_no_spaces": len(text.replace(' ', '')),
            "words": len(words),
            "sentences": len(sentences),
            "paragraphs": len([p for p in text.split('\n\n') if p.strip()]),
            "lines": len(text.split('\n'))
        }

    @staticmethod
    def preview_text(text: str, max_chars: int = 500) -> str:
        """
        Generate a preview of the text.

        Args:
            text: Full text
            max_chars: Maximum characters in preview

        Returns:
            Preview text
        """
        if len(text) <= max_chars:
            return text

        # Try to cut at sentence boundary
        preview = text[:max_chars]
        last_period = preview.rfind('.')
        last_question = preview.rfind('?')
        last_exclamation = preview.rfind('!')

        cut_point = max(last_period, last_question, last_exclamation)

        if cut_point > max_chars * 0.7:  # If we found a good break point
            preview = text[:cut_point + 1]
        else:
            preview = text[:max_chars] + "..."

        return preview
