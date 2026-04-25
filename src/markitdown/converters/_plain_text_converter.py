"""Plain text converter for MarkItDown.

Handles plain text files (.txt) and other simple text formats,
returning the content as-is or with minimal formatting.
"""

import re
from pathlib import Path
from typing import BinaryIO, Any, Optional

from .._base_converter import BaseConverter, DocumentConverterResult


class PlainTextConverter(BaseConverter):
    """Converter for plain text files.

    Accepts .txt files and generic text content. Returns the text
    content with minimal processing — normalizing line endings and
    stripping excessive blank lines.
    """

    # Added .md and .rst since they're also plain text at the binary level
    ACCEPTED_EXTENSIONS = {".txt", ".text", ".log", ".md", ".rst"}
    ACCEPTED_MIME_TYPES = {"text/plain"}

    def accepts(
        self,
        file_extension: Optional[str] = None,
        mime_type: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Return True if this converter can handle the given file type.

        Args:
            file_extension: The file extension (e.g. '.txt').
            mime_type: The MIME type of the content.
            **kwargs: Additional keyword arguments (ignored).

        Returns:
            True if the extension or MIME type is supported.
        """
        if file_extension is not None:
            if file_extension.lower() in self.ACCEPTED_EXTENSIONS:
                return True
        if mime_type is not None:
            # Handle mime types like 'text/plain; charset=utf-8'
            base_mime = mime_type.split(";")[0].strip().lower()
            if base_mime in self.ACCEPTED_MIME_TYPES:
                return True
        return False

    def convert(
        self,
        file_stream: BinaryIO,
        file_extension: Optional[str] = None,
        mime_type: Optional[str] = None,
        charset: str = "utf-8",
        **kwargs: Any,
    ) -> DocumentConverterResult:
        """Convert plain text content to Markdown.

        Since plain text is already human-readable, this converter
        normalizes whitespace and returns the content as a Markdown
        code block if it appears to be structured data, or as plain
        text otherwise.

        Args:
            file_stream: Binary stream of the file content.
            file_extension: The file extension (e.g. '.txt').
            mime_type: The MIME type of the content.
            charset: Character encoding to use when decoding. Defaults to 'utf-8'.
            **kwargs: Additional keyword arguments (ignored).

        Returns:
            DocumentConverterResult with the text content as Markdown.
        """
        raw = file_stream.read()

        # Try to decode with the provided charset, fall back to latin-1
        try:
            text = raw.decode(charset)
        except (UnicodeDecodeError, LookupError):
            text = raw.decode("latin-1")

        # Normalize Windows-style line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Collapse runs of more than two blank lines into exactly two
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Strip leading/trailing whitespace from the whole document
        text = text.strip()

        return DocumentConverterResult(markdown=text)
