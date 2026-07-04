import httpx
import asyncio
import json

BASE_URL = "http://0.0.0.0:8080"

async def test_ai_chat():
    """اختبار مسار /api/chat"""
    print("--- اختبار مسار /api/chat ---")
    url = f"{BASE_URL}/api/chat"
    payload = {"message": "ما هي أفضل استراتيجية تسويق لمنتج جديد؟"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            print(f"الحالة: {response.status_code}")
            print(f"الرد: {data.get('response')[:100]}...")
            assert data.get('success') is True
            print("✅ اختبار الدردشة بالذكاء الاصطناعي ناجح.")
            
    except httpx.HTTPStatusError as e:
        print(f"❌ فشل اختبار الدردشة بالذكاء الاصطناعي: خطأ في حالة HTTP {e.response.status_code}")
        print(f"الرد: {e.response.text}")
    except Exception as e:
        print(f"❌ فشل اختبار الدردشة بالذكاء الاصطناعي: {e}")

async def test_crm_add_lead():
    """اختبار مسار /api/crm/add_lead"""
    print("\n--- اختبار مسار /api/crm/add_lead ---")
    url = f"{BASE_URL}/api/crm/add_lead"
    payload = {
        "name": "عميل تجريبي",
        "email": "test@example.com",
        "phone": "123456789",
        "source": "API Test"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            print(f"الحالة: {response.status_code}")
            print(f"الرد: {data.get('message')}")
            assert data.get('success') is True
            assert data.get('provider') == 'MockCRM'
            print("✅ اختبار إضافة عميل محتمل إلى CRM ناجح (Mock).")
            
    except httpx.HTTPStatusError as e:
        print(f"❌ فشل اختبار إضافة عميل محتمل إلى CRM: خطأ في حالة HTTP {e.response.status_code}")
        print(f"الرد: {e.response.text}")
    except Exception as e:
        print(f"❌ فشل اختبار إضافة عميل محتمل إلى CRM: {e}")

async def test_generate_ad_copy():
    """اختبار مسار /api/ads/generate"""
    print("\n--- اختبار مسار /api/ads/generate ---")
    url = f"{BASE_URL}/api/ads/generate"
    payload = {
        "product_name": "Brilliox AI",
        "target_audience": "أصحاب الأعمال الصغيرة والمسوقين",
        "product_description": "مساعد تسويق بالذكاء الاصطناعي لتبسيط الحملات الإعلانية.",
        "num_copies": 3
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            print(f"الحالة: {response.status_code}")
            print(f"العنوان: {data.get('ad_copy', {}).get('headline')}")
            assert data.get('success') is True
            assert 'ad_copy' in data
            assert 'headline' in data['ad_copy']
            print("✅ اختبار إنشاء محتوى إعلاني ناجح.")
            
    except httpx.HTTPStatusError as e:
        print(f"❌ فشل اختبار إنشاء محتوى إعلاني: خطأ في حالة HTTP {e.response.status_code}")
        print(f"الرد: {e.response.text}")
    except Exception as e:
        print(f"❌ فشل اختبار إنشاء محتوى إعلاني: {e}")

async def test_analyze_lead_quality():
    """اختبار مسار /api/leads/analyze"""
    print("\n--- اختبار مسار /api/leads/analyze ---")
    url = f"{BASE_URL}/api/leads/analyze"
    payload = {
        "lead_data": {
            "name": "سارة علي",
            "company_size": "10-50 موظف",
            "industry": "التجارة الإلكترونية",
            "recent_activity": "زارت صفحة التسعير مرتين"
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            print(f"الحالة: {response.status_code}")
            print(f"التقييم: {data.get('analysis', {}).get('quality_score')}")
            assert data.get('success') is True
            assert 'analysis' in data
            assert 'quality_score' in data['analysis']
            print("✅ اختبار تحليل جودة العميل المحتمل ناجح.")
            
    except httpx.HTTPStatusError as e:
        print(f"❌ فشل اختبار تحليل جودة العميل المحتمل: خطأ في حالة HTTP {e.response.status_code}")
        print(f"الرد: {e.response.text}")
    except Exception as e:
        print(f"❌ فشل اختبار تحليل جودة العميل المحتمل: {e}")

async def main():
    await test_ai_chat()
    await test_crm_add_lead()
    await test_generate_ad_copy()
    await test_analyze_lead_quality()

if __name__ == "__main__":
    asyncio.run(main())
