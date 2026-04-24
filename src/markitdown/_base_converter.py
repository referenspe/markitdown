# SPDX-FileCopyrightText: 2024 Marcus Schiesser <mail@marcusschiesser.de>
#
# SPDX-License-Identifier: MIT

"""Base converter interface for markitdown converters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, BinaryIO, Dict, Optional, Union


@dataclass
class DocumentConverterResult:
    """Result of a document conversion operation."""

    title: Optional[str] = None
    """The title of the document, if available."""

    text_content: str = ""
    """The converted markdown text content."""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata extracted from the document."""

    def __str__(self) -> str:
        """Return the text content as the string representation."""
        return self.text_content


class BaseConverter(ABC):
    """Abstract base class for all document converters.

    All converters must implement the `convert` method which takes a
    file path or stream and returns a `DocumentConverterResult`.
    """

    @abstractmethod
    def convert(
        self,
        file_path: Optional[str],
        file_extension: Optional[str] = None,
        file_stream: Optional[BinaryIO] = None,
        **kwargs: Any,
    ) -> Optional[DocumentConverterResult]:
        """Convert a document to markdown.

        Args:
            file_path: Path to the file to convert. May be None if
                       file_stream is provided.
            file_extension: The file extension (e.g., '.pdf', '.docx').
                            Used to determine the converter to use.
            file_stream: A binary stream of the file content. May be
                         None if file_path is provided.
            **kwargs: Additional keyword arguments passed to the converter.

        Returns:
            A `DocumentConverterResult` containing the converted markdown
            text and any extracted metadata, or None if the converter
            cannot handle the given file.
        """
        ...

    def accepts(
        self,
        file_path: Optional[str],
        file_extension: Optional[str] = None,
        **kwargs: Any,
    ) -> bool:
        """Check whether this converter can handle the given file.

        Override this method to provide a fast pre-check before attempting
        conversion. The default implementation always returns True.

        Args:
            file_path: Path to the file.
            file_extension: The file extension (e.g., '.pdf', '.docx').
            **kwargs: Additional keyword arguments.

        Returns:
            True if the converter can handle the file, False otherwise.
        """
        return True
