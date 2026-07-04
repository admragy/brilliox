"""
AI Marketing Consultant Service - خدمة الذكاء الاصطناعي للاستشارات التسويقية
بدون أي إشارة لمصطلح "Hunter" أو "الصياد"
"""
import os
import time
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import google.generativeai as genai
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False


class AIMarketingService:
    """خدمة الذكاء الاصطناعي للاستشارات التسويقية الاحترافية"""
    
    # Prompt نظيف ومهني بدون مصطلحات "الصياد"
    SYSTEM_PROMPT = """أنت مستشار تسويق رقمي محترف وخبير في:

1. **التسويق الرقمي:**
   - إنشاء حملات إعلانية فعّالة (Facebook, Instagram, Google, TikTok)
   - تحليل الجمهور المستهدف (Target Audience Analysis)
   - بناء استراتيجيات التسويق بالمحتوى
   - تحسين معدلات التحويل (Conversion Rate Optimization)

2. **التجارة الإلكترونية:**
   - استراتيجيات زيادة المبيعات
   - تحسين تجربة المستخدم (UX/UI)
   - بناء قوائم العملاء المحتملين (Lead Generation)
   - إدارة علاقات العملاء (CRM)

3. **الإعلانات الممولة:**
   - Facebook & Instagram Ads
   - Google Ads & YouTube
   - TikTok & Snapchat Ads
   - LinkedIn B2B Marketing

4. **تحليل البيانات:**
   - تحليل أداء الحملات الإعلانية
   - تفسير المقاييس (KPIs, ROI, ROAS)
   - توصيات التحسين المستمر

**أسلوب الرد:**
- ردود احترافية، واضحة، ومباشرة
- أمثلة عملية وقابلة للتطبيق
- نصائح مبنية على أحدث اتجاهات التسويق
- دعم كامل للغة العربية والإنجليزية

**القيود الأخلاقية:**
- لا تقدم نصائح عن أساليب احتيالية أو غير أخلاقية
- احترام خصوصية المستخدمين
- الالتزام بسياسات المنصات الإعلانية
- تشجيع الممارسات التسويقية الشفافة والصادقة
"""

    AD_GENERATION_PROMPT = """أنت خبير في إنشاء محتوى إعلاني احترافي وجذاب.

**مهمتك:**
إنشاء نصوص إعلانية (Ad Copy) مُحسّنة لزيادة معدلات النقر والتحويل.

**تخصصاتك:**
1. **عناوين جذابة (Headlines):** قصيرة، قوية، تجذب الانتباه خلال 3 ثوانٍ
2. **نصوص أساسية (Primary Text):** واضحة، مقنعة، تحل مشكلة حقيقية
3. **Call-to-Action:** واضح ومحفز (اطلب الآن، سجّل مجاناً، احصل على عرض)
4. **الأوصاف (Descriptions):** مختصرة، تركز على الفائدة للعميل

**صيغ الإعلانات:**
- **AIDA:** Attention → Interest → Desire → Action
- **PAS:** Problem → Agitate → Solution
- **BAB:** Before → After → Bridge
- **الفائدة أولاً:** ابدأ بالفائدة، ثم الميزات

**نبرة الصوت:**
- احترافية لكن ودودة
- مباشرة وواضحة
- عاطفية عند الحاجة (خاصة B2C)
- عملية ومهنية (خاصة B2B)

**قواعد ذهبية:**
✅ ركز على فوائد العميل، ليس ميزات المنتج
✅ استخدم أرقام محددة (50% خصم، 1000+ عميل راضٍ)
✅ خلق شعور بالاستعجال (عرض محدود، متبقي 3 أيام)
✅ اذكر Social Proof (تقييمات، شهادات عملاء)
❌ تجنب المبالغة (100% مضمون، معجزة)
❌ تجنب الكلمات المحظورة (مجاني تماماً، اربح المال بسهولة)
"""

    LEAD_ANALYSIS_PROMPT = """أنت محلل بيانات تسويقية خبير في تقييم جودة العملاء المحتملين.

**مهمتك:**
تحليل بيانات العملاء المحتملين (Leads) وتصنيفهم حسب احتمالية الشراء.

**معايير التقييم:**
1. **البيانات المتوفرة:**
   - كاملة (اسم + رقم + بريد) = عالي الجودة
   - ناقصة (رقم فقط) = متوسط
   - مشكوك فيها = منخفض

2. **مصدر العميل (Lead Source):**
   - إعلان ممول مستهدف = جودة عالية
   - محرك بحث عضوي = جودة عالية
   - شبكات التواصل عضوي = متوسط
   - مصادر غير معروفة = منخفض

3. **السلوك (Behavior):**
   - تفاعل مباشر (رسالة، مكالمة) = جودة عالية
   - زيارة متعددة للموقع = جودة جيدة
   - نقرة واحدة فقط = جودة منخفضة

4. **التوقيت:**
   - استجابة سريعة (خلال ساعات) = hot lead
   - بعد أيام = warm lead
   - بعد أسابيع = cold lead

**التوصيات:**
- Hot Leads → تواصل فوري (خلال 5 دقائق)
- Warm Leads → متابعة خلال 24 ساعة
- Cold Leads → حملة تسخين (Nurturing Campaign)

**مخرجات التحليل:**
- تقييم الجودة: ⭐⭐⭐⭐⭐ (1-5 نجوم)
- احتمالية التحويل: نسبة مئوية (0-100%)
- الإجراء الموصى به: اتصال فوري / بريد إلكتروني / واتساب
- التوقيت المثالي للمتابعة
"""

    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.google_key = os.getenv('GOOGLE_API_KEY')
        
        # تهيئة الخدمات
        if self.openai_key and HAS_OPENAI:
            openai.api_key = self.openai_key
            self.provider = 'openai'
            self.model = 'gpt-4-turbo-preview'
        elif self.google_key and HAS_GOOGLE:
            genai.configure(api_key=self.google_key)
            self.provider = 'google'
            self.model = 'gemini-pro'
        else:
            self.provider = None
            logger.warning("لا توجد مفاتيح AI متاحة")
        
        # Cache للردود
        self._cache = {}
        self._cache_ttl = 3600  # ساعة واحدة
    
    async def chat(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        محادثة مع الذكاء الاصطناعي للاستشارات التسويقية
        
        Args:
            message: رسالة المستخدم
            context: سياق إضافي (تاريخ المحادثة، بيانات المستخدم، إلخ)
        
        Returns:
            {
                'response': 'رد الذكاء الاصطناعي',
                'suggestions': ['اقتراح 1', 'اقتراح 2'],
                'tokens_used': 1234,
                'provider': 'openai'
            }
        """
        if not self.provider:
            return {
                'response': 'عذراً، خدمة الذكاء الاصطناعي غير متاحة حالياً. يرجى إضافة OPENAI_API_KEY أو GOOGLE_API_KEY.',
                'error': True
            }
        
        try:
            # فحص الـ Cache
            cache_key = self._get_cache_key(message, context)
            if cache_key in self._cache:
                cached = self._cache[cache_key]
                if time.time() - cached['timestamp'] < self._cache_ttl:
                    return cached['data']
            
            # إنشاء الرد
            if self.provider == 'openai':
                result = await self._chat_openai(message, context)
            else:
                result = await self._chat_google(message, context)
            
            # حفظ في Cache
            self._cache[cache_key] = {
                'timestamp': time.time(),
                'data': result
            }
            
            return result
            
        except Exception as e:
            logger.error(f"AI Chat Error: {e}")
            return {
                'response': f'عذراً، حدث خطأ: {str(e)}',
                'error': True
            }
    
    async def _chat_openai(self, message: str, context: Optional[Dict]) -> Dict:
        """محادثة باستخدام OpenAI GPT"""
        messages = [
            {'role': 'system', 'content': self.SYSTEM_PROMPT}
        ]
        
        # إضافة السياق
        if context and context.get('history'):
            for msg in context['history'][-5:]:  # آخر 5 رسائل
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        messages.append({'role': 'user', 'content': message})
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        return {
            'response': response.choices[0].message.content,
            'tokens_used': response.usage.total_tokens,
            'provider': 'openai',
            'model': self.model
        }
    
    async def _chat_google(self, message: str, context: Optional[Dict]) -> Dict:
        """محادثة باستخدام Google Gemini"""
        model = genai.GenerativeModel(self.model)
        
        # بناء الـ Prompt
        full_prompt = f"{self.SYSTEM_PROMPT}\n\nالسؤال: {message}"
        
        if context and context.get('history'):
            history_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in context['history'][-3:]
            ])
            full_prompt += f"\n\nالسياق السابق:\n{history_text}"
        
        response = model.generate_content(full_prompt)
        
        return {
            'response': response.text,
            'tokens_used': len(response.text.split()),  # تقدير تقريبي
            'provider': 'google',
            'model': self.model
        }
    
    async def generate_ad_copy(self, product_info: Dict) -> Dict[str, Any]:
        """
        إنشاء محتوى إعلاني احترافي
        
        Args:
            product_info: {
                'product_name': 'اسم المنتج',
                'description': 'وصف المنتج',
                'target_audience': 'الجمهور المستهدف',
                'unique_selling_point': 'ميزة تنافسية',
                'call_to_action': 'اطلب الآن',
                'platform': 'facebook'  # facebook, instagram, google
            }
        
        Returns:
            {
                'headline': 'العنوان',
                'primary_text': 'النص الأساسي',
                'description': 'الوصف',
                'cta': 'Call-to-Action',
                'variations': [...]  # 3 نسخ بديلة
            }
        """
        prompt = f"""
أنشئ محتوى إعلاني احترافي لـ:

**المنتج/الخدمة:** {product_info.get('product_name')}
**الوصف:** {product_info.get('description')}
**الجمهور المستهدف:** {product_info.get('target_audience')}
**الميزة التنافسية:** {product_info.get('unique_selling_point')}
**المنصة:** {product_info.get('platform', 'facebook')}

**المطلوب:**
1. عنوان جذاب (Headline) - 40 حرف كحد أقصى
2. نص أساسي (Primary Text) - 125 حرف
3. وصف (Description) - 30 حرف
4. Call-to-Action مناسب

**أنشئ 3 نسخ مختلفة** باستخدام:
- النسخة 1: أسلوب AIDA
- النسخة 2: أسلوب PAS
- النسخة 3: التركيز على الفائدة

صيغة الرد: JSON
"""
        
        result = await self.chat(prompt)
        
        # TODO: تحليل الرد وإرجاع JSON منظم
        return {
            'raw_response': result.get('response'),
            'provider': result.get('provider')
        }
    
    async def analyze_lead_quality(self, lead_data: Dict) -> Dict[str, Any]:
        """
        تحليل جودة عميل محتمل
        
        Args:
            lead_data: {
                'name': 'الاسم',
                'phone': 'رقم الهاتف',
                'email': 'البريد الإلكتروني',
                'source': 'مصدر العميل',
                'interaction_history': [],
                'timestamp': 'وقت التسجيل'
            }
        
        Returns:
            {
                'quality_score': 4.5,  # من 5
                'conversion_probability': 75,  # نسبة مئوية
                'category': 'hot_lead',  # hot/warm/cold
                'recommended_action': 'اتصال فوري',
                'best_contact_time': '10:00 AM - 12:00 PM'
            }
        """
        # حساب النقاط
        score = 0
        max_score = 5
        
        # 1. اكتمال البيانات (2 نقطة)
        if lead_data.get('name') and lead_data.get('phone'):
            score += 1
        if lead_data.get('email'):
            score += 1
        
        # 2. مصدر العميل (2 نقطة)
        source = lead_data.get('source', '').lower()
        if 'paid' in source or 'ad' in source:
            score += 2
        elif 'organic' in source or 'search' in source:
            score += 1.5
        elif 'social' in source:
            score += 1
        
        # 3. التفاعل (1 نقطة)
        if lead_data.get('interaction_history'):
            score += min(len(lead_data['interaction_history']) * 0.3, 1)
        
        # تصنيف
        if score >= 4:
            category = 'hot_lead'
            action = '🔥 اتصال فوري خلال 5 دقائق'
        elif score >= 2.5:
            category = 'warm_lead'
            action = '⚡ متابعة خلال 24 ساعة'
        else:
            category = 'cold_lead'
            action = '📧 إرسال بريد إلكتروني ترحيبي'
        
        return {
            'quality_score': round(score, 1),
            'max_score': max_score,
            'conversion_probability': int((score / max_score) * 100),
            'category': category,
            'recommended_action': action,
            'best_contact_time': '10:00 صباحاً - 12:00 ظهراً',
            'notes': self._get_lead_notes(lead_data, score)
        }
    
    def _get_lead_notes(self, lead: Dict, score: float) -> List[str]:
        """ملاحظات وتوصيات للعميل المحتمل"""
        notes = []
        
        if not lead.get('email'):
            notes.append('⚠️ البريد الإلكتروني مفقود - اطلبه في أول تواصل')
        
        if score < 2:
            notes.append('💡 نوصي بحملة تسخين (Email Nurturing) قبل البيع المباشر')
        
        if not lead.get('interaction_history'):
            notes.append('📞 أول تواصل - كن ودوداً واستمع أكثر')
        
        return notes
    
    def _get_cache_key(self, message: str, context: Optional[Dict]) -> str:
        """إنشاء مفتاح الـ Cache"""
        import hashlib
        
        key_data = message
        if context:
            key_data += str(context.get('user_id', ''))
        
        return hashlib.md5(key_data.encode()).hexdigest()


# مثال استخدام
if __name__ == '__main__':
    service = AIMarketingService()
    print("✅ خدمة الذكاء الاصطناعي للتسويق جاهزة (بدون كود الصياد)")
