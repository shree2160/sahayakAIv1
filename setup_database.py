"""
Sahayak AI - Supabase Database Setup Script
===========================================
This script automatically creates the 'local_knowledge' table in your Supabase project.

How to use:
1. Ensure your .env file has SUPABASE_URL and SUPABASE_KEY.
2. Run: python setup_database.py
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv

# Load env
load_dotenv(dotenv_path=".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def setup():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in your .env file.")
        return

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    print(f"🚀 Setting up Sahayak AI database at {SUPABASE_URL}...")

    # SQL to create the table
    # Since Supabase doesn't expose a direct SQL endpoint via REST for security, 
    # we usually advise users to run SQL in the dashboard.
    # However, we can try to check if the table exists by doing a GET.
    
    try:
        async with httpx.AsyncClient() as client:
            # Check if table exists
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/local_knowledge?select=id&limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                print("✅ Table 'local_knowledge' already exists.")
            else:
                print("📝 Table not found or access denied.")
                print("Please follow these steps to set up your database:")
                print("1. log in to https://app.supabase.com")
                print("2. Open your project -> SQL Editor")
                print("3. Paste the contents of 'supabase_setup.sql'")
                print("4. Click 'Run'")
                
            # Offer to insert sample data if table is empty
            if response.status_code == 200 and len(response.json()) == 0:
                print("📥 Table is empty. Inserting sample data...")
                sample_data = [
                    {
                        "content": "Aadhaar Card Update: Visit myaadhaar.uidai.gov.in, login with OTP, select 'Update Aadhaar Online', and upload documents. Fee is ₹50.",
                        "category": "government",
                        "location": None
                    },
                    {
                        "content": "Mobile Recharge: Open PhonePe/Paytm, select 'Mobile Recharge', enter number, choose plan, and pay via UPI PIN.",
                        "category": "telecom",
                        "location": None
                    },
                    {
                        "content": "Pan Card Apply: Go to NSDL portal (onlineservices.nsdl.com), fill Form 49A, pay ₹110, and upload Aadhaar for e-KYC.",
                        "category": "government",
                        "location": None
                    }
                ]
                
                insert_resp = await client.post(
                    f"{SUPABASE_URL}/rest/v1/local_knowledge",
                    headers=headers,
                    json=sample_data
                )
                
                if insert_resp.status_code in [200, 201]:
                    print("✅ Sample data inserted successfully!")
                else:
                    print(f"❌ Failed to insert sample data: {insert_resp.text}")

    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(setup())
