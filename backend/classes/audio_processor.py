import io
import os
from pathlib import Path

from .translator import Translator


class AudioProcessor:
    """Transcribe, traduce y genera el audio de salida."""

    def __init__(self, translator: Translator):
        self.translator = translator
        self.transcription_model = os.getenv("OPENAI_TRANSCRIPTION_MODEL", "gpt-4o-mini-transcribe")
        self.tts_model = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
        self.voice = os.getenv("OPENAI_TTS_VOICE", "alloy")
        self.client = translator.client

    def process(self, filename, content, source_language, target_language):
        language_name = "Spanish" if source_language == "es" else "English"

        file_buffer = io.BytesIO(content)
        file_buffer.name = Path(filename).name

        transcription = self.client.audio.transcriptions.create(
            model=self.transcription_model,
            file=file_buffer,
            prompt=f"The spoken language is {language_name}.",
        )

        transcript = (transcription.text or "").strip()
        if not transcript:
            raise ValueError("No se pudo obtener contenido hablado utilizable del audio.")

        translated = self.translator.translate(
            transcript,
            source_language,
            target_language,
        )

        speech = self.client.audio.speech.create(
            model=self.tts_model,
            voice=self.voice,
            input=translated,
            response_format="mp3",
        )

        audio_bytes = speech.read()
        if not audio_bytes:
            raise RuntimeError("No se pudo generar el audio traducido.")

        return {
            "transcript": transcript,
            "translation": translated,
            "audio_bytes": audio_bytes,
            "audio_mime": "audio/mpeg",
        }
