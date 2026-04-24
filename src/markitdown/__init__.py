# SPDX-FileCopyrightText: 2024 Marcus Ottosson <marcus@abstractfactory.io>
# SPDX-License-Identifier: MIT

"""MarkItDown - Convert various file formats to Markdown.

This package provides utilities to convert a wide range of file formats
(PDF, DOCX, PPTX, HTML, images, audio, etc.) into clean Markdown text,
suitable for use with large language models and other text processing tools.

Example usage::

    from markitdown import MarkItDown

    md = MarkItDown()
    result = md.convert("document.pdf")
    print(result.text_content)
"""

from markitdown._markitdown import MarkItDown, DocumentConverter, ConversionResult

__all__ = [
    "MarkItDown",
    "DocumentConverter",
    "ConversionResult",
]

__version__ = "0.1.0"
