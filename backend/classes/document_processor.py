import io
from pathlib import Path

from docx import Document
from pypdf import PdfReader

from .translator import Translator


class DocumentProcessor:
    """Extrae texto de PDF, DOCX y TXT y traduce su contenido."""

    MAX_TEXT_CHARS = 30000
    CHUNK_SIZE = 6000

    def __init__(self, translator: Translator):
        self.translator = translator

    def process(self, filename, content, source_language, target_language):
        extension = Path(filename).suffix.lower()

        if extension == ".pdf":
            text = self._extract_pdf(content)
        elif extension == ".docx":
            text = self._extract_docx(content)
        elif extension == ".txt":
            text = content.decode("utf-8", errors="replace")
        else:
            raise ValueError("Formato de documento no soportado.")

        text = self._clean_text(text)

        if not text:
            raise ValueError("El documento no contiene texto procesable.")
        if len(text) > self.MAX_TEXT_CHARS:
            raise ValueError(
                f"El documento contiene demasiado texto. El límite es de {self.MAX_TEXT_CHARS} caracteres."
            )

        chunks = self._chunk_text(text)
        translated_chunks = [
            self.translator.translate(chunk, source_language, target_language)
            for chunk in chunks
        ]

        return {
            "filename": filename,
            "original": text,
            "translation": "\n\n".join(translated_chunks),
            "chunks": len(chunks),
        }

    def _extract_pdf(self, content):
        reader = PdfReader(io.BytesIO(content))
        return "\n\n".join((page.extract_text() or "") for page in reader.pages)

    def _extract_docx(self, content):
        document = Document(io.BytesIO(content))
        paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    def _clean_text(self, text):
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line).strip()

    def _chunk_text(self, text):
        if len(text) <= self.CHUNK_SIZE:
            return [text]

        chunks, current = [], []
        for paragraph in text.split("\n"):
            candidate = "\n".join(current + [paragraph])
            if current and len(candidate) > self.CHUNK_SIZE:
                chunks.append("\n".join(current).strip())
                current = [paragraph]
            else:
                current.append(paragraph)

        if current:
            chunks.append("\n".join(current).strip())

        return [chunk for chunk in chunks if chunk]
