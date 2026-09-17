import io
import os
from pathlib import Path

from .translator import Translator


class AudioProcessor:
    """
    Procesa archivos de audio.

    Flujo:
    1. Transcribe el audio.
    2. Traduce la transcripción.
    3. Genera audio con la traducción.
    """

    def __init__(self, translator: Translator):

        self.translator = translator

        # ----------------------------------------------------
        # MODELOS DE OPENAI
        # ----------------------------------------------------

        self.transcription_model = os.getenv(
            "OPENAI_TRANSCRIPTION_MODEL",
            "gpt-4o-mini-transcribe"
        )

        self.tts_model = os.getenv(
            "OPENAI_TTS_MODEL",
            "gpt-4o-mini-tts"
        )

        self.voice = os.getenv(
            "OPENAI_TTS_VOICE",
            "alloy"
        )

        # ----------------------------------------------------
        # CLIENTE OPENAI
        # ----------------------------------------------------

        self.client = translator.client

    # ========================================================
    # PROCESAR AUDIO
    # ========================================================

    def process(
        self,
        filename,
        content,
        source_language,
        target_language
    ):

        # ----------------------------------------------------
        # VALIDAR CONTENIDO
        # ----------------------------------------------------

        if not content:

            raise ValueError(
                "El contenido del audio está vacío."
            )

        # ----------------------------------------------------
        # DETERMINAR IDIOMA
        # ----------------------------------------------------

        language_name = (
            "Spanish"
            if source_language == "es"
            else "English"
        )

        # ----------------------------------------------------
        # CREAR BUFFER
        # ----------------------------------------------------

        file_buffer = io.BytesIO(content)

        file_buffer.name = Path(
            filename or "audio"
        ).name

        # ====================================================
        # 1. TRANSCRIPCIÓN
        # ====================================================

        transcription = self.client.audio.transcriptions.create(
            model=self.transcription_model,
            file=file_buffer,
            prompt=(
                f"The spoken language is "
                f"{language_name}."
            ),
        )

        transcript = (
            transcription.text or ""
        ).strip()

        if not transcript:

            raise ValueError(
                "No se pudo obtener contenido "
                "hablado utilizable del audio."
            )

        # ====================================================
        # 2. TRADUCCIÓN
        # ====================================================

        translated = self.translator.translate(
            transcript,
            source_language,
            target_language,
        )

        translated = (
            translated or ""
        ).strip()

        if not translated:

            raise ValueError(
                "No se obtuvo una traducción válida."
            )

        # ====================================================
        # 3. TEXTO A VOZ
        # ====================================================

        speech = self.client.audio.speech.create(
            model=self.tts_model,
            voice=self.voice,
            input=translated,
            response_format="mp3",
        )

        # ====================================================
        # 4. OBTENER AUDIO
        # ====================================================

        audio_bytes = speech.read()

        if not audio_bytes:

            raise RuntimeError(
                "No se pudo generar el audio traducido."
            )

        # ====================================================
        # RESPUESTA
        # ====================================================

        return {
            "transcript": transcript,
            "translation": translated,
            "audio_bytes": audio_bytes,
            "audio_mime": "audio/mpeg",
        }