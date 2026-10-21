# server.py - FastAPI Web Server & REST API for IVERI AI Terminal
import os
import sys
import json
import hashlib
import tempfile
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure local imports work cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

import config
import commands
import gpt
import online_rag
import tts

app = FastAPI(
    title="IVERI AI Terminal",
    description="Next-Gen Edge-Cloud Voice & Terminal Assistant with Gemini Flash & Online RAG",
    version="2.0.0"
)

# CORS middleware for open web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static & cache directories exist
STATIC_DIR = Path(__file__).parent / "static"
CACHE_DIR = Path(__file__).parent / "cache" / "audio"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class ChatRequest(BaseModel):
    message: str
    use_history: Optional[bool] = True
    voice_response: Optional[bool] = True
    voice_choice: Optional[str] = "new"  # 'new' (ElevenLabs Flash v2.5) or 'classic' (Offline system voice)
    force_rag: Optional[bool] = False


@app.get("/health")
def health_check():
    """Health check endpoint for cloud hosting providers (Render, Railway, Fly.io)"""
    return {
        "status": "healthy",
        "service": "IVERI AI Terminal",
        "engine": "Google Gemini Flash",
        "rag": "Online RAG (Google News RSS & Wikipedia)",
        "voice": "ElevenLabs Flash v2.5"
    }


@app.get("/api/status")
def get_system_status():
    """Returns real-time status of APIs, memory, and engine configuration"""
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    has_eleven = bool(os.getenv("ELEVENLABS_API_KEY"))
    has_porcupine = bool(os.getenv("PICOVOICE_ACCESS_KEY"))

    # Determine active Flash model
    active_model = gpt.FLASH_MODELS[0] if hasattr(gpt, "FLASH_MODELS") else "gemini-3.6-flash"

    return {
        "status": "online",
        "gemini_active": has_gemini,
        "active_model": active_model,
        "elevenlabs_active": has_eleven,
        "elevenlabs_model": getattr(config, "ELEVENLABS_MODEL_ID", "eleven_flash_v2_5"),
        "wake_word_available": has_porcupine,
        "rag_sources": ["Google News RSS", "Wikipedia REST API"],
        "platform": sys.platform
    }


@app.post("/api/chat")
def handle_chat(req: ChatRequest):
    """
    Unified chat endpoint:
    1. Checks for 0ms deterministic local/system commands
    2. Fallbacks to Gemini Flash + Online RAG
    3. Optionally synthesizes voice audio with ElevenLabs Flash v2.5
    """
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Empty message received")

    # Step 1: Check for local/system command
    is_cmd, cmd_resp = commands.handle_command(user_msg, execute=True)
    if is_cmd and cmd_resp:
        response_text = cmd_resp
        source = "command"
    else:
        # Step 2: Route through Gemini Flash with real-time Online RAG
        response_text = gpt.get_response(
            user_msg,
            use_history=req.use_history,
            force_rag=req.force_rag
        )
        # Determine if RAG was used
        is_rag_query = req.force_rag or online_rag.should_use_rag(user_msg)
        source = "rag" if is_rag_query else "ai"

    # Step 3: Handle Audio Generation based on user choice ('new' vs 'classic')
    audio_id = None
    audio_url = None
    voice_engine = "classic" if req.voice_choice in ("classic", "old", "system") else "new"

    if req.voice_response and response_text and voice_engine == "new":
        try:
            cache_hash = hashlib.md5(f"eleven_{response_text}".encode("utf-8")).hexdigest()
            cache_file = CACHE_DIR / f"{cache_hash}.mp3"
            
            eleven_key = os.getenv("ELEVENLABS_API_KEY")
            if cache_file.exists():
                audio_id = cache_hash
                audio_url = f"/api/audio/{audio_id}"
            elif eleven_key and len(eleven_key) > 10:
                audio_bytes = tts.synthesize_elevenlabs_speech(response_text)
                if audio_bytes:
                    with open(cache_file, "wb") as f:
                        f.write(audio_bytes)
                    audio_id = cache_hash
                    audio_url = f"/api/audio/{audio_id}"
        except Exception:
            pass

    return {
        "user_message": user_msg,
        "response": response_text,
        "source": source,
        "voice_engine": voice_engine,
        "audio_url": audio_url
    }


@app.get("/api/audio/{audio_id}")
def stream_audio(audio_id: str):
    """Streams cached MP3 audio directly to the browser"""
    # Sanitize ID to prevent path traversal
    safe_id = "".join(c for c in audio_id if c.isalnum() or c in ("-", "_"))
    audio_path = CACHE_DIR / f"{safe_id}.mp3"
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
        
    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=f"iveri_{safe_id}.mp3"
    )


@app.post("/api/transcribe")
async def transcribe_audio(request: Request):
    """Fallback audio transcription endpoint using SpeechRecognition"""
    try:
        body = await request.body()
        if not body:
            return {"transcript": "", "error": "Empty audio data"}
            
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(body)
            tmp_path = tmp.name

        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        try:
            os.remove(tmp_path)
        except Exception:
            pass

        return {"transcript": text}
    except Exception as e:
        return {"transcript": "", "error": str(e)}


# Serve single-page frontend static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_index():
    """Serves the main terminal UI"""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>IVERI AI Terminal is Running</h1><p>Frontend assets loading...</p>")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"[*] Starting IVERI AI Server on port {port}...")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
