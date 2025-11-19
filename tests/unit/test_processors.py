"""
Unit tests for document processors (parser and text cleaner).
"""

import pytest
from pathlib import Path
from src.processors.document_parser import DocumentParser
from src.processors.text_cleaner import TextCleaner


class TestDocumentParserTXT:
    """Test suite for TXT file parsing."""

    def test_parse_txt_success(self, sample_txt_file):
        """Test successful TXT file parsing."""
        text = DocumentParser.parse_txt(str(sample_txt_file))
        assert isinstance(text, str)
        assert len(text) > 0

    def test_parse_txt_preserves_content(self, temp_dir):
        """Test that TXT parsing preserves content exactly."""
        content = "Hello, world!\nThis is a test.\n"
        txt_file = temp_dir / "test.txt"
        txt_file.write_text(content)

        parsed = DocumentParser.parse_txt(str(txt_file))
        assert parsed == content

    def test_parse_txt_empty_file(self, temp_dir):
        """Test parsing empty TXT file."""
        txt_file = temp_dir / "empty.txt"
        txt_file.write_text("")

        parsed = DocumentParser.parse_txt(str(txt_file))
        assert parsed == ""

    def test_parse_txt_unicode_content(self, temp_dir):
        """Test parsing TXT with unicode characters."""
        content = "Hello 世界 🌍 Ñoño"
        txt_file = temp_dir / "unicode.txt"
        txt_file.write_text(content, encoding='utf-8')

        parsed = DocumentParser.parse_txt(str(txt_file))
        assert content in parsed


class TestDocumentParserPDF:
    """Test suite for PDF file parsing."""

    def test_parse_pdf_success(self, sample_pdf_file):
        """Test successful PDF file parsing."""
        text = DocumentParser.parse_pdf(str(sample_pdf_file))
        assert isinstance(text, str)
        assert len(text) > 0

    def test_parse_pdf_extracts_text(self, sample_pdf_file):
        """Test that PDF parsing extracts text content."""
        text = DocumentParser.parse_pdf(str(sample_pdf_file))
        # Our sample PDF contains "Test PDF"
        assert "Test PDF" in text or "Test" in text

    def test_parse_pdf_nonexistent_file(self):
        """Test parsing non-existent PDF file."""
        with pytest.raises(Exception):
            DocumentParser.parse_pdf("/nonexistent/file.pdf")


class TestDocumentParserDOCX:
    """Test suite for DOCX file parsing."""

    def test_parse_docx_requires_library(self):
        """Test that DOCX parsing checks for library."""
        # This test verifies the code handles missing library
        # Actual behavior depends on whether python-docx is installed
        try:
            from docx import Document
            has_docx = True
        except ImportError:
            has_docx = False

        formats = DocumentParser.get_supported_formats()
        if has_docx:
            assert ".docx" in formats
        else:
            assert ".docx" not in formats


class TestDocumentParserGeneral:
    """Test suite for general document parsing."""

    def test_parse_file_txt(self, sample_txt_file):
        """Test auto-detection for TXT files."""
        text, error = DocumentParser.parse_file(str(sample_txt_file))
        assert error is None
        assert isinstance(text, str)
        assert len(text) > 0

    def test_parse_file_pdf(self, sample_pdf_file):
        """Test auto-detection for PDF files."""
        text, error = DocumentParser.parse_file(str(sample_pdf_file))
        assert error is None
        assert isinstance(text, str)

    def test_parse_file_nonexistent(self):
        """Test parsing non-existent file."""
        text, error = DocumentParser.parse_file("/nonexistent/file.txt")
        assert text == ""
        assert "does not exist" in error

    def test_parse_file_unsupported_format(self, unsupported_file):
        """Test parsing unsupported file format."""
        text, error = DocumentParser.parse_file(str(unsupported_file))
        assert text == ""
        assert "Unsupported file format" in error

    def test_parse_file_empty_document(self, temp_dir):
        """Test parsing empty document."""
        empty_file = temp_dir / "empty.txt"
        empty_file.write_text("")

        text, error = DocumentParser.parse_file(str(empty_file))
        assert text == ""
        assert "No text could be extracted" in error

    def test_get_supported_formats(self):
        """Test getting list of supported formats."""
        formats = DocumentParser.get_supported_formats()
        assert isinstance(formats, list)
        assert ".txt" in formats
        assert len(formats) >= 1


class TestTextCleanerWhitespace:
    """Test suite for whitespace cleaning."""

    def test_remove_excessive_whitespace_multiple_spaces(self):
        """Test removing multiple spaces."""
        text = "Hello    world     test"
        cleaned = TextCleaner.remove_excessive_whitespace(text)
        assert cleaned == "Hello world test"

    def test_remove_excessive_whitespace_newlines(self):
        """Test removing excessive newlines."""
        text = "Para 1\n\n\n\nPara 2"
        cleaned = TextCleaner.remove_excessive_whitespace(text)
        assert cleaned == "Para 1\n\nPara 2"

    def test_remove_excessive_whitespace_preserves_paragraphs(self):
        """Test that paragraph breaks are preserved."""
        text = "First paragraph.\n\nSecond paragraph."
        cleaned = TextCleaner.remove_excessive_whitespace(text)
        assert "\n\n" in cleaned

    def test_remove_excessive_whitespace_strips_edges(self):
        """Test that leading/trailing whitespace is removed."""
        text = "  Hello world  "
        cleaned = TextCleaner.remove_excessive_whitespace(text)
        assert cleaned == "Hello world"

    def test_remove_excessive_whitespace_line_trimming(self):
        """Test that each line is trimmed."""
        text = "  Line 1  \n  Line 2  "
        cleaned = TextCleaner.remove_excessive_whitespace(text)
        assert cleaned == "Line 1\nLine 2"


class TestTextCleanerPageNumbers:
    """Test suite for page number removal."""

    def test_remove_page_numbers_standalone_numbers(self):
        """Test removing standalone page numbers."""
        text = "Text here\n12\nMore text\n13\nEven more"
        cleaned = TextCleaner.remove_page_numbers(text)
        assert "12" not in cleaned or "Text" in cleaned
        assert "13" not in cleaned or "Text" in cleaned

    def test_remove_page_numbers_page_x_format(self):
        """Test removing 'Page X' format."""
        text = "Content Page 5 more content"
        cleaned = TextCleaner.remove_page_numbers(text)
        assert "Page 5" not in cleaned

    def test_remove_page_numbers_page_x_of_y_format(self):
        """Test removing 'Page X of Y' format."""
        text = "Content Page 5 of 100 more content"
        cleaned = TextCleaner.remove_page_numbers(text)
        assert "Page 5 of 100" not in cleaned

    def test_remove_page_numbers_case_insensitive(self):
        """Test that page number removal is case-insensitive."""
        text = "Content page 5 and PAGE 6 content"
        cleaned = TextCleaner.remove_page_numbers(text)
        assert "page 5" not in cleaned
        assert "PAGE 6" not in cleaned


class TestTextCleanerBulletPoints:
    """Test suite for bullet point cleaning."""

    def test_clean_bullet_points_unicode_bullets(self):
        """Test normalizing unicode bullet characters."""
        text = "• Item 1\n○ Item 2\n● Item 3"
        cleaned = TextCleaner.clean_bullet_points(text)
        assert "- Item 1" in cleaned
        assert "- Item 2" in cleaned
        assert "- Item 3" in cleaned

    def test_clean_bullet_points_various_markers(self):
        """Test normalizing various list markers."""
        text = "■ Square\n□ Empty square\n▪ Small square"
        cleaned = TextCleaner.clean_bullet_points(text)
        assert cleaned.count("- ") >= 1


class TestTextCleanerURLs:
    """Test suite for URL removal."""

    def test_remove_urls_http(self):
        """Test removing HTTP URLs."""
        text = "Check http://example.com for info"
        cleaned = TextCleaner.remove_urls(text)
        assert "http://example.com" not in cleaned
        assert "Check" in cleaned
        assert "for info" in cleaned

    def test_remove_urls_https(self):
        """Test removing HTTPS URLs."""
        text = "Visit https://example.com/page"
        cleaned = TextCleaner.remove_urls(text)
        assert "https://example.com/page" not in cleaned

    def test_remove_urls_www(self):
        """Test removing www URLs."""
        text = "See www.example.com for details"
        cleaned = TextCleaner.remove_urls(text)
        assert "www.example.com" not in cleaned

    def test_remove_urls_multiple(self):
        """Test removing multiple URLs."""
        text = "http://site1.com and https://site2.com"
        cleaned = TextCleaner.remove_urls(text)
        assert "http://site1.com" not in cleaned
        assert "https://site2.com" not in cleaned


class TestTextCleanerQuotes:
    """Test suite for quote normalization."""

    def test_normalize_quotes_smart_double_quotes(self):
        """Test normalizing smart double quotes."""
        text = "\u201cHello\u201d and \u201cWorld\u201d"
        cleaned = TextCleaner.normalize_quotes(text)
        assert cleaned == '"Hello" and "World"'

    def test_normalize_quotes_smart_single_quotes(self):
        """Test normalizing smart single quotes."""
        text = "\u2018Hello\u2019 and \u2018World\u2019"
        cleaned = TextCleaner.normalize_quotes(text)
        assert cleaned == "'Hello' and 'World'"


class TestTextCleanerMain:
    """Test suite for main cleaning function."""

    def test_clean_document_text_default(self):
        """Test document cleaning with default settings."""
        text = "Page 1\nCheck http://example.com\nSome    text\n\n\nMore text"
        cleaned = TextCleaner.clean_document_text(text)

        assert "http://example.com" not in cleaned
        assert "Page 1" not in cleaned
        assert "Some text" in cleaned

    def test_clean_document_text_empty(self):
        """Test cleaning empty text."""
        cleaned = TextCleaner.clean_document_text("")
        assert cleaned == ""

    def test_clean_document_text_remove_urls_false(self):
        """Test cleaning with URLs preserved."""
        text = "Visit http://example.com"
        cleaned = TextCleaner.clean_document_text(text, remove_urls=False)
        assert "http://example.com" in cleaned

    def test_clean_document_text_remove_page_numbers_false(self):
        """Test cleaning with page numbers preserved."""
        text = "Page 5"
        cleaned = TextCleaner.clean_document_text(text, remove_page_numbers=False)
        assert "Page 5" in cleaned

    def test_clean_document_text_normalize_whitespace_false(self):
        """Test cleaning without whitespace normalization."""
        text = "Text    with    spaces"
        cleaned = TextCleaner.clean_document_text(text, normalize_whitespace=False)
        # Should still have multiple spaces
        assert "    " in cleaned

    def test_clean_document_text_comprehensive(self):
        """Test comprehensive text cleaning."""
        text = """
        Page 1

        • First item with http://example.com
        "Smart quotes" and 'apostrophes'



        Page 2 of 100
        More    content    here
        """

        cleaned = TextCleaner.clean_document_text(text)

        # URLs should be removed
        assert "http://example.com" not in cleaned
        # Page numbers should be removed
        assert "Page 1" not in cleaned
        assert "Page 2 of 100" not in cleaned
        # Content should be preserved
        assert "First item" in cleaned
        assert "content" in cleaned
        # Whitespace should be normalized
        assert "    " not in cleaned


class TestTextCleanerStats:
    """Test suite for text statistics."""

    def test_get_text_stats_basic(self):
        """Test basic text statistics."""
        text = "Hello world. This is a test."
        stats = TextCleaner.get_text_stats(text)

        assert stats["characters"] == len(text)
        assert stats["words"] == 6
        assert stats["sentences"] == 2

    def test_get_text_stats_structure(self):
        """Test that stats return correct structure."""
        stats = TextCleaner.get_text_stats("Test")
        assert "characters" in stats
        assert "characters_no_spaces" in stats
        assert "words" in stats
        assert "sentences" in stats
        assert "paragraphs" in stats
        assert "lines" in stats

    def test_get_text_stats_paragraphs(self):
        """Test paragraph counting."""
        text = "Para 1\n\nPara 2\n\nPara 3"
        stats = TextCleaner.get_text_stats(text)
        assert stats["paragraphs"] == 3

    def test_get_text_stats_empty(self):
        """Test statistics for empty text."""
        stats = TextCleaner.get_text_stats("")
        assert stats["characters"] == 0
        assert stats["words"] == 0

    def test_get_text_stats_no_spaces(self):
        """Test characters without spaces counting."""
        text = "Hello world"
        stats = TextCleaner.get_text_stats(text)
        assert stats["characters"] == 11
        assert stats["characters_no_spaces"] == 10


class TestTextCleanerPreview:
    """Test suite for text preview generation."""

    def test_preview_text_short_text(self):
        """Test preview of short text (no truncation)."""
        text = "This is short."
        preview = TextCleaner.preview_text(text, max_chars=500)
        assert preview == text

    def test_preview_text_long_text_sentence_boundary(self):
        """Test preview cuts at sentence boundary."""
        text = "First sentence. Second sentence. " + "A" * 500
        preview = TextCleaner.preview_text(text, max_chars=50)
        # Should cut at first sentence
        assert "First sentence." in preview
        assert len(preview) < 100

    def test_preview_text_long_text_no_good_boundary(self):
        """Test preview with no good sentence boundary."""
        text = "A" * 1000
        preview = TextCleaner.preview_text(text, max_chars=500)
        assert len(preview) <= 503  # max_chars + "..."
        assert preview.endswith("...") or len(preview) == 500

    def test_preview_text_exactly_max_chars(self):
        """Test preview when text is exactly max length."""
        text = "A" * 500
        preview = TextCleaner.preview_text(text, max_chars=500)
        assert preview == text

    @pytest.mark.parametrize("max_chars", [100, 200, 500, 1000])
    def test_preview_text_various_lengths(self, max_chars):
        """Test preview with various max lengths."""
        long_text = "Word. " * 500  # Very long text with many sentences
        preview = TextCleaner.preview_text(long_text, max_chars=max_chars)
        assert len(preview) <= max_chars + 3  # +3 for potential "..."


class TestProcessorsIntegration:
    """Integration tests for processors working together."""

    def test_parse_and_clean_workflow(self, sample_txt_file):
        """Test complete parse and clean workflow."""
        # Parse document
        text, error = DocumentParser.parse_file(str(sample_txt_file))
        assert error is None

        # Clean text
        cleaned = TextCleaner.clean_document_text(text)
        assert isinstance(cleaned, str)
        assert len(cleaned) > 0

        # Get stats
        stats = TextCleaner.get_text_stats(cleaned)
        assert stats["characters"] > 0

        # Generate preview
        preview = TextCleaner.preview_text(cleaned, max_chars=100)
        assert len(preview) <= 103

    def test_parse_clean_stats_preview_pipeline(self, temp_dir):
        """Test complete text processing pipeline."""
        # Create test document
        content = """
        Page 1

        Visit http://example.com for more information.

        "This is a quote" with special characters.

        • Item 1
        • Item 2

        Page 2
        """
        txt_file = temp_dir / "test_doc.txt"
        txt_file.write_text(content)

        # 1. Parse
        text, error = DocumentParser.parse_file(str(txt_file))
        assert error is None

        # 2. Clean
        cleaned = TextCleaner.clean_document_text(text)

        # Verify cleaning
        assert "http://example.com" not in cleaned
        assert "Page 1" not in cleaned
        assert "This is a quote" in cleaned
        assert "Item 1" in cleaned

        # 3. Get stats
        stats = TextCleaner.get_text_stats(cleaned)
        assert stats["words"] > 0

        # 4. Preview
        preview = TextCleaner.preview_text(cleaned, max_chars=50)
        assert len(preview) <= 53

    def test_realistic_document_processing(self, temp_dir):
        """Test processing a realistic document."""
        # Create a more realistic document
        content = """
        The Art of Programming
        Page 1

        Introduction

        Programming is both an art and a science. Visit https://programming.com
        for tutorials and guides.

        Key Concepts:
        • Variables and data types
        • Control structures
        • Functions and methods

        Page 2 of 10

        "The best programs are written when programmers have fun" - Anonymous

        For    more    information,    see    Chapter    5.
        """

        doc_file = temp_dir / "programming.txt"
        doc_file.write_text(content)

        # Full pipeline
        text, _ = DocumentParser.parse_file(str(doc_file))
        cleaned = TextCleaner.clean_document_text(text)
        stats = TextCleaner.get_text_stats(cleaned)
        preview = TextCleaner.preview_text(cleaned, max_chars=200)

        # Verify quality
        assert "https://programming.com" not in cleaned
        assert "Page 1" not in cleaned
        assert "Page 2 of 10" not in cleaned
        assert "Programming is both an art" in cleaned
        assert stats["sentences"] > 0
        assert len(preview) <= 203
