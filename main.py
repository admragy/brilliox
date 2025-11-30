from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import re
import requests
import json
from datetime import datetime
from supabase import create_client
from pydantic import BaseModel

app = FastAPI(title="Hunter Pro", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

SERPER_KEYS = [k.strip() for k in os.environ.get("SERPER_KEYS", "").split(",") if k.strip()]
key_index = 0

class HuntRequest(BaseModel):
    intent_sentence: str
    city: str
    user_id: str = "admin"

class WhatsAppRequest(BaseModel):
    phone_number: str
    message: str
    user_id: str

def get_key():
    global key_index
    if not SERPER_KEYS: return None
    key = SERPER_KEYS[key_index]
    key_index = (key_index + 1) % len(SERPER_KEYS)
    return key

def analyze_quality(text):
    text = text.lower()
    if any(w in text for w in ["للبيع", "for sale", "سمسار", "broker"]): return "رفض"
    if any(w in text for w in ["مطلوب", "محتاج", "عايز", "wanted"]): return "ممتاز 🔥"
    return "جيد ⭐"

def save_lead(phone, keyword, quality, user_id):
    try:
        supabase.table("leads").upsert({
            "phone_number": phone, "source": f"Hunter: {keyword}",
            "quality": quality, "status": "NEW", "user_id": user_id
        }, on_conflict="phone_number").execute()
        return True
    except: return False

def run_search(intent: str, city: str, user_id: str):
    key = get_key()
    if not key: return
    query = f'"{intent}" "{city}"'
    payload = json.dumps({"q": query, "num": 10, "gl": "eg", "hl": "ar"})
    headers = {"X-API-KEY": key, "Content-Type": "application/json"}
    try:
        res = requests.post("https://google.serper.dev/search", headers=headers, data=payload, timeout=30)
        if res.status_code == 200:
            results = res.json().get("organic", [])
            for r in results:
                content = f"{r.get('title', '')} {r.get('snippet', '')}"
                quality = analyze_quality(content)
                phones = re.findall(r'(01[0125][0-9]{8})', content)
                for phone in phones: save_lead(phone, intent, quality, user_id)
    except: pass

@app.get("/")
def home(): return {"message": "Hunter Pro is running ✅"}

@app.post("/hunt")
async def hunt(req: HuntRequest, bg: BackgroundTasks):
    bg.add_task(run_search, req.intent_sentence, req.city, req.user_id)
    return {"status": "started", "search": req.intent_sentence, "city": req.city}

@app.get("/leads")
def get_leads(user_id: str = "admin"):
    try:
        rows = supabase.table("leads").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return {"success": True, "leads": rows.data}
    except Exception as e:
        return {"success": False, "error": str(e)}
