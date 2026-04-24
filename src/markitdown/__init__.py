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

Note: For image conversion, an OpenAI client must be passed explicitly::

    from openai import OpenAI
    from markitdown import MarkItDown

    md = MarkItDown(llm_client=OpenAI(), llm_model="gpt-4o")
    result = md.convert("image.png")
    print(result.text_content)

Tip: You can also convert from a URL directly::

    md = MarkItDown()
    result = md.convert("https://example.com/document.pdf")
    print(result.text_content)

Tip: To convert a string of HTML directly (without a file), use convert_stream::

    import io
    md = MarkItDown()
    html_bytes = b"<h1>Hello</h1><p>World</p>"
    result = md.convert_stream(io.BytesIO(html_bytes), file_extension=".html")
    print(result.text_content)
"""

from markitdown._markitdown import MarkItDown, DocumentConverter, ConversionResult

__all__ = [
    "MarkItDown",
    "DocumentConverter",
    "ConversionResult",
]

# Personal note: bumping to reflect my fork's starting point
__version__ = "0.1.0"
