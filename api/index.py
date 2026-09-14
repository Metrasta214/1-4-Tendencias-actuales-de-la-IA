import base64
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.classes.audio_processor import AudioProcessor
from backend.classes.document_processor import DocumentProcessor
from backend.classes.file_validator import FileValidator
from backend.classes.image_processor import ImageProcessor
from backend.classes.translator import Translator

load_dotenv()

app = FastAPI(
    title="LinguaAI - Traductor Multimodal API",
    version="1.0.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500,http://localhost:3000"
    ).split(",")
    if origin.strip()
]

if os.getenv("ALLOW_ALL_ORIGINS", "false").lower() == "true":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

validator = FileValidator()
translator_service = None
audio_processor = None
document_processor = None
image_processor = None


def get_services():
    global translator_service, audio_processor, document_processor, image_processor

    if translator_service is None:
        translator_service = Translator()
        audio_processor = AudioProcessor(translator_service)
        document_processor = DocumentProcessor(translator_service)
        image_processor = ImageProcessor(translator_service)

    return translator_service, audio_processor, document_processor, image_processor


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=12000)
    source_language: str = Field(..., pattern="^(es|en)$")
    target_language: str = Field(..., pattern="^(es|en)$")


class ChatRequest(TranslationRequest):
    history: list[dict[str, str]] = Field(default_factory=list, max_length=8)


def ensure_different_languages(source_language: str, target_language: str) -> None:
    if source_language == target_language:
        raise HTTPException(
            status_code=400,
            detail="El idioma de origen y destino deben ser diferentes."
        )


@app.get("/")
def root():
    return {"message": "LinguaAI API", "status": "ok"}


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "LinguaAI API"}


@app.post("/api/translate")
def translate(request: TranslationRequest):
    ensure_different_languages(request.source_language, request.target_language)

    try:
        translator, _, _, _ = get_services()
        result = translator.translate(
            request.text,
            request.source_language,
            request.target_language,
        )
        return {"original": request.text, "translation": result}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/chat")
def chat(request: ChatRequest):
    ensure_different_languages(request.source_language, request.target_language)

    try:
        translator, _, _, _ = get_services()
        result = translator.translate_chat(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            history=request.history,
        )
        return {"original": request.text, "translation": result}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/audio")
async def audio(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...),
):
    ensure_different_languages(source_language, target_language)
    contents = await file.read()

    validator.validate_upload(
        filename=file.filename or "",
        content_type=file.content_type or "",
        size_bytes=len(contents),
        category="audio",
    )

    try:
        _, audio_processor, _, _ = get_services()
        result = audio_processor.process(
            filename=file.filename or "audio",
            content=contents,
            source_language=source_language,
            target_language=target_language,
        )
        return {
            "transcript": result["transcript"],
            "translation": result["translation"],
            "audio_mime": result["audio_mime"],
            "audio_base64": base64.b64encode(result["audio_bytes"]).decode("utf-8"),
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/document")
async def document(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...),
):
    ensure_different_languages(source_language, target_language)
    contents = await file.read()

    validator.validate_upload(
        filename=file.filename or "",
        content_type=file.content_type or "",
        size_bytes=len(contents),
        category="document",
    )

    try:
        _, _, document_processor, _ = get_services()
        return document_processor.process(
            filename=file.filename or "document",
            content=contents,
            source_language=source_language,
            target_language=target_language,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/image")
async def image(
    file: UploadFile = File(...),
    source_language: str = Form(...),
    target_language: str = Form(...),
):
    ensure_different_languages(source_language, target_language)
    contents = await file.read()

    validator.validate_upload(
        filename=file.filename or "",
        content_type=file.content_type or "",
        size_bytes=len(contents),
        category="image",
    )

    try:
        _, _, _, image_processor = get_services()
        return image_processor.process(
            filename=file.filename or "image",
            content=contents,
            content_type=file.content_type or "image/jpeg",
            source_language=source_language,
            target_language=target_language,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
