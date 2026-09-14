from pathlib import Path


class FileValidator:
    """Valida nombre, extensión, MIME y tamaño antes de procesar archivos."""

    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

    ALLOWED = {
        "audio": {
            "extensions": {".mp3", ".wav", ".m4a", ".ogg"},
            "mime_prefixes": {"audio/"},
        },
        "document": {
            "extensions": {".pdf", ".docx", ".txt"},
            "mime_prefixes": {
                "application/pdf",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "text/plain",
            },
        },
        "image": {
            "extensions": {".png", ".jpg", ".jpeg"},
            "mime_prefixes": {"image/png", "image/jpeg"},
        },
    }

    def validate_upload(self, filename, content_type, size_bytes, category):
        if not filename:
            raise ValueError("No se recibió un archivo.")
        if size_bytes <= 0:
            raise ValueError("El archivo está vacío.")
        if size_bytes > self.MAX_FILE_SIZE_BYTES:
            raise ValueError("El archivo supera el límite de 10 MB.")
        if category not in self.ALLOWED:
            raise ValueError("Tipo de procesamiento no permitido.")

        extension = Path(filename).suffix.lower()
        rules = self.ALLOWED[category]

        if extension not in rules["extensions"]:
            raise ValueError(f"Formato no permitido: {extension or 'sin extensión'}.")

        mime_ok = any(
            content_type == prefix or content_type.startswith(prefix)
            for prefix in rules["mime_prefixes"]
        )

        if not mime_ok and content_type not in {"", "application/octet-stream"}:
            raise ValueError("El tipo de contenido del archivo no es válido.")
