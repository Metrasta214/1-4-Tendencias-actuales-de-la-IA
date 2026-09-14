# Despliegue del backend en Vercel

## 1. Estructura

El backend de FastAPI se encuentra en:

```text
api/index.py
```

Vercel utiliza este archivo como punto de entrada del backend Python. La configuración adicional está en:

```text
vercel.json
```

## 2. Crear proyecto

Desde la raíz del proyecto:

```powershell
npm install -g vercel
vercel login
vercel
```

Cuando Vercel pregunte por el proyecto, selecciona o crea el proyecto que quieras usar.

## 3. Variables de entorno

En Vercel entra a:

```text
Project → Settings → Environment Variables
```

Agrega:

```text
OPENAI_API_KEY
OPENAI_TEXT_MODEL
OPENAI_VISION_MODEL
OPENAI_TRANSCRIPTION_MODEL
OPENAI_TTS_MODEL
OPENAI_TTS_VOICE
ALLOWED_ORIGINS
ALLOW_ALL_ORIGINS
```

Valores recomendados:

```text
OPENAI_TEXT_MODEL=gpt-4.1-nano
OPENAI_VISION_MODEL=gpt-4.1-nano
OPENAI_TRANSCRIPTION_MODEL=gpt-4o-mini-transcribe
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TTS_VOICE=alloy
ALLOW_ALL_ORIGINS=false
```

Para `ALLOWED_ORIGINS` coloca la URL exacta de GitHub Pages:

```text
https://TU-USUARIO.github.io
```

No coloques la API Key en `frontend/`.

## 4. Desplegar

```powershell
vercel --prod
```

La URL resultante será similar a:

```text
https://tu-proyecto.vercel.app
```

## 5. Comprobar backend

Abre:

```text
https://tu-proyecto.vercel.app/api/health
```

Debe responder:

```json
{
  "status": "healthy",
  "service": "LinguaAI API"
}
```

Después prueba:

```text
https://tu-proyecto.vercel.app/docs
```

FastAPI mostrará la documentación interactiva.

## 6. Conectar GitHub Pages

En:

```text
frontend/js/config.js
```

cambia:

```javascript
const API_BASE_URL = "http://127.0.0.1:8000";
```

por:

```javascript
const API_BASE_URL = "https://tu-proyecto.vercel.app";
```

Después publica `frontend/` en GitHub Pages.

## 7. CORS

Si GitHub Pages es:

```text
https://metrasta214.github.io
```

entonces en Vercel:

```text
ALLOWED_ORIGINS=https://metrasta214.github.io
```

Después de cambiar variables de entorno hay que volver a desplegar.

## 8. Prueba final

1. `GET /api/health`
2. `POST /api/translate`
3. `POST /api/chat`
4. `POST /api/audio`
5. `POST /api/document`
6. `POST /api/image`

La API Key nunca debe enviarse desde el navegador.
