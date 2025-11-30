from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import requests
import re
import time
from datetime import datetime
from supabase import create_client
from pydantic import BaseModel

app = FastAPI(title="Hunter Pro System", version="1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# اتصال قاعدة البيانات
DB_STATUS = False
TABLES_EXIST = False
supabase = None

try:
    supabase = create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_KEY")
    )
    DB_STATUS = True
    
    # اختبار إذا الجداول موجودة
    try:
        supabase.table("users").select("count", count="exact").limit(1).execute()
        TABLES_EXIST = True
        print("✅ Connected to Supabase - Tables Ready!")
    except:
        TABLES_EXIST = False
        print("⚠️ Connected to Supabase - But tables missing")
        
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# نماذج البيانات
class HuntRequest(BaseModel):
    intent_sentence: str
    city: str
    user_id: str = "admin"

class LoginRequest(BaseModel):
    username: str
    password: str

# نظام البحث
SERPER_KEYS = os.environ.get("SERPER_KEYS", "").split(",")
key_index = 0

def get_active_key():
    global key_index
    if not SERPER_KEYS: return None
    key = SERPER_KEYS[key_index]
    key_index = (key_index + 1) % len(SERPER_KEYS)
    return key

def analyze_quality(text):
    text = text.lower()
    
    blacklist = ["للبيع", "for sale", "متاح الان", "احجز الان", "سمسار", "وسيط"]
    for word in blacklist:
        if word in text:
            return "رفض"

    whitelist = ["مطلوب", "محتاج", "عايز", "أبحث", "شراء", "كاش", "wanted", "buying"]
    for word in whitelist:
        if word in text:
            return "ممتاز 🔥"

    return "جيد ⭐"

def save_lead(phone, keyword, link, quality, user_id):
    if quality == "رفض" or not phone:
        return False
    
    if not TABLES_EXIST:
        print(f"💡 LEAD FOUND (Not Saved): {phone} | {quality}")
        return True
        
    try:
        data = {
            "phone_number": phone,
            "source": f"Hunter: {keyword}",
            "quality": quality,
            "status": "NEW",
            "user_id": user_id
        }
        
        result = supabase.table("leads").upsert(data, on_conflict="phone_number").execute()
        print(f"💎 LEAD SAVED: {phone}")
        return True
    except Exception as e:
        print(f"❌ SAVE ERROR: {e}")
        return False

def run_search(intent: str, city: str, user_id: str):
    if not SERPER_KEYS:
        print("❌ No API keys")
        return
    
    api_key = get_active_key()
    if not api_key:
        return
    
    search_query = f'"{intent}" "{city}" "010"'
    
    payload = json.dumps({
        "q": search_query,
        "num": 10,
        "gl": "eg", 
        "hl": "ar"
    })
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"🔍 Searching: {intent} in {city}")
        response = requests.post("https://google.serper.dev/search", headers=headers, data=payload, timeout=30)
        
        if response.status_code == 200:
            results = response.json().get("organic", [])
            found_count = 0
            
            for res in results:
                content = f"{res.get('title', '')} {res.get('snippet', '')}"
                quality = analyze_quality(content)
                
                if quality != "رفض":
                    phones = re.findall(r'(01[0125][0-9]{8})', content)
                    for phone in phones:
                        if save_lead(phone, intent, res.get('link'), quality, user_id):
                            found_count += 1
            
            print(f"✅ Search Complete: {found_count} leads found")
            
            # حفظ سجل البحث
            if TABLES_EXIST:
                try:
                    log_data = {
                        "user_id": user_id,
                        "search_query": intent,
                        "city": city,
                        "results_count": found_count,
                        "domains_checked": len(results)
                    }
                    supabase.table("hunt_logs").insert(log_data).execute()
                except:
                    pass
                    
        else:
            print(f"❌ API Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Search error: {e}")

# المسارات الأساسية
@app.get("/")
def home():
    return {
        "message": "🚀 Hunter Pro System - Ready!",
        "status": "running",
        "database": "connected" if DB_STATUS else "disconnected",
        "tables": "ready" if TABLES_EXIST else "need setup",
        "version": "1.0",
        "docs": "/docs"
    }

@app.post("/hunt")
async def start_hunt(req: HuntRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_search, req.intent_sentence, req.city, req.user_id)
    
    return {
        "status": "started", 
        "message": f"بدأ البحث عن: {req.intent_sentence} في {req.city}",
        "user": req.user_id,
        "mode": "live" if TABLES_EXIST else "demo - data not saved"
    }

@app.post("/login")
async def login(req: LoginRequest):
    if not TABLES_EXIST:
        # مصادقة افتراضية للاختبار
        if req.username == "admin" and req.password == "admin123":
            return {
                "success": True,
                "user": {"username": "admin", "role": "admin"},
                "note": "Demo mode - tables not setup"
            }
        return {"success": False, "error": "Use admin/admin123 for demo"}
    
    try:
        result = supabase.table("users").select("*").eq("username", req.username).eq("password", req.password).execute()
        
        if result.data and result.data[0]['is_active']:
            user = result.data[0]
            return {
                "success": True,
                "user": {
                    "username": user['username'],
                    "role": user['role']
                }
            }
    except Exception as e:
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    return {"success": False, "error": "Invalid credentials"}

@app.get("/leads")
async def get_leads(user_id: str = "admin"):
    if not TABLES_EXIST:
        return {
            "success": True,
            "leads": [],
            "count": 0,
            "note": "Run SQL script in Supabase to enable database"
        }
    
    try:
        result = supabase.table("leads").select("*").eq("user_id", user_id).limit(50).execute()
        return {
            "success": True,
            "leads": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected" if DB_STATUS else "disconnected",
        "tables": "ready" if TABLES_EXIST else "setup required",
        "timestamp": datetime.now().isoformat(),
        "serper_keys": len(SERPER_KEYS)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
