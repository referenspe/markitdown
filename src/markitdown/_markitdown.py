"""Core MarkItDown conversion engine.

This module provides the main MarkItDown class that orchestrates document
conversion by managing a registry of converters and routing files to the
appropriate converter based on file type and content.
"""

import mimetypes
import os
import pathlib
from typing import Optional, Union

from ._base_converter import BaseConverter, DocumentConverterResult


class MarkItDown:
    """Main class for converting documents to Markdown.

    MarkItDown maintains a list of registered converters and attempts to
    convert a given file or URL by trying each converter in priority order
    until one succeeds.

    Example usage::

        from markitdown import MarkItDown

        md = MarkItDown()
        result = md.convert("document.pdf")
        print(result.text_content)
    """

    def __init__(self) -> None:
        """Initialize MarkItDown with an empty converter registry."""
        self._converters: list[BaseConverter] = []

    def register_converter(self, converter: BaseConverter) -> None:
        """Register a converter with the MarkItDown instance.

        Converters are tried in the order they are registered. The first
        converter that accepts the input and succeeds will be used.

        Args:
            converter: A BaseConverter instance to register.
        """
        if not isinstance(converter, BaseConverter):
            raise TypeError(
                f"Expected a BaseConverter instance, got {type(converter).__name__}"
            )
        self._converters.append(converter)

    def convert(
        self,
        source: Union[str, pathlib.Path],
        **kwargs,
    ) -> DocumentConverterResult:
        """Convert a file or URL to Markdown.

        Iterates through registered converters and returns the result from
        the first converter that successfully handles the source.

        Args:
            source: Path to a local file, or a URL string.
            **kwargs: Additional keyword arguments passed to each converter's
                      ``convert`` method.

        Returns:
            A DocumentConverterResult containing the Markdown text and
            optional metadata.

        Raises:
            FileNotFoundError: If ``source`` is a local path that does not exist.
            ValueError: If no registered converter is able to handle the source.
        """
        source = str(source)

        # Resolve local file paths and validate existence
        if not source.startswith(("http://", "https://", "ftp://")):
            resolved = pathlib.Path(source).resolve()
            if not resolved.exists():
                raise FileNotFoundError(
                    f"Source file not found: {source}"
                )
            source = str(resolved)

        # Determine MIME type to assist converters
        mime_type, _ = mimetypes.guess_type(source)
        file_extension = os.path.splitext(source)[1].lower()

        # Try each converter in registration order
        for converter in self._converters:
            if converter.accepts(source, mime_type=mime_type, **kwargs):
                result = converter.convert(
                    source,
                    mime_type=mime_type,
                    file_extension=file_extension,
                    **kwargs,
                )
                if result is not None:
                    return result

        raise ValueError(
            f"No converter was able to handle the source: {source!r}. "
            f"Detected MIME type: {mime_type!r}, extension: {file_extension!r}. "
            "Ensure an appropriate converter is registered."
        )

    @property
    def converters(self) -> list[BaseConverter]:
        """Return a copy of the registered converters list."""
        return list(self._converters)
