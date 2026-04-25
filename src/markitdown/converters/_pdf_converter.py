"""PDF document converter for MarkItDown.

Converts PDF files to Markdown text by extracting text content
from each page using pdfminer.six.
"""

from __future__ import annotations

import io
from typing import BinaryIO, Optional, Union

from .._base_converter import BaseConverter, DocumentConverterResult


class PdfConverter(BaseConverter):
    """Converts PDF files to Markdown-formatted text.

    Uses pdfminer.six to extract text content from PDF documents.
    Each page is separated by a horizontal rule in the output.

    Requires the optional dependency: pdfminer.six
    Install with: pip install markitdown[pdf]
    """

    SUPPORTED_EXTENSIONS = {".pdf"}
    SUPPORTED_MIME_TYPES = {"application/pdf"}

    # Minimum number of non-whitespace characters a page must contain to be
    # included in the output.  Pages below this threshold are likely blank or
    # contain only scanned images with no extractable text, so skipping them
    # keeps the output cleaner.
    MIN_PAGE_CHARS = 10

    def accepts(
        self,
        source: Union[str, BinaryIO],
        mime_type: Optional[str] = None,
        extension: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Return True if the source appears to be a PDF file."""
        if extension and extension.lower() in self.SUPPORTED_EXTENSIONS:
            return True
        if mime_type and mime_type.lower() in self.SUPPORTED_MIME_TYPES:
            return True
        # Sniff the file header for the PDF magic bytes (%PDF-)
        if hasattr(source, "read"):
            header = source.read(5)
            if hasattr(source, "seek"):
                source.seek(0)
            return header == b"%PDF-"
        return False

    def convert(
        self,
        source: Union[str, BinaryIO],
        mime_type: Optional[str] = None,
        extension: Optional[str] = None,
        **kwargs,
    ) -> DocumentConverterResult:
        """Extract text from a PDF and return it as Markdown.

        Args:
            source: A file path string or a binary file-like object.
            mime_type: Optional MIME type hint (unused internally).
            extension: Optional file extension hint (unused internally).
            **kwargs: Additional keyword arguments (ignored).

        Returns:
            A DocumentConverterResult whose text_content contains the
            extracted text with pages separated by horizontal rules.
            Pages with fewer than MIN_PAGE_CHARS non-whitespace characters
            are silently skipped.

        Raises:
            ImportError: If pdfminer.six is not installed.
            Exception: If PDF parsing fails.
        """
        try:
            from pdfminer.high_level import extract_pages
            from pdfminer.layout import LTAnno, LTChar, LTTextContainer
        except ImportError as exc:
            raise ImportError(
                "pdfminer.six is required to convert PDF files. "
                "Install it with: pip install markitdown[pdf]"
            ) from exc

        # Normalise source to a file-like object
        if isinstance(source, str):
            file_obj: BinaryIO = open(source, "rb")  # noqa: WPS515
            should_close = True
        else:
            file_obj = source
            should_close = False

        pages_text: list[str] = []
        try:
            for page_layout in extract_pages(file_obj):
