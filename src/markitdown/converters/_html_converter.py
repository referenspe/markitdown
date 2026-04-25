"""HTML to Markdown converter."""

import re
from typing import BinaryIO, Optional

from markitdown._base_converter import BaseConverter, DocumentConverterResult


class HtmlConverter(BaseConverter):
    """Converts HTML content to Markdown.

    Uses BeautifulSoup for parsing and markdownify (or a fallback)
    to produce clean Markdown output from HTML input.
    """

    SUPPORTED_MIME_TYPES = (
        "text/html",
        "application/xhtml+xml",
    )

    SUPPORTED_EXTENSIONS = (
        ".html",
        ".htm",
        ".xhtml",
    )

    def accepts(
        self,
        source: str,
        mime_type: Optional[str] = None,
        **kwargs,
    ) -> bool:
        """Return True if this converter can handle the given source."""
        if mime_type and mime_type.split(";")[0].strip() in self.SUPPORTED_MIME_TYPES:
            return True
        if isinstance(source, str):
            lower = source.lower()
            return any(lower.endswith(ext) for ext in self.SUPPORTED_EXTENSIONS)
        return False

    def convert(
        self,
        source: str | BinaryIO,
        mime_type: Optional[str] = None,
        charset: str = "utf-8",
        **kwargs,
    ) -> DocumentConverterResult:
        """Convert HTML to Markdown.

        Args:
            source: A file path, URL string, or binary stream containing HTML.
            mime_type: Optional MIME type hint.
            charset: Character encoding to use when reading bytes (default utf-8).

        Returns:
            A DocumentConverterResult with the Markdown text.

        Raises:
            ImportError: If neither markdownify nor beautifulsoup4 is installed.
        """
        try:
            from bs4 import BeautifulSoup  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "beautifulsoup4 is required for HTML conversion. "
                "Install it with: pip install 'markitdown[html]'"
            ) from exc

        # Read raw HTML
        if hasattr(source, "read"):
            raw = source.read()
            if isinstance(raw, bytes):
                raw = raw.decode(charset, errors="replace")
        else:
            # Treat as file path
            with open(source, encoding=charset, errors="replace") as fh:
                raw = fh.read()

        soup = BeautifulSoup(raw, "html.parser")

        # Remove script / style noise
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # Try markdownify first for richer output
        try:
            import markdownify  # type: ignore

            markdown_text = markdownify.markdownify(
                str(soup),
                heading_style=markdownify.ATX,
                bullets="-",
            )
        except ImportError:
            # Fallback: extract plain text with minimal formatting
            markdown_text = self._simple_html_to_md(soup)

        # Clean up excessive blank lines
        markdown_text = re.sub(r"\n{3,}", "\n\n", markdown_text).strip()

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else None

        return DocumentConverterResult(markdown=markdown_text, title=title)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _simple_html_to_md(self, soup) -> str:  # type: ignore[no-untyped-def]
        """Very basic HTML → Markdown fallback when markdownify is unavailable."""
        lines = []
        _heading_tags = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####", "h6": "######"}

        for element in soup.descendants:
            if element.name in _heading_tags:
                prefix = _heading_tags[element.name]
                lines.append(f"{prefix} {element.get_text(strip=True)}\n")
            elif element.name == "p":
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"{text}\n")
            elif element.name in ("li",):
                text = element.get_text(strip=True)
                if text:
                    lines.append(f"- {text}")

        return "\n".join(lines)
