"""
Facebook Boosted Posts Service - الحل الذكي للإعلانات الممولة بدون سجل تجاري
يستخدم Facebook Graph API مع طريقة Boosted Posts
"""
import requests
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class FacebookBoostService:
    """خدمة إنشاء إعلانات ممولة على Facebook بدون Business Manager"""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def create_post_and_boost(self, page_id: str, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        إنشاء منشور وترويجه مباشرة (Boost)
        
        Args:
            page_id: معرّف الصفحة
            post_data: بيانات المنشور والإعلان
                {
                    'message': 'نص المنشور',
                    'link': 'رابط اختياري',
                    'image_url': 'صورة اختيارية',
                    'budget': 50,  # الميزانية اليومية بالدولار
                    'duration_days': 7,  # مدة الحملة
                    'targeting': {
                        'countries': ['EG', 'SA', 'AE'],
                        'age_min': 18,
                        'age_max': 65,
                        'interests': ['Marketing', 'Business']
                    }
                }
        
        Returns:
            معلومات الإعلان المُنشأ
        """
        try:
            # 1. إنشاء المنشور
            post_id = self._create_page_post(page_id, post_data)
            
            if not post_id:
                return {'success': False, 'error': 'فشل إنشاء المنشور'}
            
            # 2. ترويج المنشور (Boost)
            boost_result = self._boost_post(post_id, post_data)
            
            return {
                'success': True,
                'post_id': post_id,
                'promotion_id': boost_result.get('id'),
                'message': 'تم إنشاء الإعلان الممول بنجاح ✅',
                'estimated_reach': self._estimate_reach(post_data),
                'instructions': self._get_manual_instructions()
            }
            
        except Exception as e:
            logger.error(f"Facebook Boost Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'alternative_methods': self._get_alternative_methods()
            }
    
    def _create_page_post(self, page_id: str, data: Dict) -> Optional[str]:
        """إنشاء منشور على الصفحة"""
        endpoint = f"{self.base_url}/{page_id}/feed"
        
        params = {
            'message': data.get('message', ''),
            'access_token': self.access_token
        }
        
        if data.get('link'):
            params['link'] = data['link']
        
        if data.get('image_url'):
            # رفع الصورة أولاً
            photo_id = self._upload_photo(page_id, data['image_url'])
            if photo_id:
                params['object_attachment'] = photo_id
        
        response = requests.post(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json().get('id')
        
        return None
    
    def _boost_post(self, post_id: str, data: Dict) -> Dict:
        """ترويج المنشور (Boost)"""
        endpoint = f"{self.base_url}/{post_id}/promotions"
        
        targeting = data.get('targeting', {})
        
        params = {
            'access_token': self.access_token,
            'budget_rebalance_flag': True,
            'daily_budget': int(data.get('budget', 10) * 100),  # بالسنت
            'end_time': self._calculate_end_time(data.get('duration_days', 7)),
            'targeting': {
                'geo_locations': {
                    'countries': targeting.get('countries', ['EG'])
                },
                'age_min': targeting.get('age_min', 18),
                'age_max': targeting.get('age_max', 65),
                'interests': [
                    {'name': interest} for interest in targeting.get('interests', [])
                ]
            }
        }
        
        response = requests.post(endpoint, json=params)
        return response.json()
    
    def _upload_photo(self, page_id: str, image_url: str) -> Optional[str]:
        """رفع صورة للصفحة"""
        endpoint = f"{self.base_url}/{page_id}/photos"
        
        params = {
            'url': image_url,
            'access_token': self.access_token,
            'published': False
        }
        
        response = requests.post(endpoint, params=params)
        
        if response.status_code == 200:
            return response.json().get('id')
        
        return None
    
    def _calculate_end_time(self, days: int) -> int:
        """حساب وقت انتهاء الحملة"""
        import time
        return int(time.time()) + (days * 24 * 60 * 60)
    
    def _estimate_reach(self, data: Dict) -> Dict:
        """تقدير الوصول المتوقع"""
        budget = data.get('budget', 10)
        days = data.get('duration_days', 7)
        countries = data.get('targeting', {}).get('countries', ['EG'])
        
        # متوسط CPM (التكلفة لكل 1000 ظهور) حسب الدولة
        cpm_rates = {
            'EG': 1.0,  # مصر
            'SA': 4.0,  # السعودية
            'AE': 5.0,  # الإمارات
            'KW': 3.5,  # الكويت
            'QA': 4.5,  # قطر
        }
        
        avg_cpm = sum(cpm_rates.get(c, 2.0) for c in countries) / len(countries)
        
        total_budget = budget * days
        estimated_impressions = (total_budget / avg_cpm) * 1000
        estimated_clicks = estimated_impressions * 0.02  # CTR 2%
        
        return {
            'total_budget': f'${total_budget}',
            'estimated_impressions': f'{int(estimated_impressions):,}',
            'estimated_clicks': f'{int(estimated_clicks):,}',
            'estimated_ctr': '2%',
            'avg_cpm': f'${avg_cpm}'
        }
    
    def _get_manual_instructions(self) -> Dict:
        """تعليمات الاستخدام اليدوي (البديل الأسهل)"""
        return {
            'الطريقة_1_Boost_Post': {
                'الخطوات': [
                    '1. افتح صفحتك على Facebook',
                    '2. انشر منشوراً عادياً (نص + صورة + رابط)',
                    '3. اضغط زر "Boost Post" (ترويج المنشور) الأزرق',
                    '4. اختر الجمهور: الموقع، العمر، الاهتمامات',
                    '5. حدد الميزانية (10-100$ يومياً)',
                    '6. اختر مدة الإعلان (1-30 يوم)',
                    '7. ادفع بالفيزا/ماستركارد مباشرة',
                    '8. انقر "Boost" وسيُراجع الإعلان خلال 24 ساعة'
                ],
                'المميزات': [
                    '✅ لا يحتاج Business Manager',
                    '✅ لا يحتاج سجل تجاري',
                    '✅ بطاقة بنك عادية كافية',
                    '✅ سهل جداً للمبتدئين'
                ],
                'القيود': [
                    '⚠️ ميزانية يومية أقصاها ~100$',
                    '⚠️ خيارات استهداف أقل تفصيلاً'
                ]
            },
            'الطريقة_2_Instagram_Promote': {
                'الخطوات': [
                    '1. حوّل حسابك لـ Instagram Business',
                    '2. انشر صورة أو ريلز',
                    '3. اضغط "Promote" أسفل المنشور',
                    '4. اختر الهدف: More Profile Visits / More Website Traffic',
                    '5. حدد الجمهور والميزانية',
                    '6. ادفع بالفيزا مباشرة'
                ],
                'المميزات': [
                    '✅ أسهل من Facebook',
                    '✅ لا توثيق إطلاقاً',
                    '✅ جمهور شاب ونشط',
                    '✅ معدلات تفاعل أعلى'
                ],
                'التكلفة': '5$ - 50$ يومياً'
            },
            'الطريقة_3_WhatsApp_Click_to_Chat': {
                'الخطوات': [
                    '1. أنشئ WhatsApp Business API (مجاناً)',
                    '2. اذهب لـ Facebook Ads Manager',
                    '3. اختر "Messages" كهدف',
                    '4. اختر WhatsApp كوجهة',
                    '5. Facebook لن يطلب سجل تجاري لهذا النوع!',
                    '6. الدفع بالفيزا عادي'
                ],
                'المميزات': [
                    '✅ تواصل مباشر مع العملاء',
                    '✅ تحويلات عالية جداً',
                    '✅ مناسب للسوق العربي',
                    '✅ توثيق أقل تعقيداً'
                ],
                'ROI': 'من أعلى معدلات العائد على الاستثمار'
            }
        }
    
    def _get_alternative_methods(self) -> Dict:
        """طرق بديلة للإعلان بدون Facebook"""
        return {
            'google_ads': {
                'المميزات': '✅ لا يحتاج توثيق، فقط بطاقة فيزا',
                'التكلفة': 'أعلى قليلاً من Facebook',
                'الوصول': 'محرك البحث + YouTube + شبكة Google الإعلانية'
            },
            'tiktok_ads': {
                'المميزات': '✅ توثيق بسيط، جمهور شاب',
                'التكلفة': 'منخفضة جداً (أرخص من Facebook)',
                'الوصول': '100 مليون+ مستخدم عربي'
            },
            'snapchat_ads': {
                'المميزات': '✅ شعبية في الخليج والسعودية',
                'التكلفة': 'متوسطة',
                'الوصول': 'قوي جداً في السعودية والإمارات'
            },
            'linkedin_ads': {
                'المميزات': '✅ مثالي لـ B2B والخدمات المهنية',
                'التكلفة': 'أغلى من كل المنصات',
                'الوصول': 'جودة عالية، decision makers'
            }
        }
    
    def get_setup_guide(self) -> Dict:
        """دليل الإعداد الكامل"""
        return {
            'العنوان': '🚀 دليل إنشاء إعلانات Facebook الممولة بدون سجل تجاري',
            'الطريقة_الموصى_بها': {
                'الاسم': 'Facebook Boosted Posts (ترويج المنشورات)',
                'لماذا_هي_الأفضل': [
                    '1. لا تحتاج Business Manager معقد',
                    '2. لا تحتاج سجل تجاري',
                    '3. تتم من صفحتك مباشرة',
                    '4. الدفع بأي بطاقة فيزا/ماستركارد',
                    '5. مناسبة للميزانيات الصغيرة (10$+)'
                ],
                'الخطوات_التفصيلية': {
                    'الخطوة_1_إنشاء_صفحة': [
                        'اذهب لـ facebook.com/pages/create',
                        'اختر نوع الصفحة (Business/Brand)',
                        'املأ المعلومات الأساسية',
                        'ارفع صورة Profile + Cover جذابة'
                    ],
                    'الخطوة_2_إضافة_محتوى': [
                        'انشر 3-5 منشورات عادية أولاً',
                        'أضف صور عالية الجودة',
                        'اكتب وصف قوي وواضح',
                        'أضف Call-to-Action (تواصل معنا، اشتري الآن، إلخ)'
                    ],
                    'الخطوة_3_Boost': [
                        'انقر "Boost Post" على أي منشور',
                        'اختر هدف الإعلان (Traffic, Messages, Engagement)',
                        'حدد الجمهور المستهدف:',
                        '  - الموقع الجغرافي (مصر، السعودية، إلخ)',
                        '  - العمر (18-65)',
                        '  - الاهتمامات (تسويق، تجارة، إلخ)',
                        'حدد الميزانية: $10 - $100 يومياً',
                        'اختر المدة: 1 - 30 يوم',
                        'أدخل بيانات الدفع (Visa/Mastercard)',
                        'انقر "Boost" ✅'
                    ],
                    'الخطوة_4_المتابعة': [
                        'انتظر مراجعة Facebook (عادة 1-24 ساعة)',
                        'راقب الأداء من "Ad Center"',
                        'قم بالتحسين: أوقف الإعلانات الضعيفة، ضاعف الناجحة',
                        'جرّب A/B Testing (نفس الإعلان بصور/نصوص مختلفة)'
                    ]
                }
            },
            'نصائح_ذهبية': {
                'لزيادة_فرص_القبول': [
                    '✅ استخدم محتوى أصلي (صورك الخاصة)',
                    '✅ تجنب النصوص المبالغ فيها (100% مضمون، إلخ)',
                    '✅ لا تستخدم صور قبل/بعد طبية',
                    '✅ تجنب المحتوى الحساس (سياسة، دين)',
                    '✅ صفحة نشطة > صفحة جديدة'
                ],
                'لتقليل_التكلفة': [
                    '💰 ابدأ بميزانية صغيرة (10$ يومياً)',
                    '💰 استهدف جمهور ضيق (مدينة واحدة بدلاً من دولة)',
                    '💰 شغّل الإعلانات في أوقات الذروة فقط',
                    '💰 استخدم Video/Reels (أرخص من الصور)',
                    '💰 اختبر 3-5 إعلانات، احتفظ بالأفضل فقط'
                ],
                'لزيادة_التحويلات': [
                    '🎯 Call-to-Action واضح (اطلب الآن، تواصل معنا)',
                    '🎯 Landing Page مباشر (WhatsApp أفضل من موقع)',
                    '🎯 عرض محدود (خصم 50% لأول 100 عميل)',
                    '🎯 Social Proof (تقييمات، عدد العملاء)',
                    '🎯 رد سريع على الرسائل (خلال 5 دقائق)'
                ]
            },
            'الأخطاء_الشائعة': [
                '❌ استهداف واسع جداً (كل مصر بدلاً من القاهرة)',
                '❌ محتوى ضعيف (صور سيئة، نصوص غير واضحة)',
                '❌ عدم المتابعة (ترك الإعلان يعمل بدون تحسين)',
                '❌ ميزانية كبيرة من البداية (ابدأ صغيراً)',
                '❌ عدم اختبار A/B (إعلان واحد فقط)'
            ],
            'متى_تحتاج_Business_Manager': [
                'إذا كانت ميزانيتك أكثر من 100$ يومياً',
                'إذا أردت إعلانات متقدمة (Pixel, Retargeting)',
                'إذا كان لديك فريق تسويق',
                'إذا أردت إعلانات على Instagram + Facebook + Messenger معاً'
            ],
            'الخلاصة': '✨ ابدأ بـ Boosted Posts البسيطة، وعندما تنمو (100$+ يومياً) انتقل لـ Business Manager'
        }


# مثال استخدام
if __name__ == '__main__':
    service = FacebookBoostService()
    guide = service.get_setup_guide()
    print("=" * 60)
    print(guide['العنوان'])
    print("=" * 60)
