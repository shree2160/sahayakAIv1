-- =============================================================================
-- Sahayak AI - Supabase Database Setup
-- =============================================================================
-- Run this SQL in your Supabase SQL Editor to create the required tables
-- and insert sample data for local knowledge.
--
-- Steps:
-- 1. Go to your Supabase project dashboard
-- 2. Navigate to SQL Editor
-- 3. Paste this entire file
-- 4. Click "Run"
-- =============================================================================

-- Enable vector extension for embeddings (if not already enabled)
-- Note: This is available in Supabase by default
CREATE EXTENSION IF NOT EXISTS vector;

-- =============================================================================
-- TABLE: local_knowledge
-- Stores local procedures, guides, and information for Indian users
-- =============================================================================

CREATE TABLE IF NOT EXISTS local_knowledge (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    location TEXT,  -- City/State where this applies (NULL = all India)
    category TEXT NOT NULL DEFAULT 'other',
    embedding VECTOR(768),  -- For semantic search (optional)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster category searches
CREATE INDEX IF NOT EXISTS idx_local_knowledge_category ON local_knowledge(category);

-- Create index for location-based searches
CREATE INDEX IF NOT EXISTS idx_local_knowledge_location ON local_knowledge(location);

-- Create index for full-text search
CREATE INDEX IF NOT EXISTS idx_local_knowledge_content ON local_knowledge USING gin(to_tsvector('simple', content));

-- =============================================================================
-- SAMPLE DATA: Common procedures and information
-- =============================================================================

-- Telecom / Mobile Recharge
INSERT INTO local_knowledge (content, category, location) VALUES
(
    'मोबाइल रिचार्ज कैसे करें (Mobile Recharge):

    विधि 1: UPI Apps (PhonePe, Google Pay, Paytm)
    1. ऐप खोलें और लॉगिन करें
    2. "Mobile Recharge" या "रिचार्ज" विकल्प चुनें
    3. अपना मोबाइल नंबर डालें
    4. ऑपरेटर अपने आप पता चल जाएगा
    5. अपना प्लान चुनें या राशि डालें
    6. UPI PIN डालकर भुगतान करें
    
    विधि 2: ऑपरेटर ऐप (Jio, Airtel, Vi)
    1. अपने ऑपरेटर का ऐप डाउनलोड करें
    2. अपना नंबर से लॉगिन करें
    3. प्लान चुनें और भुगतान करें
    
    विधि 3: रिचार्ज दुकान
    - नजदीकी मोबाइल शॉप पर जाएं
    - नंबर और राशि बताएं
    - नकद या UPI से भुगतान करें',
    'telecom',
    NULL
),
(
    'Jio Recharge Plans (जियो रिचार्ज):
    
    लोकप्रिय प्लान:
    • ₹149 - 24 दिन, 1GB/day, अनलिमिटेड कॉल
    • ₹199 - 28 दिन, 1.5GB/day, अनलिमिटेड कॉल
    • ₹239 - 28 दिन, 1.5GB/day + जियो ऐप्स
    • ₹299 - 28 दिन, 2GB/day, अनलिमिटेड कॉल
    • ₹666 - 84 दिन, 1.5GB/day
    • ₹999 - 84 दिन, 2.5GB/day
    
    Jio App या MyJio वेबसाइट पर जाकर रिचार्ज करें।
    हेल्पलाइन: 198 या 1800-889-9999',
    'telecom',
    NULL
);

-- Government Services
INSERT INTO local_knowledge (content, category, location) VALUES
(
    'आधार कार्ड अपडेट कैसे करें (Aadhaar Update):

    ऑनलाइन अपडेट (myaadhaar.uidai.gov.in):
    1. myaadhaar.uidai.gov.in पर जाएं
    2. "Update Aadhaar" पर क्लिक करें
    3. आधार नंबर डालें और OTP वेरीफाई करें
    4. जो जानकारी बदलनी है वो चुनें
    5. नई जानकारी भरें और डॉक्यूमेंट अपलोड करें
    6. ₹50 फीस का भुगतान करें
    7. URN नंबर सेव करें
    
    ऑफलाइन अपडेट (आधार केंद्र):
    1. नजदीकी आधार केंद्र खोजें (uidai.gov.in)
    2. अपॉइंटमेंट लें (वैकल्पिक)
    3. मूल दस्तावेज लेकर जाएं
    4. फॉर्म भरें और बायोमेट्रिक दें
    5. रसीद लें (अपडेट 90 दिनों में होगा)
    
    जरूरी दस्तावेज: पता प्रमाण, पहचान प्रमाण',
    'government',
    NULL
),
(
    'पैन कार्ड बनवाना (PAN Card Apply):

    ऑनलाइन आवेदन:
    1. onlineservices.nsdl.com या utiitsl.com पर जाएं
    2. "Apply for New PAN" चुनें
    3. फॉर्म 49A भरें (भारतीय नागरिक)
    4. दस्तावेज अपलोड करें:
       - फोटो (JPEG, 2MB तक)
       - हस्ताक्षर (JPEG, 2MB तक)
       - पहचान प्रमाण (आधार/पासपोर्ट)
       - पता प्रमाण
       - जन्म तिथि प्रमाण
    5. ₹110 + GST फीस का भुगतान करें
    6. एक्नॉलेजमेंट नंबर सेव करें
    7. 15-20 दिनों में पैन कार्ड मिलेगा
    
    e-PAN तुरंत मिल जाता है डाउनलोड के लिए।
    हेल्पलाइन: 020-27218080',
    'government',
    NULL
),
(
    'पासपोर्ट बनवाना (Passport Apply):

    ऑनलाइन आवेदन (passportindia.gov.in):
    1. पासपोर्ट सेवा पोर्टल पर रजिस्टर करें
    2. फॉर्म भरें और सबमिट करें
    3. अपॉइंटमेंट बुक करें (PSK/POPSK)
    4. फीस भरें:
       - सामान्य (36 पेज): ₹1,500
       - तत्काल: ₹3,500
    
    PSK पर जाएं:
    - ओरिजिनल दस्तावेज लेकर जाएं
    - बायोमेट्रिक और फोटो होगा
    - पुलिस वेरिफिकेशन होगा
    
    जरूरी दस्तावेज:
    - आधार कार्ड
    - जन्म प्रमाण पत्र
    - पता प्रमाण
    - फोटो (हाल की, सफेद बैकग्राउंड)
    
    समय: सामान्य 30-45 दिन, तत्काल 7-14 दिन',
    'government',
    NULL
),
(
    'वोटर ID कैसे बनवाएं (Voter ID Card):

    ऑनलाइन आवेदन (voters.eci.gov.in):
    1. National Voter Service Portal पर जाएं
    2. "New Voter Registration" चुनें
    3. Form 6 भरें
    4. फोटो और दस्तावेज अपलोड करें
    5. सबमिट करें और Reference ID सेव करें
    
    ऑफलाइन आवेदन:
    1. नजदीकी BLO (Booth Level Officer) से मिलें
    2. Form 6 लें और भरें
    3. दस्तावेज की कॉपी लगाएं
    4. जमा करें
    
    जरूरी दस्तावेज:
    - आधार कार्ड
    - पासपोर्ट साइज फोटो
    - पता प्रमाण
    - आयु प्रमाण (18+ होना चाहिए)
    
    प्रोसेसिंग समय: 15-30 दिन
    हेल्पलाइन: 1950',
    'government',
    NULL
);

-- Banking
INSERT INTO local_knowledge (content, category, location) VALUES
(
    'बैंक अकाउंट कैसे खोलें (Bank Account Opening):

    जरूरी दस्तावेज:
    - आधार कार्ड (अनिवार्य)
    - पैन कार्ड (₹50,000+ के लिए)
    - पासपोर्ट साइज फोटो (2)
    - पता प्रमाण
    - मोबाइल नंबर
    
    प्रक्रिया:
    1. नजदीकी बैंक शाखा जाएं
    2. अकाउंट खोलने का फॉर्म लें
    3. फॉर्म भरें और दस्तावेज लगाएं
    4. न्यूनतम जमा राशि दें:
       - Savings: ₹500-1000
       - Zero Balance: ₹0 (PMJDY)
    5. 7 दिनों में पासबुक और ATM कार्ड मिलेगा
    
    जीरो बैलेंस अकाउंट:
    - प्रधानमंत्री जन धन योजना (PMJDY)
    - आधार + मोबाइल से खुल जाता है
    - ₹1 लाख एक्सीडेंट बीमा मुफ्त',
    'banking',
    NULL
),
(
    'UPI Payment कैसे करें:

    UPI सेटअप (PhonePe/GPay/Paytm):
    1. ऐप डाउनलोड करें
    2. मोबाइल नंबर वेरीफाई करें
    3. बैंक अकाउंट लिंक करें
    4. UPI PIN सेट करें
    
    पेमेंट करना:
    विधि 1: QR Code स्कैन
    - "Scan" पर टैप करें
    - दुकान का QR स्कैन करें
    - राशि डालें और PIN डालें
    
    विधि 2: UPI ID से
    - "Pay" पर टैप करें
    - UPI ID डालें (example@upi)
    - राशि और PIN डालें
    
    विधि 3: मोबाइल नंबर से
    - "Pay" पर टैप करें
    - नंबर डालें
    - बैंक चुनें और भुगतान करें
    
    लिमिट: ₹1 लाख/दिन (बैंक के हिसाब से)
    हेल्पलाइन: 1800-120-3721 (NPCI)',
    'banking',
    NULL
);

-- Health
INSERT INTO local_knowledge (content, category, location) VALUES
(
    'आयुष्मान भारत कार्ड (Ayushman Bharat Card):

    पात्रता जांचें:
    1. mera.pmjay.gov.in पर जाएं
    2. राशन कार्ड नंबर या SECC डेटा से चेक करें
    3. अगर नाम है तो कार्ड बनवा सकते हैं
    
    कार्ड बनवाना:
    1. नजदीकी CSC (Common Service Centre) जाएं
    2. या आयुष्मान मित्र से मिलें (सरकारी अस्पताल में)
    3. आधार कार्ड और राशन कार्ड दिखाएं
    4. e-KYC होगा (फिंगरप्रिंट)
    5. कार्ड तुरंत या 15 दिनों में मिलेगा
    
    लाभ:
    - ₹5 लाख तक मुफ्त इलाज
    - सभी सरकारी + कुछ प्राइवेट अस्पताल
    - कैशलेस इलाज
    
    हेल्पलाइन: 14555',
    'health',
    NULL
);

-- Education
INSERT INTO local_knowledge (content, category, location) VALUES
(
    'Scholarship कैसे अप्लाई करें (NSP - National Scholarship Portal):

    1. scholarships.gov.in पर जाएं
    2. "New Registration" करें
    3. आधार नंबर से वेरीफाई करें
    4. लॉगिन करें और स्कॉलरशिप चुनें
    5. फॉर्म भरें:
       - व्यक्तिगत जानकारी
       - शैक्षिक योग्यता
       - बैंक खाता विवरण
       - परिवार की आय
    6. दस्तावेज अपलोड करें
    7. सबमिट और प्रिंट करें
    
    जरूरी दस्तावेज:
    - आधार कार्ड
    - आय प्रमाण पत्र
    - जाति प्रमाण पत्र (अगर लागू हो)
    - पिछली मार्कशीट
    - फोटो
    - बैंक पासबुक
    
    स्कॉलरशिप सीधे बैंक में आती है।',
    'education',
    NULL
);

-- Transport
INSERT INTO local_knowledge (content, category, location) VALUES
(
    'Driving License बनवाना (Driving Licence):

    Learner License (LLR):
    1. parivahan.gov.in पर जाएं
    2. "Apply for Learner License" चुनें
    3. फॉर्म 2 भरें
    4. RTO में स्लॉट बुक करें
    5. फीस भरें (₹200-400)
    6. RTO जाएं - टेस्ट दें (ट्रैफिक नियम)
    7. LLR 6 महीने के लिए वैध होगा
    
    Permanent License (DL):
    1. LLR के 30 दिन बाद अप्लाई करें
    2. parivahan.gov.in पर "Apply for DL"
    3. RTO में स्लॉट बुक करें
    4. ड्राइविंग टेस्ट दें
    5. पास होने पर DL मिलेगा
    
    जरूरी दस्तावेज:
    - आधार कार्ड
    - पता प्रमाण
    - आयु प्रमाण (18+ दोपहिया, 20+ चौपहिया)
    - पासपोर्ट फोटो
    - मेडिकल सर्टिफिकेट (50+ आयु)
    
    हेल्पलाइन: 0120-2459-169',
    'transport',
    NULL
);

-- =============================================================================
-- ROW LEVEL SECURITY (Optional but recommended)
-- =============================================================================

-- Enable RLS
ALTER TABLE local_knowledge ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Allow public read access" ON local_knowledge
    FOR SELECT USING (true);

-- Allow authenticated users to insert (optional)
CREATE POLICY "Allow authenticated insert" ON local_knowledge
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- =============================================================================
-- FUNCTION: Search knowledge by text similarity
-- =============================================================================

CREATE OR REPLACE FUNCTION search_knowledge(
    search_query TEXT,
    category_filter TEXT DEFAULT NULL,
    location_filter TEXT DEFAULT NULL,
    result_limit INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    location TEXT,
    category TEXT,
    similarity REAL
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lk.id,
        lk.content,
        lk.location,
        lk.category,
        ts_rank(to_tsvector('simple', lk.content), plainto_tsquery('simple', search_query)) AS similarity
    FROM local_knowledge lk
    WHERE 
        (category_filter IS NULL OR lk.category = category_filter)
        AND (location_filter IS NULL OR lk.location ILIKE '%' || location_filter || '%' OR lk.location IS NULL)
        AND to_tsvector('simple', lk.content) @@ plainto_tsquery('simple', search_query)
    ORDER BY similarity DESC
    LIMIT result_limit;
END;
$$;

-- =============================================================================
-- DONE! Your database is ready for Sahayak AI
-- =============================================================================
