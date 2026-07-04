"""
Brilliox Marketing AI - Clean Version
نظام تسويق رقمي احترافي بدون كود الصياد
"""
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

# تهيئة التطبيق
app = FastAPI(
    title="Brilliox Marketing AI",
    description="مساعد تسويق رقمي مدعوم بالذكاء الاصطناعي",
    version="5.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ====================== Routes ======================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """الصفحة الرئيسية"""
    return templates.TemplateResponse("mobile_app.html", {"request": request})


@app.get("/mobile", response_class=HTMLResponse)
async def mobile_app(request: Request):
    """تطبيق الموبايل"""
    return templates.TemplateResponse("mobile_app.html", {"request": request})


@app.get("/manifest.json")
async def manifest():
    """PWA Manifest"""
    return FileResponse("static/manifest.json")


@app.get("/sw.js")
async def service_worker():
    """Service Worker"""
    return FileResponse("static/sw.js")


@app.post("/api/chat")
async def chat(request: Request):
    """API للمحادثة مع الذكاء الاصطناعي"""
    try:
        data = await request.json()
        message = data.get('message', '')
        
        # TODO: ربط مع AIMarketingService
        response = {
            'success': True,
            'response': f'شكراً لرسالتك: {message}. سيتم الرد عليك قريباً!',
            'provider': 'demo'
        }
        
        return JSONResponse(response)
        
    except Exception as e:
        return JSONResponse({
            'success': False,
            'error': str(e)
        }, status_code=500)


@app.get("/api/facebook-ads/guide")
async def facebook_ads_guide():
    """دليل إنشاء إعلانات Facebook بدون سجل تجاري"""
    from app.services.facebook_boost_service import FacebookBoostService
    
    service = FacebookBoostService()
    guide = service.get_setup_guide()
    
    return JSONResponse(guide)


@app.post("/api/ads/generate")
async def generate_ad_copy(request: Request):
    """إنشاء محتوى إعلاني"""
    try:
        data = await request.json()
        
        # TODO: ربط مع AIMarketingService
        response = {
            'success': True,
            'ad_copy': {
                'headline': 'عنوان جذاب هنا',
                'primary_text': 'نص أساسي مقنع هنا',
                'description': 'وصف مختصر',
                'cta': 'اطلب الآن'
            }
        }
        
        return JSONResponse(response)
        
    except Exception as e:
        return JSONResponse({
            'success': False,
            'error': str(e)
        }, status_code=500)


@app.get("/api/health")
async def health_check():
    """فحص صحة التطبيق"""
    return {
        'status': 'healthy',
        'version': '5.0.0',
        'features': [
            'Facebook Ads without Business Registration',
            'AI Marketing Consultant',
            'Lead Quality Analysis',
            'Multi-language Support',
            'PWA Mobile App'
        ]
    }


# ====================== Startup ======================

@app.on_event("startup")
async def startup_event():
    """عند بدء التشغيل"""
    print("=" * 60)
    print("🚀 Brilliox Marketing AI - Starting...")
    print("=" * 60)
    print("✅ Clean Code - No Hunter References")
    print("✅ Facebook Ads Solution Ready")
    print("✅ Mobile App PWA Ready")
    print("✅ Multi-platform Support")
    print("=" * 60)
    print("📱 Open: http://localhost:5000")
    print("📱 Mobile App: http://localhost:5000/mobile")
    print("📚 API Docs: http://localhost:5000/docs")
    print("=" * 60)


# ====================== Run ======================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 5000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
