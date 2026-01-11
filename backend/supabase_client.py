"""
Sahayak AI - Supabase Client Module
===================================
Handles database operations with Supabase (free tier).
Stores local procedures and knowledge for Indian users.
"""

import logging
from typing import List, Dict, Any, Optional

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase not installed. Run: pip install supabase==1.2.0")

from config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Supabase client for local knowledge storage and retrieval.
    Falls back to hardcoded knowledge when database is unavailable.
    """
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.is_ready = False
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Supabase client."""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase library not available - using fallback")
            return
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.warning("Supabase credentials not configured - using fallback")
            return
        
        try:
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            self.is_ready = True
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Supabase initialization error: {e}")
    
    async def search_knowledge(self, query: str, category: str = None, 
                                location: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search local knowledge base."""
        if not self.is_ready:
            return self._get_fallback_knowledge(query)
        
        try:
            # Build query
            query_builder = self.client.table("local_knowledge").select("*")
            
            if category:
                query_builder = query_builder.eq("category", category)
            
            if location:
                query_builder = query_builder.ilike("location", f"%{location}%")
            
            # Search in content
            query_builder = query_builder.ilike("content", f"%{query}%")
            query_builder = query_builder.limit(limit)
            
            result = query_builder.execute()
            
            if result.data:
                return result.data
            else:
                return self._get_fallback_knowledge(query)
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            return self._get_fallback_knowledge(query)
    
    async def add_knowledge(self, content: str, category: str, location: str = None) -> bool:
        """Add new knowledge entry."""
        if not self.is_ready:
            logger.warning("Cannot add knowledge - Supabase not connected")
            return False
        
        try:
            data = {
                "content": content,
                "category": category,
                "location": location
            }
            self.client.table("local_knowledge").insert(data).execute()
            logger.info("Knowledge entry added successfully")
            return True
        except Exception as e:
            logger.error(f"Insert error: {e}")
            return False
    
    def _get_fallback_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Return hardcoded knowledge when DB unavailable."""
        fallback = [
            {
                "id": "1",
                "content": "मोबाइल रिचार्ज कैसे करें:\n\n1. PhonePe, Paytm, या Google Pay ऐप खोलें\n2. 'Mobile Recharge' या 'रिचार्ज' विकल्प चुनें\n3. अपना मोबाइल नंबर डालें\n4. प्लान चुनें या राशि डालें\n5. UPI PIN डालकर भुगतान करें\n\nया नजदीकी मोबाइल शॉप पर जाकर रिचार्ज करवाएं।",
                "category": "telecom",
                "location": None
            },
            {
                "id": "2", 
                "content": "आधार कार्ड अपडेट कैसे करें:\n\n1. myaadhaar.uidai.gov.in पर जाएं\n2. 'Update Aadhaar' पर क्लिक करें\n3. आधार नंबर डालें और OTP वेरीफाई करें\n4. जो जानकारी बदलनी है वो चुनें\n5. नई जानकारी भरें\n6. ₹50 फीस का भुगतान करें\n\nया नजदीकी आधार केंद्र जाएं।",
                "category": "government",
                "location": None
            },
            {
                "id": "3",
                "content": "पैन कार्ड कैसे बनवाएं:\n\n1. onlineservices.nsdl.com पर जाएं\n2. 'Apply for New PAN' चुनें\n3. फॉर्म 49A भरें\n4. दस्तावेज अपलोड करें: फोटो, हस्ताक्षर, आधार\n5. ₹110 फीस भरें\n6. 15-20 दिनों में पैन कार्ड मिलेगा\n\nहेल्पलाइन: 020-27218080",
                "category": "government",
                "location": None
            },
            {
                "id": "4",
                "content": "बैंक अकाउंट कैसे खोलें:\n\n1. नजदीकी बैंक शाखा जाएं\n2. जरूरी दस्तावेज: आधार कार्ड, पैन कार्ड, फोटो\n3. अकाउंट खोलने का फॉर्म भरें\n4. न्यूनतम जमा: ₹500-1000\n\nजीरो बैलेंस अकाउंट:\n- प्रधानमंत्री जन धन योजना (PMJDY)\n- आधार + मोबाइल से खुल जाता है",
                "category": "banking",
                "location": None
            },
            {
                "id": "5",
                "content": "UPI Payment कैसे करें:\n\n1. PhonePe/GPay/Paytm ऐप डाउनलोड करें\n2. मोबाइल नंबर वेरीफाई करें\n3. बैंक अकाउंट लिंक करें\n4. UPI PIN सेट करें\n\nपेमेंट करना:\n- QR Code स्कैन करें\n- या UPI ID डालें\n- राशि डालें और PIN से कन्फर्म करें",
                "category": "banking",
                "location": None
            },
            {
                "id": "6",
                "content": "पासपोर्ट कैसे बनवाएं:\n\n1. passportindia.gov.in पर रजिस्टर करें\n2. फॉर्म भरें और अपॉइंटमेंट बुक करें\n3. फीस: सामान्य ₹1,500, तत्काल ₹3,500\n4. PSK पर जाएं - बायोमेट्रिक और डॉक्यूमेंट वेरिफिकेशन\n5. पुलिस वेरिफिकेशन के बाद पासपोर्ट मिलेगा\n\nसमय: 30-45 दिन",
                "category": "government", 
                "location": None
            },
            {
                "id": "7",
                "content": "Driving License कैसे बनवाएं:\n\n1. parivahan.gov.in पर जाएं\n2. Learner License के लिए अप्लाई करें\n3. RTO में टेस्ट दें (₹200-400 फीस)\n4. 30 दिन बाद Permanent License के लिए अप्लाई करें\n5. ड्राइविंग टेस्ट दें\n\nजरूरी: आधार, पता प्रमाण, आयु 18+",
                "category": "transport",
                "location": None
            },
            {
                "id": "8",
                "content": "आयुष्मान भारत कार्ड:\n\n1. mera.pmjay.gov.in पर पात्रता जांचें\n2. CSC सेंटर या सरकारी अस्पताल में आयुष्मान मित्र से मिलें\n3. आधार और राशन कार्ड दिखाएं\n4. e-KYC करें\n\nलाभ: ₹5 लाख तक मुफ्त इलाज\nहेल्पलाइन: 14555",
                "category": "health",
                "location": None
            }
        ]
        
        # Filter by query keywords
        query_lower = query.lower()
        keywords = query_lower.split()
        
        results = []
        for item in fallback:
            content_lower = item["content"].lower()
            if any(keyword in content_lower for keyword in keywords):
                results.append(item)
        
        return results[:3] if results else fallback[:2]
    
    def get_status(self) -> dict:
        """Get the status of the database service."""
        return {
            "available": SUPABASE_AVAILABLE,
            "connected": self.is_ready,
            "mode": "supabase" if self.is_ready else "fallback"
        }


_supabase_instance: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get or create the global SupabaseClient instance."""
    global _supabase_instance
    if _supabase_instance is None:
        _supabase_instance = SupabaseClient()
    return _supabase_instance
