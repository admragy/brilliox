import os
import requests
import json
from datetime import datetime
from database import supabase

class WhatsAppManager:
    def __init__(self):
        self.twilio_sid = os.environ.get("TWILIO_SID")
        self.twilio_token = os.environ.get("TWILIO_TOKEN")
        self.twilio_whatsapp_number = os.environ.get("TWILIO_WHATSAPP_NUMBER")
    
    def send_message(self, to_number, message):
        """إرسال رسالة واتساب عبر Twilio"""
        if not all([self.twilio_sid, self.twilio_token, self.twilio_whatsapp_number]):
            print("❌ Twilio credentials not configured")
            return {"success": False, "error": "Twilio not configured"}
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        
        data = {
            'From': f'whatsapp:{self.twilio_whatsapp_number}',
            'To': f'whatsapp:{to_number}',
            'Body': message
        }
        
        try:
            response = requests.post(
                url,
                data=data,
                auth=(self.twilio_sid, self.twilio_token),
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ WhatsApp message sent to {to_number}")
                return {
                    "success": True,
                    "message_sid": result.get('sid'),
                    "status": result.get('status')
                }
            else:
                error_msg = f"Twilio API error: {response.status_code}"
                print(f"❌ {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Failed to send WhatsApp: {str(e)}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def create_campaign(self, campaign_name, message_template, target_quality, created_by):
        """إنشاء حملة واتساب جديدة"""
        try:
            campaign_data = {
                "campaign_name": campaign_name,
                "message_template": message_template,
                "target_quality": target_quality,
                "created_by": created_by,
                "status": "active"
            }
            
            result = supabase.table("whatsapp_campaigns").insert(campaign_data).execute()
            
            if result.data:
                print(f"✅ Campaign created: {campaign_name}")
                return {"success": True, "campaign_id": result.data[0]['id']}
            else:
                return {"success": False, "error": "Failed to create campaign"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_campaign(self, campaign_id):
        """تنفيذ حملة واتساب"""
        try:
            # جلب بيانات الحملة
            campaign_result = supabase.table("whatsapp_campaigns").select("*").eq("id", campaign_id).execute()
            
            if not campaign_result.data:
                return {"success": False, "error": "Campaign not found"}
            
            campaign = campaign_result.data[0]
            
            # جلب العملاء المستهدفين
            leads_result = supabase.table("leads").select("phone_number, quality").in_("quality", campaign['target_quality']).execute()
            
            sent_count = 0
            failed_count = 0
            
            for lead in leads_result.data:
                phone = lead['phone_number']
                personalized_message = self.personalize_message(campaign['message_template'], lead)
                
                # إرسال الرسالة
                result = self.send_message(phone, personalized_message)
                
                # تسجيل النتيجة
                log_data = {
                    "campaign_id": campaign_id,
                    "lead_phone": phone,
                    "message_sent": personalized_message,
                    "status": "sent" if result['success'] else "failed"
                }
                
                supabase.table("campaign_logs").insert(log_data).execute()
                
                if result['success']:
                    sent_count += 1
                else:
                    failed_count += 1
                
                # وقفة بين الرسائل
                import time
                time.sleep(2)
            
            # تحديث إحصائيات الحملة
            supabase.table("whatsapp_campaigns").update({
                "sent_count": sent_count,
                "delivered_count": sent_count
            }).eq("id", campaign_id).execute()
            
            return {
                "success": True,
                "sent": sent_count,
                "failed": failed_count,
                "total": sent_count + failed_count
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def personalize_message(self, template, lead_data):
        """تخصيص الرسالة بناءً على بيانات العميل"""
        personalized = template
        
        # استبدال العناصر النائبة
        replacements = {
            '{phone}': lead_data.get('phone_number', ''),
            '{quality}': lead_data.get('quality', ''),
            '{date}': datetime.now().strftime('%Y-%m-%d')
        }
        
        for placeholder, value in replacements.items():
            personalized = personalized.replace(placeholder, value)
        
        return personalized
    
    def get_campaign_stats(self, campaign_id):
        """الحصول على إحصائيات الحملة"""
        try:
            logs_result = supabase.table("campaign_logs").select("*").eq("campaign_id", campaign_id).execute()
            
            total = len(logs_result.data)
            sent = len([log for log in logs_result.data if log['status'] == 'sent'])
            failed = len([log for log in logs_result.data if log['status'] == 'failed'])
            responded = len([log for log in logs_result.data if log.get('response_text')])
            
            return {
                "total": total,
                "sent": sent,
                "failed": failed,
                "responded": responded,
                "response_rate": round((responded / total * 100), 2) if total > 0 else 0
            }
            
        except Exception as e:
            return {"error": str(e)}

# نماذج رسائل واتساب جاهزة
MESSAGE_TEMPLATES = {
    "عقارات": "مرحباً، شكراً لاهتمامك بالعقارات. نحن متخصصون في تقديم أفضل العروض المناسبة لاحتياجاتك. هل يمكننا مساعدتك في العثور على ما تبحث عنه؟",
    "سيارات": "أهلاً بك، نرى أنك مهتم بالسيارات. لدينا مجموعة مميزة من السيارات قد تناسب ذوقك. هل ترغب في معرفة المزيد؟",
    "عام": "مرحباً، شكراً لاهتمامك. نحن هنا لمساعدتك في العثور على أفضل الحلول. لا تتردد في التواصل معنا لأي استفسار.",
    "متابعة": "مرحباً مرة أخرى، هل لا زلت مهتماً بالعروض؟ نحن جاهزون لمساعدتك في أي وقت."
}
