import os
from supabase import create_client, Client

class Database:
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.client = None
        self.connect()
    
    def connect(self):
        """الاتصال بقاعدة بيانات Supabase"""
        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
            print("✅ Connected to Supabase successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            self.client = None
            return False
    
    def test_connection(self):
        """اختبار اتصال قاعدة البيانات"""
        if not self.client:
            return False
        
        try:
            result = self.client.table("users").select("count", count="exact").execute()
            return True
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False
    
    def get_leads(self, user_id: str, filters: dict = None, limit: int = 100, offset: int = 0):
        """جلب العملاء المحتملين مع إمكانية التصفية"""
        if not self.client:
            return []
        
        try:
            query = self.client.table("leads").select("*").eq("user_id", user_id)
            
            if filters:
                if filters.get('quality'):
                    query = query.eq("quality", filters['quality'])
                if filters.get('status'):
                    query = query.eq("status", filters['status'])
                if filters.get('source'):
                    query = query.ilike("source", f"%{filters['source']}%")
                if filters.get('date_from'):
                    query = query.gte("created_at", filters['date_from'])
                if filters.get('date_to'):
                    query = query.lte("created_at", filters['date_to'])
            
            result = query.order("created_at", desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            print(f"❌ Error fetching leads: {e}")
            return []
    
    def get_user_stats(self, user_id: str):
        """الحصول على إحصائيات المستخدم"""
        if not self.client:
            return {}
        
        try:
            # إجمالي العملاء
            total_result = self.client.table("leads").select("id", count="exact").eq("user_id", user_id).execute()
            
            # العملاء حسب الجودة
            quality_result = self.client.table("leads").select("quality").eq("user_id", user_id).execute()
            
            # سجلات البحث
            hunt_result = self.client.table("hunt_logs").select("results_count").eq("user_id", user_id).execute()
            
            # حساب الإحصائيات
            total_leads = total_result.count or 0
            quality_stats = {}
            for lead in quality_result.data:
                quality = lead.get('quality', 'غير معروف')
                quality_stats[quality] = quality_stats.get(quality, 0) + 1
            
            total_searches = len(hunt_result.data)
            total_found = sum(log['results_count'] for log in hunt_result.data if log.get('results_count'))
            
            return {
                'total_leads': total_leads,
                'quality_stats': quality_stats,
                'total_searches': total_searches,
                'total_found': total_found,
                'success_rate': round((total_found / (total_searches * 20)) * 100, 2) if total_searches > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error fetching user stats: {e}")
            return {}
    
    def update_lead_status(self, lead_id: str, status: str, notes: str = None):
        """تحديث حالة العميل"""
        if not self.client:
            return False
        
        try:
            update_data = {"status": status}
            if notes:
                update_data["notes"] = notes
            
            result = self.client.table("leads").update(update_data).eq("id", lead_id).execute()
            return bool(result.data)
        except Exception as e:
            print(f"❌ Error updating lead status: {e}")
            return False
    
    def add_hunt_log(self, log_data: dict):
        """إضافة سجل بحث جديد"""
        if not self.client:
            return False
        
        try:
            result = self.client.table("hunt_logs").insert(log_data).execute()
            return bool(result.data)
        except Exception as e:
            print(f"❌ Error adding hunt log: {e}")
            return False

# إنشاء instance عام للاستخدام
supabase_client = Database()
