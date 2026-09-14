import os

from openai import OpenAI


LANGUAGE_NAMES = {"es": "español", "en": "inglés"}


class Translator:
    """Servicio de traducción basado en OpenAI."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta OPENAI_API_KEY en las variables de entorno del backend.")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-nano")

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        source = LANGUAGE_NAMES[source_language]
        target = LANGUAGE_NAMES[target_language]

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "developer",
                    "content": (
                        "Eres un traductor profesional español-inglés. "
                        "Traduce preservando significado, tono, nombres propios, cifras, fechas, "
                        "unidades, siglas y términos técnicos. No agregues explicaciones, prefacios "
                        "ni comentarios. Devuelve únicamente la traducción."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Idioma origen: {source}\nIdioma destino: {target}\n\nTexto:\n{text}",
                },
            ],
        )

        result = (response.output_text or "").strip()
        if not result:
            raise RuntimeError("La IA no devolvió una traducción.")
        return result

    def translate_chat(self, text, source_language, target_language, history):
        source = LANGUAGE_NAMES[source_language]
        target = LANGUAGE_NAMES[target_language]

        history_text = "\n".join(
            f"Original: {item.get('original', '')}\nTraducción: {item.get('translation', '')}"
            for item in history[-8:]
        )

        prompt = (
            f"Idioma de origen: {source}\n"
            f"Idioma de destino: {target}\n\n"
            "Contexto previo:\n"
            f"{history_text or '(sin contexto previo)'}\n\n"
            f"Nuevo mensaje:\n{text}"
        )

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "developer",
                    "content": (
                        "Traduce mensajes conversacionales de forma natural. Mantén el contexto "
                        "y la intención del hablante. No respondas la conversación ni agregues "
                        "contenido. Devuelve exclusivamente la traducción."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        result = (response.output_text or "").strip()
        if not result:
            raise RuntimeError("La IA no devolvió una traducción.")
        return result
