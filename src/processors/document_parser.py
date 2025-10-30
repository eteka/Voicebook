"""Document parsing utilities for extracting text from various formats."""

import os
from pathlib import Path
from typing import Tuple, Optional

# PDF parsing
try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

# DOCX parsing
try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


class DocumentParser:
    """Parse text from various document formats."""

    @staticmethod
    def parse_txt(file_path: str) -> str:
        """
        Extract text from TXT file.

        Args:
            file_path: Path to TXT file

        Returns:
            Extracted text
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with latin-1 encoding as fallback
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """
        Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text

        Raises:
            ImportError: If pypdf is not installed
        """
        if not HAS_PYPDF:
            raise ImportError(
                "pypdf is required for PDF parsing. "
                "Install it with: pip install pypdf"
            )

        try:
            reader = PdfReader(file_path)
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            return "\n\n".join(text_parts)

        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """
        Extract text from DOCX file.

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text

        Raises:
            ImportError: If python-docx is not installed
        """
        if not HAS_DOCX:
            raise ImportError(
                "python-docx is required for DOCX parsing. "
                "Install it with: pip install python-docx"
            )

        try:
            doc = Document(file_path)
            text_parts = []

            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)

            return "\n\n".join(text_parts)

        except Exception as e:
            raise Exception(f"Failed to parse DOCX: {str(e)}")

    @staticmethod
    def parse_file(file_path: str) -> Tuple[str, Optional[str]]:
        """
        Parse text from file (auto-detect format).

        Args:
            file_path: Path to document file

        Returns:
            Tuple of (extracted_text, error_message)
        """
        if not os.path.exists(file_path):
            return "", "File does not exist"

        ext = Path(file_path).suffix.lower()

        try:
            if ext == ".txt":
                text = DocumentParser.parse_txt(file_path)
            elif ext == ".pdf":
                text = DocumentParser.parse_pdf(file_path)
            elif ext == ".docx":
                text = DocumentParser.parse_docx(file_path)
            else:
                return "", f"Unsupported file format: {ext}"

            if not text or not text.strip():
                return "", "No text could be extracted from the document"

            return text, None

        except Exception as e:
            return "", f"Error parsing document: {str(e)}"

    @staticmethod
    def get_supported_formats() -> list[str]:
        """Get list of supported file formats."""
        formats = [".txt"]

        if HAS_PYPDF:
            formats.append(".pdf")

        if HAS_DOCX:
            formats.append(".docx")

        return formats
