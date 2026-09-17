import base64

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.classes.audio_processor import AudioProcessor
from backend.classes.document_processor import DocumentProcessor
from backend.classes.file_validator import FileValidator
from backend.classes.image_processor import ImageProcessor
from backend.classes.translator import Translator


# ============================================================
# APLICACIÓN
# ============================================================

app = FastAPI(
    title="LinguaAI - Traductor Multimodal API",
    version="1.0.0",
    description="Backend para traducción español-inglés mediante OpenAI."
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://metrasta214.github.io",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ============================================================
# SERVICIOS
# ============================================================

validator = FileValidator()

translator_service = None
audio_processor = None
document_processor = None
image_processor = None


def get_services():

    global translator_service
    global audio_processor
    global document_processor
    global image_processor

    if translator_service is None:

        translator_service = Translator()

        audio_processor = AudioProcessor(
            translator_service
        )

        document_processor = DocumentProcessor(
            translator_service
        )

        image_processor = ImageProcessor(
            translator_service
        )

    return (
        translator_service,
        audio_processor,
        document_processor,
        image_processor,
    )


# ============================================================
# MODELOS
# ============================================================

class TranslationRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
        max_length=12000
    )

    source_language: str = Field(
        ...,
        pattern="^(es|en)$"
    )

    target_language: str = Field(
        ...,
        pattern="^(es|en)$"
    )


class ChatRequest(TranslationRequest):

    history: list[dict[str, str]] = Field(
        default_factory=list,
        max_length=8
    )


# ============================================================
# VALIDACIÓN DE IDIOMAS
# ============================================================

def ensure_different_languages(
    source_language: str,
    target_language: str
):

    if source_language == target_language:

        raise HTTPException(
            status_code=400,
            detail=(
                "El idioma de origen y destino "
                "deben ser diferentes."
            )
        )


# ============================================================
# RUTA PRINCIPAL
# ============================================================

@app.get("/")
def root():

    return {
        "message": "LinguaAI API",
        "status": "ok"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    return {
        "status": "healthy",
        "service": "LinguaAI API"
    }


# ============================================================
# TRADUCCIÓN
# ============================================================

@app.post("/api/translate")
def translate(
    request: TranslationRequest
):

    try:

        ensure_different_languages(
            request.source_language,
            request.target_language
        )

        translator, _, _, _ = get_services()

        result = translator.translate(
            request.text,
            request.source_language,
            request.target_language
        )

        return {
            "original": request.text,
            "translation": result
        }

    except HTTPException:
        raise

    except Exception as exc:

        print(
            f"ERROR /api/translate: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail=f"Error en la traducción: {str(exc)}"
        ) from exc


# ============================================================
# CHAT
# ============================================================

@app.post("/api/chat")
def chat(
    request: ChatRequest
):

    try:

        ensure_different_languages(
            request.source_language,
            request.target_language
        )

        translator, _, _, _ = get_services()

        result = translator.translate_chat(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            history=request.history
        )

        return {
            "original": request.text,
            "translation": result
        }

    except HTTPException:
        raise

    except Exception as exc:

        print(
            f"ERROR /api/chat: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail=f"Error en el chat: {str(exc)}"
        ) from exc


# ============================================================
# AUDIO
# ============================================================

@app.post("/api/audio")
async def audio(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...)
):

    try:

        # ----------------------------------------------------
        # IDIOMAS
        # ----------------------------------------------------

        ensure_different_languages(
            source_language,
            target_language
        )

        # ----------------------------------------------------
        # ARCHIVO
        # ----------------------------------------------------

        contents = await file.read()

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="El archivo de audio está vacío."
            )

        # ----------------------------------------------------
        # VALIDACIÓN
        # ----------------------------------------------------

        validator.validate_upload(
            filename=file.filename or "",
            content_type=file.content_type or "",
            size_bytes=len(contents),
            category="audio"
        )

        # ----------------------------------------------------
        # SERVICIO
        # ----------------------------------------------------

        _, audio_service, _, _ = get_services()

        if audio_service is None:

            raise RuntimeError(
                "No se pudo inicializar el servicio de audio."
            )

        # ----------------------------------------------------
        # PROCESAMIENTO
        # ----------------------------------------------------

        result = audio_service.process(
            filename=file.filename or "audio",
            content=contents,
            source_language=source_language,
            target_language=target_language
        )

        if not result:

            raise RuntimeError(
                "El procesador de audio no devolvió resultados."
            )

        if not result.get("transcript"):

            raise RuntimeError(
                "No se obtuvo una transcripción válida."
            )

        if not result.get("translation"):

            raise RuntimeError(
                "No se obtuvo una traducción válida."
            )

        if not result.get("audio_bytes"):

            raise RuntimeError(
                "No se obtuvo el audio traducido."
            )

        # ----------------------------------------------------
        # RESPUESTA
        # ----------------------------------------------------

        return {
            "transcript": result["transcript"],
            "translation": result["translation"],
            "audio_mime": result["audio_mime"],
            "audio_base64": base64.b64encode(
                result["audio_bytes"]
            ).decode("utf-8")
        }

    except HTTPException:
        raise

    except Exception as exc:

        print(
            f"ERROR /api/audio: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                f"Error procesando el audio: "
                f"{type(exc).__name__}: {str(exc)}"
            )
        ) from exc


# ============================================================
# DOCUMENTOS
# ============================================================

@app.post("/api/document")
async def document(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...)
):

    try:

        ensure_different_languages(
            source_language,
            target_language
        )

        contents = await file.read()

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="El archivo está vacío."
            )

        validator.validate_upload(
            filename=file.filename or "",
            content_type=file.content_type or "",
            size_bytes=len(contents),
            category="document"
        )

        _, _, document_service, _ = get_services()

        result = document_service.process(
            filename=file.filename or "document",
            content=contents,
            source_language=source_language,
            target_language=target_language
        )

        return result

    except HTTPException:
        raise

    except Exception as exc:

        print(
            f"ERROR /api/document: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail=f"Error procesando documento: {str(exc)}"
        ) from exc


# ============================================================
# IMÁGENES
# ============================================================

@app.post("/api/image")
async def image(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...)
):

    try:

        ensure_different_languages(
            source_language,
            target_language
        )

        contents = await file.read()

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="La imagen está vacía."
            )

        validator.validate_upload(
            filename=file.filename or "",
            content_type=file.content_type or "",
            size_bytes=len(contents),
            category="image"
        )

        _, _, _, image_service = get_services()

        result = image_service.process(
            filename=file.filename or "image",
            content=contents,
            content_type=file.content_type or "image/jpeg",
            source_language=source_language,
            target_language=target_language
        )

        return result

    except HTTPException:
        raise

    except Exception as exc:

        print(
            f"ERROR /api/image: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail=f"Error procesando imagen: {str(exc)}"
        ) from exc