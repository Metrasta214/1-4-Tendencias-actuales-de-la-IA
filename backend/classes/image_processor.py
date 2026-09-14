import base64
import os


class ImageProcessor:
    """Envía una imagen con texto visible al modelo de visión."""

    def __init__(self, translator):
        self.translator = translator
        self.model = os.getenv("OPENAI_VISION_MODEL", "gpt-4.1-nano")

    def process(self, filename, content, content_type, source_language, target_language):
        image_data = base64.b64encode(content).decode("utf-8")
        data_url = f"data:{content_type};base64,{image_data}"

        source = "español" if source_language == "es" else "inglés"
        target = "español" if target_language == "es" else "inglés"

        response = self.translator.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "developer",
                    "content": (
                        "Analiza únicamente el texto visible de la imagen. Tradúcelo al idioma "
                        "de destino. Conserva nombres, números, fechas, unidades y siglas. "
                        "Si no hay texto legible, devuelve exactamente [NO_LEGIBLE_TEXT]. "
                        "No describas la imagen y no agregues explicaciones."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                f"Idioma del texto: {source}\n"
                                f"Idioma destino: {target}\n"
                                "Extrae y traduce todo el texto legible."
                            ),
                        },
                        {
                            "type": "input_image",
                            "image_url": data_url,
                            "detail": "auto",
                        },
                    ],
                },
            ],
        )

        translated = (response.output_text or "").strip()
        if not translated:
            raise ValueError("La IA no devolvió una traducción.")
        if translated == "[NO_LEGIBLE_TEXT]":
            raise ValueError(
                "La imagen no contiene texto legible o la calidad impide interpretarlo."
            )

        return {"filename": filename, "translation": translated}
