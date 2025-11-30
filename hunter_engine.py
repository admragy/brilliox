import os
import json
import re
import requests
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from supabase import create_client
from langchain_groq import ChatGroq

# --- الإعدادات ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SERPER_KEYS_RAW = os.environ.get("SERPER_KEYS") or os.environ.get("SERPER_API_KEY") or ""
SERPER_KEYS = [k.strip().replace('"', '') for k in SERPER_KEYS_RAW.split(',') if k.strip()]

print(f"--- Brain V36 (Diamond Hunter 💎) --- Quality over Quantity")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    llm = ChatGroq(model="llama3-70b-8192", temperature=0.3, api_key=GROQ_API_KEY)
    print("✅ System Ready!")
except:
    supabase = None
    llm = None

app = FastAPI()

class HuntRequest(BaseModel):
    intent_sentence: str
    city: str
    time_filter: str = "qdr:m"
    user_id: str = "admin"
    mode: str = "general"

class ChatRequest(BaseModel):
    phone_number: str
    message: str

# --- إدارة المفاتيح ---
key_index = 0
def get_active_key():
    global key_index
    if not SERPER_KEYS: return None
    k = SERPER_KEYS[key_index]
    key_index = (key_index + 1) % len(SERPER_KEYS)
    return k

# --- تقسيم المناطق (لزيادة الفرص) ---
def get_sub_locations(city):
    if "القاهرة" in city:
        return ["التجمع", "المعادي", "مدينة نصر", "مصر الجديدة", "الزمالك", "الرحاب", "مدينتي"]
    if "الجيزة" in city:
        return ["أكتوبر", "الشيخ زايد", "الهرم", "المهندسين", "الدقي"]
    try:
        return [city] 
    except: return [city]

# --- 🛡️ القاضي الصارم (Strict Judge) ---
def analyze_quality(text):
    text = text.lower()
    
    # 1. قائمة المحظورات (المنافسين والسماسرة)
    # لو لقينا أي كلمة من دول، الرقم ده "سام" ولازم يترمي
    blacklist = ["للبيع", "for sale", "متاح الان", "احجز الان", "تواصل معنا", "امتلك", "فرصة", "offer", "discount"]
    for word in blacklist:
        if word in text:
            return "TRASH" # ارمي في الزبالة

    # 2. قائمة الرغبات (الزبون اللقطة)
    # لازم نلاقي كلمة من دول عشان نقبله
    whitelist = ["مطلوب", "محتاج", "عايز", "أبحث", "شراء", "كاش", "wanted", "buying", "looking for", "need"]
    for word in whitelist:
        if word in text:
            return "Excellent 🔥"

    # 3. المنطقة الرمادية (ممكن يكون مهتم بس مش كاتب صريح)
    # بنقبله بس بياخد تقييم أقل
    neutral = ["سعر", "تفاصيل", "price", "details", "بكام"]
    for word in neutral:
        if word in text:
            return "Very Good ⭐"
            
    # لو مفيش ولا ده ولا ده، يبقى غالباً رقم مش مفيد
    return "TRASH" 

# --- الحفظ ---
def save_lead(phone, email, keyword, link, quality, user_id):
    # الفلتر النهائي: لو الجودة زبالة، متسجلوش أصلاً
    if quality == "TRASH": 
        print(f"   🗑️ Trash Skipped: {phone}")
        return False
        
    data = {
        "source": f"SmartHunt: {keyword}",
        "status": "NEW",
        "notes": f"Link: {link}",
        "quality": quality,
        "user_id": user_id
    }
    
    if phone:
        data["phone_number"] = phone
        if email: data["email"] = email
        try:
            supabase.table("leads").upsert(data, on_conflict="phone_number").execute()
            print(f"   💎 DIAMOND SAVED: {phone} ({quality})")
            return True
        except: pass
    return False

# --- المحرك الرئيسي ---
def run_hydra_process(intent: str, main_city: str, time_filter: str, user_id: str, mode: str):
    if not SERPER_KEYS: return
    
    # بنحول جملة العميل للغة الطلب (عشان نجيب اللي عايز يشتري)
    search_intent = intent
    if "شقة" in intent and "مطلوب" not in intent:
        search_intent = f'مطلوب {intent}' # إجبار كلمة مطلوب

    sub_cities = get_sub_locations(main_city)
    print(f"🌍 Quality Hunting for: {search_intent} in {sub_cities}")
    
    total_found = 0

    for area in sub_cities:
        # معادلات بحث مركزة على "الطلب"
        queries = [
            f'site:facebook.com "{search_intent}" "{area}" "010"',
            f'site:olx.com.eg "{search_intent}" "{area}" "010"',
            f'"{search_intent}" "{area}" "010" -site:youtube.com'
        ]
        
        for q in queries:
            api_key = get_active_key()
            if not api_key: break
            
            # بنطلب 100 نتيجة، بس هننقي منهم بالملقاط
            payload = json.dumps({"q": q, "num": 100, "tbs": time_filter, "gl": "eg", "hl": "ar"})
            headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
            
            try:
                print(f"🚀 Scanning: {q}")
                response = requests.post("https://google.serper.dev/search", headers=headers, data=payload)
                results = response.json().get("organic", [])
                
                for res in results:
                    snippet = str(res.get('title', '')) + " " + str(res.get('snippet', ''))
                    
                    # 1. تقييم الجودة أولاً
                    quality = analyze_quality(snippet)
                    
                    # 2. لو الجودة تمام، نستخرج الرقم
                    if quality != "TRASH":
                        phones = re.findall(r'(01[0125][0-9 \-]{8,15})', snippet)
                        for raw in phones:
                            clean = raw.replace(" ", "").replace("-", "")
                            if len(clean) == 11:
                                if save_lead(clean, None, intent, res.get('link'), quality, user_id):
                                    total_found += 1
                                    
            except Exception as e:
                print(f"   ⚠️ Error: {e}")

    print(f"🏁 Quality Hunt Finished. Total Diamonds: {total_found}")

# --- Endpoints ---
@app.get("/")
def home(): return {"status": "Brain V36 Quality First"}

@app.post("/start_hunt")
async def start_hunt(req: HuntRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_hydra_process, req.intent_sentence, req.city, req.time_filter, req.user_id, req.mode)
    return {"status": "Started"}

@app.post("/analyze_intent")
async def analyze_intent(req: ChatRequest): return {"action": "PROCEED", "intent": "INTERESTED"}

@app.post("/chat")
async def chat(req: ChatRequest):
    return {"response": "اهلا"}
    
