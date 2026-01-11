"""
Sahayak AI - Smart Reasoning Engine
====================================
Intelligently routes queries to:
- Overpass API (map/location queries)
- Supabase (procedural knowledge)
- AI self-knowledge (general queries)
"""

import logging
import os
import json
import time
from typing import Optional, Dict, Any, Tuple, List
from dotenv import load_dotenv

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
    logger.info("Successfully imported Google Gen AI SDK")
except ImportError:
    GEMINI_AVAILABLE = False
    logger.error("Google Gen AI SDK NOT found. Please install: pip install google-genai")

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "gemini-1.5-flash"  # Default stable model

# Enhanced system prompt for Indian context
SYSTEM_PROMPT = """You are Sahayak AI, a helpful voice assistant for Indian citizens.

Your capabilities:
1. LOCATION QUERIES: Finding nearby hospitals, banks, ATMs, petrol pumps, police stations, etc.
2. PROCEDURE QUERIES: Explaining how to do Aadhaar update, PAN card, passport, mobile recharge, etc.
3. GENERAL QUERIES: Answering general questions about India, government schemes, etc.

Guidelines:
- Respond in the SAME LANGUAGE as the user (Hindi/English/Hinglish)
- Give step-by-step instructions for procedures
- Include distance and names for location-based answers
- Be concise but complete
- Use simple language anyone can understand
"""

# Keywords for routing - expanded with variations
LOCATION_KEYWORDS = [
    "nearby", "near me", "closest", "nearest", "where is", "find", "locate", "directions", 
    "नजदीक", "नजदीकी", "पास में", "कहाँ है", "कहां है", "किधर है", "दिखाओ", "बताओ"
]
PROCEDURE_KEYWORDS = ["कैसे करें", "कैसे बनाएं", "how to", "process", "procedure", "steps", "apply for", "आवेदन", "तरीका"]

class ReasoningEngine:
    def __init__(self):
        self.client = None
        self.is_ready = False
        self.model_id = MODEL_ID
        logger.info("Initializing ReasoningEngine...")
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        if not GEMINI_API_KEY:
            logger.error("❌ GEMINI_API_KEY is missing from environment variables!")
            return

        # Using STABLE models (gemini-1.5-flash is best for free tier)
        # IMPORTANT: gemini-2.5 does NOT exist yet In the official API.
        models_to_try = [
            "gemini-1.5-flash",      # High quota stable
            "gemini-2.0-flash",      # Modern stable
            "gemini-2.0-flash-lite", # Lightweight stable
            "gemini-pro"             # Robust fallback
        ]
        
        for model_name in models_to_try:
            try:
                logger.info(f"Attempting to initialize model: {model_name}...")
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                # Test call to verify model availability
                self.client.models.generate_content(model=model_name, contents="test")
                self.model_id = model_name
                self.is_ready = True
                logger.info(f"✅ Success! ReasoningEngine is active using model: {self.model_id}")
                return
            except Exception as e:
                logger.warning(f"⚠️ Model {model_name} failed or restricted: {str(e)[:100]}...")
        
        logger.error("❌ CRITICAL: All Gemini models failed to initialize. Check API Quota or Key.")

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Detects if a query is for a Map (Location), Knowledge (Procedures), or AI (General).
        Uses keywords first, then AI for fine-tuning.
        """
        logger.info(f"🔍 Analyzing User Query: '{query}'")
        start_time = time.time()
        
        query_lower = query.lower()
        
        # 1. Place Type Detection (Heuristic)
        place_keywords = {
            "hospital": ["hospital", "अस्पताल", "doctor", "medical", "हॉस्पिटल"],
            "bank": ["bank", "बैंक", "atm"],
            "pharmacy": ["pharmacy", "medical store", " दवा", "मेडिकल"],
            "police": ["police", "thana", "पुलिस", "थाना"],
            "petrol": ["petrol", "fuel", "पेट्रोल"],
            "restaurant": ["restaurant", "food", "khana", "dhaba", "खाना", "होटल"],
            "grocery": ["grocery", "kirana", "किराना", "store"],
            "temple": ["temple", "mandir", "मंदिर"],
            "csc": ["csc", " केंद्र", "ई-सेवा", "seva kendra"]
        }
        
        detected_place = None
        for ptype, keywords in place_keywords.items():
            if any(kw in query_lower for kw in keywords):
                detected_place = ptype
                break
        
        # 2. Heuristic Indicators
        is_location_words = any(kw in query_lower for kw in LOCATION_KEYWORDS)
        is_procedure_words = any(kw in query_lower for kw in PROCEDURE_KEYWORDS)
        
        # Initial status
        data_source = "ai"
        intent = "general_info"
        
        if (is_location_words or detected_place) and not is_procedure_words:
            data_source = "map"
            intent = "find_location"
        elif is_procedure_words:
            data_source = "knowledge"
            intent = "process_help"

        # 3. AI Refinement (If ready)
        if self.is_ready:
            try:
                prompt = f"""Analyze query: "{query}"
                Return JSON only:
                {{
                  "intent": "find_location | process_help | general",
                  "place_type": "string or null",
                  "requires_map": boolean
                }}"""
                
                resp = self.client.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                ai = json.loads(resp.text)
                logger.info(f"AI Analysis Result: {ai}")
                
                # AI can override or refine
                if ai.get("requires_map"):
                    data_source = "map"
                    intent = "find_location"
                    if not detected_place: 
                        detected_place = ai.get("place_type")
                elif ai.get("intent") == "process_help":
                    data_source = "knowledge"
                    intent = "process_help"
                
            except Exception as e:
                logger.debug(f"AI refinement failed: {e}")

        # Final cleanup for map
        if data_source == "map" and not detected_place:
            # Fallback if we know its a map query but don't have a specific type
            detected_place = "hospital" # Sensible default if searching 'near me'
            logger.info("Defaulting place_type to 'hospital' for general location query")

        duration = time.time() - start_time
        logger.info(f"Analysis Complete ({duration:.2f}s) -> Source: {data_source.upper()}, Place: {detected_place}")
        
        return {
            "data_source": data_source,
            "place_type": detected_place,
            "intent": intent,
            "category": self._detect_category(query_lower)
        }

    def _detect_category(self, q: str) -> str:
        if any(w in q for w in ["hospital", "doctor", "अस्पताल"]): return "health"
        if any(w in q for w in ["bank", "atm", "बैंक"]): return "banking"
        if any(w in q for w in ["recharge", "mobile", "सिम"]): return "telecom"
        if any(w in q for w in ["aadhaar", "pan", "passport", "आधार"]): return "government"
        return "general"

    def generate_response(self, query: str, **kwargs) -> Tuple[str, Optional[str]]:
        logger.info(f"✍️ Generating Response for: '{query[:50]}...'")
        start_time = time.time()
        
        if not self.is_ready:
            logger.warning("ReasoningEngine not ready. Using hardcoded fallback.")
            return "Server connection issue. Please try again later.", "Engine Not Ready"

        data_source = kwargs.get("data_source", "ai")
        context = ""
        
        if data_source == "map" and kwargs.get("nearby_places"):
            places = kwargs["nearby_places"]
            logger.info(f"Injecting Map Context: {len(places)} places found.")
            context = "Context: Nearby places found from OpenStreetMap: " + json.dumps(places[:5])
        elif data_source == "knowledge" and kwargs.get("knowledge_results"):
            kb = kwargs["knowledge_results"]
            logger.info(f"Injecting Knowledge Context: {len(kb)} entries found.")
            context = "Context: Local procedural steps: " + json.dumps(kb)

        prompt = f"{SYSTEM_PROMPT}\n{context}\nUser asks: {query}\nResponse:"
        
        try:
            logger.info(f"Calling Gemini API ({self.model_id})...")
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            text = response.text.strip()
            duration = time.time() - start_time
            logger.info(f"✅ Response Generated ({len(text)} chars) in {duration:.2f}s")
            return text, None
        except Exception as e:
            logger.error(f"❌ Gemini Generation Error: {e}")
            return "I'm having trouble thinking right now.", str(e)

# Singleton
_engine = None
def get_reasoning_engine():
    global _engine
    if _engine is None:
        _engine = ReasoningEngine()
    return _engine