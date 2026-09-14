# LinguaAI — Traductor Multimodal Español ↔ Inglés

Aplicación Web de Inteligencia Artificial que integra traducción de texto conversacional, audio, documentos e imágenes dentro de una sola plataforma.

## Incluye

- Español → Inglés e Inglés → Español.
- Chat bilingüe con original y traducción.
- Audio: transcripción + traducción + audio de salida.
- Documentos: PDF, DOCX y TXT.
- Imágenes: lectura de texto visible + traducción.
- Validación de extensiones, MIME y tamaño.
- Manejo de errores.
- Programación Orientada a Objetos.
- OpenAI mediante backend Python.
- CORS configurable.
- Colección de Postman.
- Preparado para Vercel y GitHub Pages.

## Modelo

El proyecto usa `gpt-4.1-nano` como modelo principal para texto e imágenes por su bajo costo y baja latencia. Para audio utiliza `gpt-4o-mini-transcribe` y `gpt-4o-mini-tts`.

Puedes cambiar los modelos desde `.env` sin modificar el código.

## Arquitectura

```text
GitHub Pages
    │
    │ HTTPS / REST
    ▼
Vercel
    │
    ├── FastAPI
    ├── Translator
    ├── AudioProcessor
    ├── DocumentProcessor
    ├── ImageProcessor
    └── FileValidator
            │
            ▼
        OpenAI API
```

## Instalación en Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env` y coloca:

```env
OPENAI_API_KEY=tu_clave_real
```

Después:

```powershell
uvicorn api.index:app --reload --port 8000
```

En otra terminal:

```powershell
python -m http.server 5500 --directory frontend
```

Abre:

```text
http://127.0.0.1:5500
```

## Postman

Importa:

```text
postman/Generales.postman_collection.json
```

Las pruebas locales usan:

```text
http://127.0.0.1:8000
```

## Vercel

El backend Python/FastAPI está preparado para Vercel mediante:

```text
api/index.py
vercel.json
```

Vercel utiliza `api/index.py` como entrada del backend Python. El despliegue puede hacerse con:

```powershell
npm install -g vercel
vercel login
vercel
vercel --prod
```

Configura en Vercel las variables de entorno indicadas en `VERCEL.md`, especialmente `OPENAI_API_KEY` y `ALLOWED_ORIGINS`.

La comprobación básica después del despliegue es:

```text
https://TU-PROYECTO.vercel.app/api/health
```

Consulta `VERCEL.md` para el procedimiento completo.

## GitHub Pages

Publica el contenido de `frontend/`.

Antes de publicar, cambia en:

```text
frontend/js/config.js
```

la URL local por la URL pública de Vercel.

## Backend

El backend está en:

```text
api/index.py
```

Desde la raíz:

```powershell
npm i -g vercel
vercel login
vercel
```

En Vercel agrega como variables de entorno:

```text
OPENAI_API_KEY
OPENAI_TEXT_MODEL
OPENAI_VISION_MODEL
OPENAI_TRANSCRIPTION_MODEL
OPENAI_TTS_MODEL
OPENAI_TTS_VOICE
ALLOWED_ORIGINS
```

`ALLOWED_ORIGINS` debe contener la URL exacta de tu GitHub Pages.

## Seguridad

La API Key no está en el frontend. `.env` está ignorado por Git. El backend valida archivos y limita su tamaño a 10 MB. Los orígenes permitidos son configurables.

## Limitaciones

- Un PDF escaneado como imagen puede no producir texto con `pypdf`.
- Los documentos tienen un límite de 30,000 caracteres para controlar consumo.
- Audio y archivos grandes dependen de la conexión y del servicio.
- Deben configurarse las URLs reales antes del despliegue final.

## Autor

Álvaro Madrid Morales
