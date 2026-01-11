"""
Sahayak AI - Main FastAPI Application
=====================================
Voice-Enabled Local Assistant for Everyday India

Detailed logging added to track every step of the request lifecycle.
"""

import logging
import base64
import os
import time
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION, 
    ALLOWED_ORIGINS, MAX_AUDIO_SIZE, AUDIO_DIR
)
from schemas import AskRequest, AskResponse, HealthResponse, ErrorResponse
from speech_to_text import get_stt
from text_to_speech import get_tts
from reasoning import get_reasoning_engine
from osm_service import get_osm_service
from supabase_client import get_supabase_client
from location_service import get_location_service

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SAHAYAK_MAIN")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events with logging."""
    logger.info("========================================")
    logger.info(f"INIT: Starting {APP_NAME} v{APP_VERSION}")
    logger.info("========================================")
    
    os.makedirs(AUDIO_DIR, exist_ok=True)
    logger.info(f"FILESYSTEM: Storage directory ready at {AUDIO_DIR}")
    
    # Initialize components
    logger.info("BOOT: Initializing core services...")
    get_stt()
    get_tts()
    get_reasoning_engine()
    logger.info("BOOT: All services loaded and ready.")
    
    yield
    logger.info("SHUTDOWN: Cleaning up resources...")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For flexible development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check with service status logging."""
    logger.info("HEALTH: Received status request.")
    stt = get_stt()
    stt_info = stt.get_status()
    stt_ready = stt.is_ready
    tts_ready = get_tts().is_ready
    ai_ready = get_reasoning_engine().is_ready
    db_ready = get_supabase_client().is_ready
    
    stt_status = "ready"
    if not stt_ready:
        if not stt_info.get("available", False):
            stt_status = "library_missing"
        else:
            stt_status = "model_missing"

    # Check FFmpeg
    ffmpeg_ready = False
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=1)
        ffmpeg_ready = True
    except:
        pass

    status = {
        "vosk": stt_status,
        "espeak": "ready" if tts_ready else "missing_system",
        "ffmpeg": "ready" if ffmpeg_ready else "missing",
        "gemini": "active" if ai_ready else "inactive",
        "supabase": "connected" if db_ready else "fallback",
        "osm": "online"
    }
    
    if not stt_ready or not ffmpeg_ready:
        logger.info(f"👉 VOSK/Voice Note: {'Install FFmpeg' if not ffmpeg_ready else ''} {'Download Hindi model' if stt_ready == False and stt_status == 'model_missing' else ''}")
    return HealthResponse(
        status="running" if ai_ready else "limited",
        version=APP_VERSION,
        services=status
    )

@app.post("/ask", response_model=AskResponse, tags=["Assistant"])
async def ask_assistant(request: AskRequest):
    """
    Main request handler with step-by-step trace logging.
    """
    request_id = f"req_{int(time.time())}"
    logger.info(f"[{request_id}] >>> NEW REQUEST RECEIVED")
    req_start = time.time()
    
    try:
        transcribed_text = None
        query_text = request.text_query
        
        # 1. Processing Audio Input
        if request.audio_base64 and not query_text:
            logger.info(f"[{request_id}] STEP 1: Processing audio input...")
            stt = get_stt()
            try:
                audio_bytes = base64.b64decode(request.audio_base64)
                logger.debug(f"[{request_id}] Decoded {len(audio_bytes)} bytes of audio data")
                
                if len(audio_bytes) > MAX_AUDIO_SIZE:
                    logger.error(f"[{request_id}] Audio too large: {len(audio_bytes)} bytes")
                    raise HTTPException(400, "Audio too large")
                
                stt_start = time.time()
                transcribed_text, error = stt.transcribe_from_bytes(audio_bytes, "webm")
                stt_duration = time.time() - stt_start
                
                if error:
                    logger.warning(f"[{request_id}] STT failed: {error}")
                    return AskResponse(success=False, text_response="आवाज़ समझ नहीं आई।", error_message=error)
                
                query_text = transcribed_text
                logger.info(f"[{request_id}] TRANSCRIPTION: '{query_text}' (took {stt_duration:.2f}s)")
            except Exception as e:
                logger.error(f"[{request_id}] Audio processing crash: {e}")
                return AskResponse(success=False, text_response="ऑडियो एरर।", error_message=str(e))
        
        if not query_text:
            logger.warning(f"[{request_id}] Empty query received.")
            return AskResponse(success=False, text_response="कृपया कुछ बोलें।")

        logger.info(f"[{request_id}] QUERY_TEXT: {query_text}")

        # 2. Location Context
        logger.info(f"[{request_id}] STEP 2: Fetching location context...")
        loc_svc = get_location_service()
        lat, lon, source = loc_svc.get_location(request.latitude, request.longitude, query_text)
        logger.info(f"[{request_id}] LOCATION: {lat}, {lon} (Source: {source})")
        
        # 3. Smart Query Analysis
        logger.info(f"[{request_id}] STEP 3: Routing query (Smart Analysis)...")
        reasoning = get_reasoning_engine()
        analysis = reasoning.analyze_query(query_text)
        data_source = analysis["data_source"]
        logger.info(f"[{request_id}] ROUTE: Using {data_source.upper()} as primary source.")

        # 4. Data Extraction
        nearby_places = []
        knowledge_results = []
        
        if data_source == "map" and analysis.get("place_type"):
            logger.info(f"[{request_id}] STEP 4: Querying Overpass API for '{analysis['place_type']}'...")
            osm = get_osm_service()
            nearby_places = await osm.find_nearby(lat, lon, analysis["place_type"], radius=3000)
            logger.info(f"[{request_id}] DATA: Found {len(nearby_places)} nearby locations.")
            
        elif data_source == "knowledge":
            logger.info(f"[{request_id}] STEP 4: Searching Supabase Knowledge Base...")
            supabase = get_supabase_client()
            knowledge_results = await supabase.search_knowledge(query_text, limit=2)
            logger.info(f"[{request_id}] DATA: Retrieved {len(knowledge_results)} kb entries.")

        # 5. AI Response Generation
        logger.info(f"[{request_id}] STEP 5: Generating AI response...")
        gen_start = time.time()
        response_text, error = reasoning.generate_response(
            query_text, 
            nearby_places=nearby_places, 
            knowledge_results=knowledge_results,
            data_source=data_source
        )
        gen_duration = time.time() - gen_start
        logger.info(f"[{request_id}] AI: Response generated in {gen_duration:.2f}s")
        
        # 6. TTS Synthesis
        audio_output = None
        tts = get_tts()
        if tts.is_ready and response_text:
            logger.info(f"[{request_id}] STEP 6: Synthesizing voice response...")
            # Use concise version for speech
            speech_text = response_text[:350] 
            audio_output, tts_error = tts.synthesize_to_base64(speech_text)
            if tts_error:
                logger.warning(f"[{request_id}] TTS Synthesis skipped: {tts_error}")

        total_duration = time.time() - req_start
        logger.info(f"[{request_id}] <<< REQUEST COMPLETE in {total_duration:.2f}s")
        
        return AskResponse(
            success=True,
            text_response=response_text,
            audio_base64=audio_output,
            transcribed_text=transcribed_text,
            detected_intent=analysis["intent"],
            nearby_places=nearby_places if nearby_places else None
        )
        
    except Exception as e:
        logger.exception(f"[{request_id}] UNHANDLED CRASH: {e}")
        return AskResponse(success=False, text_response="सर्वर एरर।", error_message=str(e))

@app.get("/", tags=["System"])
async def root():
    return {"message": "Sahayak AI Backend Online", "status": "active"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Launcher: Starting development server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
